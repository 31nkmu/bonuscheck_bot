from typing import Optional
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
import logging
from aiogram.dispatcher.filters import Text

from loguru._logger import Logger

from bot.keyboards.keyboards import KeyboardManager
from interface.backend import BackendInterface


class FSM(StatesGroup):
    enter_code = State()


class BotHandler:
    __slots__ = "dp", "bot", "log", "bi", "kb"

    def __init__(self,
                 dp: Dispatcher,
                 log: Logger,
                 bi: BackendInterface,
                 kb: KeyboardManager):
        self.dp = dp
        self.bot = dp.bot
        self.log = log
        self.bi = bi
        self.kb = kb

    def register_user_handlers(self):
        # Логика проверки кода в таблице
        self.dp.register_message_handler(self.start, commands=['start'], state='*')
        self.dp.register_message_handler(self.enter_code, state=FSM.enter_code)

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
        except Exception as _ex:
            await self.dp.bot.send_message(chat_id=message.chat.id,
                                           text="❌Ошибка при проверке кода.")
            logging.exception(_ex)
        finally:
            await self.bot.delete_message(chat_id=message.chat.id, message_id=message_to_delete)

    @staticmethod
    async def download_check(cb: CallbackQuery, state: FSMContext):
        await state.finish()
        await cb.bot.send_message(chat_id=cb.message.chat.id, text='Загрузка чеков')

    async def personal_area(self, cb: CallbackQuery, state: FSMContext):
        await state.finish()
        personal_area_kb = await self.kb.get_personal_area_kb()
        await cb.bot.send_message(chat_id=cb.message.chat.id, reply_markup=personal_area_kb, text='Ваш выбор')

    async def check_statistic(self, cb: CallbackQuery, state: FSMContext):
        await state.finish()
        user = await self.bi.get_user(tg_id=cb.from_user.id)
        check_amount = await self.bi.get_all_check_amount(user)
        await cb.bot.send_message(chat_id=cb.message.chat.id, text=check_amount)
