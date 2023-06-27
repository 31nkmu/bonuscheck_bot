from typing import Optional
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from loguru._logger import Logger


class BotHandler:
    __slots__ = "dp", "bot", "log"

    def __init__(self,
                 dp: Dispatcher,
                 log: Logger):
        self.dp = dp
        self.bot = dp.bot
        self.log = log

    def register_user_handlers(self):
        # Логика проверки почты в таблице
        self.dp.register_message_handler(self.start, commands=['start'], state='*')

    async def edit_page(self, message: Message,
                        new_text: str,
                        new_markup: Optional[types.InlineKeyboardMarkup] = None,
                        previous_markup_needed: bool = False):
        await message.edit_text(new_text)
        if not previous_markup_needed:
            await message.edit_reply_markup(new_markup)

    async def start(self, message: Message, state: FSMContext):
        await self.bot.send_message(message.chat.id, 'hello')
