import io
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
from loguru import logger
from loguru._logger import Logger
from pyzbar import pyzbar

from bot.keyboards.keyboards import KeyboardManager
from interface.backend import BackendInterface
from interface.proverkacheka import ProverkachekaInterface


class FSM(StatesGroup):
    enter_code = State()
    send_check = State()


class BotHandler:
    __slots__ = "dp", "bot", "log", "bi", "kb", "pchi"

    def __init__(self,
                 dp: Dispatcher,
                 log: Logger,
                 bi: BackendInterface,
                 kb: KeyboardManager,
                 pchi: ProverkachekaInterface):
        self.dp = dp
        self.bot = dp.bot
        self.log = log
        self.bi = bi
        self.kb = kb
        self.pchi = pchi

    def register_user_handlers(self):
        # Логика проверки кода в таблице
        self.dp.register_message_handler(self.start, commands=['start'], state='*')
        self.dp.register_message_handler(self.enter_code, state=FSM.enter_code)
        self.dp.register_message_handler(self.send_check, state=FSM.send_check, content_types=types.ContentTypes.PHOTO)

        self.dp.register_callback_query_handler(self.download_check, Text('download_check'), state='*')
        self.dp.register_callback_query_handler(self.personal_area, Text('personal_area'), state='*')
        self.dp.register_callback_query_handler(self.check_statistic, Text('check_statistic'), state='*')

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

    async def send_check(self, message: types.Message, state: FSMContext):
        """
        Срабатывает после того как пользователь отправит фотографию с чеком
        """
        try:
            await state.finish()
            file_id = message.photo[-1].file_id
            qr = await self.get_qr_code_by_file_id(file_id)
            if qr:
                # TODO: Отправлять этот qr на проверку
                qr_data = await self.pchi.send_raw_data(qr)

                await self.bot.send_message(chat_id=message.chat.id, text=qr)
            else:
                find_not_qr_text = 'Не могу найти на этой фотографии qr code\nПопробуйте еще раз'
                await FSM.send_check.set()
                await self.bot.send_message(chat_id=message.chat.id, text=find_not_qr_text)
        except Exception as err:
            logging.exception(err)
            await self.bot.send_message(chat_id=message.chat.id,
                                        text="❌Ошибка при проверке чека.")

    async def download_check(self, cb: CallbackQuery, state: FSMContext):
        """
        При нажатии на 'Загрузка чеков'
        """
        await state.finish()
        await FSM.send_check.set()
        await cb.bot.send_message(chat_id=cb.message.chat.id, text='Отправьте фотографию с чеком')

    async def personal_area(self, cb: CallbackQuery, state: FSMContext):
        """
        Появляется при нажатии на 'Личный кабинет'
        """
        await state.finish()
        personal_area_kb = await self.kb.get_personal_area_kb()
        await cb.bot.send_message(chat_id=cb.message.chat.id, reply_markup=personal_area_kb, text='Ваш выбор')

    async def check_statistic(self, cb: CallbackQuery, state: FSMContext):
        """
        Выводит статистику чеков
        """
        await state.finish()
        user = await self.bi.get_user(tg_id=cb.from_user.id)
        check_amount = await self.bi.get_all_check_amount(user)
        await cb.bot.send_message(chat_id=cb.message.chat.id, text=check_amount)

    async def get_qr_code_by_file_id(self, file_id):
        """
        Находит qr code по фотографии
        """
        # Загрузка изображения по file_id
        image_bytes = await self.bot.download_file_by_id(file_id)
        image = Image.open(io.BytesIO(image_bytes.read()))
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Поиск QR-кодов
        barcodes = pyzbar.decode(gray)

        # Обработка найденных QR-кодов
        if len(barcodes) > 0:
            for barcode in barcodes:
                # Извлечение данных из QR-кода
                data = barcode.data.decode("utf-8")
                return data
