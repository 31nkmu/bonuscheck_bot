import functools
import io
import os
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
import logging
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async
from loguru import logger
from loguru._logger import Logger
from pyzbar import pyzbar
from django.db import connection
import pandas as pd

from applications.users.models import UserRole
from bot.keyboards.keyboards import KeyboardManager
from interface.backend import BackendInterface
from interface.proverkacheka import ProverkachekaInterface


class FSM(StatesGroup):
    enter_code = State()
    send_check = State()
    admin_menu = State()
    give_bonus = State()


class BotHandler:
    __slots__ = "dp", "bot", "log", "bi", "kb", "pchi", "check_iter", "accrue_handler"

    def __init__(self,
                 dp: Dispatcher,
                 log: Logger,
                 bi: BackendInterface,
                 kb: KeyboardManager,
                 pchi: ProverkachekaInterface,
                 check_iter=None,
                 accrue_handler=None):
        self.dp = dp
        self.bot = dp.bot
        self.log = log
        self.bi = bi
        self.kb = kb
        self.pchi = pchi
        self.check_iter = check_iter
        self.accrue_handler = accrue_handler

    def register_user_handlers(self):
        # Логика проверки кода в таблице
        self.dp.register_message_handler(self.start, commands=['start'], state='*',
                                         role=[UserRole.USER, UserRole.ADMIN])
        self.dp.register_message_handler(self.admin, commands=['admin'], state='*', role=UserRole.ADMIN)
        self.dp.register_message_handler(self.enter_code, state=FSM.enter_code, role=[UserRole.USER, UserRole.ADMIN])

        self.dp.register_message_handler(self.admin_menu, state=FSM.admin_menu, content_types=types.ContentTypes.ANY,
                                         role=UserRole.ADMIN)
        self.dp.register_message_handler(self.send_check, state=FSM.send_check, content_types=types.ContentTypes.PHOTO,
                                         role=[UserRole.USER, UserRole.ADMIN])

        self.dp.register_callback_query_handler(self.download_check, Text('download_check'), state='*',
                                                role=[UserRole.USER, UserRole.ADMIN])
        self.dp.register_callback_query_handler(self.personal_area, Text('personal_area'), state='*',
                                                role=[UserRole.USER, UserRole.ADMIN])
        self.dp.register_callback_query_handler(self.check_statistic, Text('check_statistic'), state='*',
                                                role=UserRole.ADMIN)
        self.dp.register_callback_query_handler(self.check_treatment, Text('check_treatment'), state='*',
                                                role=UserRole.ADMIN)
        self.dp.register_callback_query_handler(self.get_back, Text('get_back'), state='*',
                                                role=[UserRole.USER, UserRole.ADMIN])
        self.dp.register_callback_query_handler(self.accrue, Text('accrue'), state='*', role=UserRole.ADMIN)
        self.dp.register_callback_query_handler(self.reject, Text('reject'), state='*', role=UserRole.ADMIN)
        self.dp.register_callback_query_handler(self.get_back_admin, Text('get_back_admin'), state='*',
                                                role=UserRole.ADMIN)

    @staticmethod
    async def edit_page(message: Message,
                        new_text: str,
                        new_markup: Optional[types.InlineKeyboardMarkup] = None,
                        previous_markup_needed: bool = False):
        await message.edit_text(new_text)
        if not previous_markup_needed:
            await message.edit_reply_markup(new_markup)

    async def start(self, message: Message, state: FSMContext):
        await state.finish()
        text = "👋Здравствуйте!"
        await self.bot.send_photo(chat_id=message.chat.id, caption=text,
                                  photo=types.InputFile('app/bot/media/test2.jpg'))
        user = await self.bi.get_user(tg_id=message.from_user.id)
        if user:
            success_code_kb = await self.kb.get_paid_kb()
            success_code_text = "Код успешно найден!"
            await self.bot.send_photo(chat_id=message.chat.id,
                                      photo=types.InputFile('app/bot/media/test2.jpg'),
                                      caption=success_code_text,
                                      reply_markup=success_code_kb)
            return
        await FSM.enter_code.set()
        text_email_code = '👇Введите код'
        await self.bot.send_message(chat_id=message.chat.id, text=text_email_code)

    async def enter_code(self, message: types.Message, state: FSMContext):
        """
        Проверяет введенный пользователем код
        """
        message_to_delete = (await message.answer('⌛Проверяем код. . .'))['message_id']
        try:
            code = await self.bi.get_code(message.text)
            if code:
                await state.finish()
                await self.bi.create_user(code=code, tg_id=message.from_user.id)
                success_code_kb = await self.kb.get_paid_kb()
                success_code_text = "Код успешно найден! \n Вы были зарегистрированы"
                await self.bot.send_photo(chat_id=message.chat.id,
                                          photo=types.InputFile('app/bot/media/test2.jpg'),
                                          caption=success_code_text,
                                          reply_markup=success_code_kb)
            else:
                await self.bot.send_message(chat_id=message.chat.id,
                                            text="❌Код не найден, проверьте код или попробуйте ещё раз.")
                await FSM.enter_code.set()
                text_email_enter = '👇Введите код'
                await message.bot.send_message(message.chat.id, text_email_enter)
        except Exception as err:
            await self.dp.bot.send_message(chat_id=message.chat.id,
                                           text="❌Ошибка при проверке кода.")
            logging.exception(err)
        finally:
            await self.bot.delete_message(chat_id=message.chat.id, message_id=message_to_delete)

    async def admin(self, message: Message, state: FSMContext):
        await state.finish()
        admin_text = 'Вы попали в меню администратора'
        kb = await self.kb.get_admin_kb()
        await self.bot.send_message(chat_id=message.chat.id, text=admin_text, reply_markup=kb)

    async def admin_menu(self, message: Message, state: FSMContext):
        await state.finish()
        kb = await self.kb.get_admin_kb()
        await self.bot.send_message(reply_markup=kb, chat_id=message.chat.id,
                                    text='Ваш выбор')

    async def send_check(self, message: types.Message, state: FSMContext):
        """
        Срабатывает после того как пользователь отправит фотографию с чеком
        """
        message_to_delete = (await message.answer('⌛Проверяем фотографию. . .'))['message_id']
        kb = await self.kb.get_back()
        try:
            await state.finish()
            photo = message.photo[-1]
            photo_binary = await photo.download(io.BytesIO())
            qr_raw, operation_type, product_list, code = await self.pchi.get_qr_by_photo(photo_binary)
            if code == 1:
                # проверяет есть ли кодовое слово
                have_codeword_products = await self.bi.get_have_codeword_products(product_list)
                is_have_qr = await self.bi.is_have_qr(qr_raw)
                if is_have_qr is True:
                    have_qr_text = 'qr code уже был использован\nПопробуйте еще раз'
                    await FSM.send_check.set()
                    await self.bot.send_message(chat_id=message.chat.id, text=have_qr_text, reply_markup=kb)
                    return
                if operation_type != 1 or len(have_codeword_products) == 0:
                    await self.bi.write_bad_qr_to_db(qr_raw=qr_raw, chat_id=message.from_user.id,
                                                     product_list=product_list)
                    find_not_qr_text = 'В qr code не найдены нужные ключевые слова\nПопробуйте еще раз'
                    await FSM.send_check.set()
                    await self.bot.send_message(chat_id=message.chat.id, text=find_not_qr_text, reply_markup=kb)
                else:
                    message_to_delete_bonus = (await message.answer('⌛Начисляем бонусы. . .'))['message_id']
                    is_gave_bonus = await self.bi.give_bonus_write_qr(qr_raw=qr_raw, chat_id=message.from_user.id,
                                                                      product_list=product_list)
                    gave_bonus_text = 'Бонусы успешно начислены,\nМожете отправить следующий чек'
                    if is_gave_bonus is True:
                        await FSM.send_check.set()
                        await self.bot.send_message(chat_id=message.chat.id, text=gave_bonus_text, reply_markup=kb)
                    else:
                        find_not_qr_text = 'Что-то пошло не так\nПопробуйте еще раз'
                        await FSM.send_check.set()
                        await self.bot.send_message(chat_id=message.chat.id, text=find_not_qr_text, reply_markup=kb)
                    await self.bot.delete_message(chat_id=message.chat.id, message_id=message_to_delete_bonus)
            else:
                find_not_qr_text = 'Не могу найти на этой фотографии qr code\nПопробуйте еще раз'
                await FSM.send_check.set()
                await self.bot.send_message(chat_id=message.chat.id, text=find_not_qr_text, reply_markup=kb)
        except Exception as err:
            logging.exception(err)
            await FSM.send_check.set()
            await self.bot.send_message(chat_id=message.chat.id,
                                        text="❌Ошибка при проверке чека.\nПопробуйте еще раз", reply_markup=kb)
        finally:
            await self.bot.delete_message(chat_id=message.chat.id, message_id=message_to_delete)

    async def download_check(self, cb: CallbackQuery, state: FSMContext):
        """
        При нажатии на 'Загрузка чеков'
        """
        await state.finish()
        await FSM.send_check.set()
        back_kb = await self.kb.get_back()
        await cb.bot.send_message(chat_id=cb.message.chat.id, text='Отправьте фотографию с чеком', reply_markup=back_kb)

    async def personal_area(self, cb: CallbackQuery, state: FSMContext):
        """
        Появляется при нажатии на 'Личный кабинет'
        """
        await state.finish()
        personal_area_kb = await self.kb.get_personal_area_kb()
        user_obj = await self.bi.get_user(tg_id=cb.from_user.id)
        processed_count = await self.bi.get_processed_count(user_obj)
        accepted_count = await self.bi.get_accepted_count(user_obj)
        reject_count = await self.bi.get_reject_count(user_obj)
        personal_data_text = f'Баланс {user_obj.bonus_balance}\n' \
                             f'Код {user_obj.code.keycode}\n' \
                             f'Обработанные  {processed_count}\n' \
                             f'Принятые {accepted_count}\n' \
                             f'Отклоненные {reject_count}'
        await cb.bot.send_message(chat_id=cb.message.chat.id, reply_markup=personal_area_kb, text=personal_data_text)

    async def check_statistic(self, cb: CallbackQuery, state: FSMContext):
        """
        Выводит статистику чеков
        """
        await state.finish()
        await self.export_table_to_excel()
        await self.send_excel_file(cb.message.chat.id)
        await self.admin_menu(cb.message, state)

    async def check_treatment(self, cb: CallbackQuery, state: FSMContext):
        """
        Обработка чеков`
        """
        await state.finish()
        accepted_check_list = await self.bi.get_all_accepted_qr()
        self.check_iter = iter(accepted_check_list)
        await self.process_next_check(cb)

    async def process_next_check(self, cb: CallbackQuery):
        """
        Получение следующего чека
        """
        try:
            next_check = next(self.check_iter)
            kb = await self.kb.get_accepted_kb(next_check)
            # список продуктов чека
            res = await self.bi.get_products_text(next_check)

            await cb.message.answer(f'{res}', reply_markup=kb)
        except StopIteration:
            kb = await self.kb.get_admin_kb()
            await self.bot.send_message(chat_id=cb.message.chat.id, text='Все чеки обработаны', reply_markup=kb)

    async def get_back(self, cb: CallbackQuery, state: FSMContext):
        await state.finish()
        kb = await self.kb.get_paid_kb()
        await cb.message.edit_reply_markup(reply_markup=kb)

    async def get_back_admin(self, cb: CallbackQuery, state: FSMContext):
        await state.finish()
        kb = await self.kb.get_admin_kb()
        await cb.message.edit_reply_markup(reply_markup=kb)

    @sync_to_async
    def export_table_to_excel(self):
        # Получить данные из базы данных
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    uc.keycode as "code", uu.tg_id, uu.bonus_balance as "balance", 
                    ch_processed.qr_data as "qr code", p.name as "product name", p.price, p.quantity
                FROM
                    users_code uc
                JOIN
                    users_users uu ON uc.id = uu.code_id
                LEFT OUTER JOIN
                    users_check ch_processed ON uu.id = ch_processed.owner_id AND ch_processed.is_processed = true
                JOIN
                    users_product p ON ch_processed.id = p.check_field_id
            """)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

        # Создать DataFrame из данных
        df = pd.DataFrame(rows, columns=column_names)
        # Сохранить DataFrame в файл Excel
        df.to_excel('Обработанные.xlsx', index=False)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    uc.keycode as "code", uu.tg_id, uu.bonus_balance as "balance", 
                    ch_processed.qr_data as "qr code", p.name as "product name", p.price, p.quantity
                FROM
                    users_code uc
                JOIN
                    users_users uu ON uc.id = uu.code_id
                LEFT OUTER JOIN
                    users_check ch_processed ON uu.id = ch_processed.owner_id AND ch_processed.is_reject = true
                JOIN
                    users_product p ON ch_processed.id = p.check_field_id
            """)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

        # Создать DataFrame из данных
        df = pd.DataFrame(rows, columns=column_names)
        # Сохранить DataFrame в файл Excel
        df.to_excel('Отклоненные.xlsx', index=False)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    uc.keycode as "code", uu.tg_id, uu.bonus_balance as "balance", 
                    ch_processed.qr_data as "qr code", p.name as "product name", p.price, p.quantity
                FROM
                    users_code uc
                JOIN
                    users_users uu ON uc.id = uu.code_id
                LEFT OUTER JOIN
                    users_check ch_processed ON uu.id = ch_processed.owner_id AND ch_processed.is_accepted = true
                JOIN
                    users_product p ON ch_processed.id = p.check_field_id
            """)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

        # Создать DataFrame из данных
        df = pd.DataFrame(rows, columns=column_names)
        # Сохранить DataFrame в файл Excel
        df.to_excel('Принятые.xlsx', index=False)

    async def send_excel_file(self, chat_id):
        # Отправить файл Excel в Telegram
        with open('Обработанные.xlsx', 'rb') as file:
            await self.dp.bot.send_document(chat_id, file)

        with open('Отклоненные.xlsx', 'rb') as file:
            await self.dp.bot.send_document(chat_id, file)

        with open('Принятые.xlsx', 'rb') as file:
            await self.dp.bot.send_document(chat_id, file)

        # Удалить файл после отправки
        os.remove('Обработанные.xlsx')
        os.remove('Отклоненные.xlsx')
        os.remove('Принятые.xlsx')

    async def accrue(self, cb: CallbackQuery, state: FSMContext):
        """
        Отвечает за начисление обработанных чеков
        """
        await state.finish()
        accepted_check = cb.message.text
        await self.bot.send_message(chat_id=cb.message.chat.id, text=accepted_check)
        if self.accrue_handler is not None:
            self.dp.message_handlers.unregister(self.accrue_handler)
        self.accrue_handler = functools.partial(self.give_bonus, cb=cb, check=accepted_check)
        self.dp.register_message_handler(self.accrue_handler, state=FSM.give_bonus,
                                         content_types=types.ContentTypes.TEXT)
        await FSM.give_bonus.set()
        await self.bot.send_message(chat_id=cb.message.chat.id, text='Введите баланс, который хотите начислить')

    async def give_bonus(self, message: types.Message, state: FSMContext, cb: CallbackQuery, check):
        await state.finish()
        check = cb.message.text.split('\n')[-1].split(' ')[-1]
        await self.bot.send_message(chat_id=message.chat.id, text=f'даем бонус {check}, {message.text}')
        try:
            await self.bi.write_bonus_accepted_qr(qr_row=check, bonus=int(message.text))
        except ValueError:
            await self.bot.send_message(chat_id=message.chat.id, text='Нужно ввести число')
        await self.process_next_check(cb)

    async def reject(self, cb: CallbackQuery, state: FSMContext):
        await state.finish()
        accepted_check = cb.message.text.split('\n')[-1].split(' ')[-1]
        await self.bi.reject_qr(qr_row=accepted_check)
        await self.bot.send_message(chat_id=cb.message.chat.id, text=f'чек {accepted_check} был отклонен')
        await self.process_next_check(cb)
