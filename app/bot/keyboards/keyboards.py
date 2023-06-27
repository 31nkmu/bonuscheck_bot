from aiogram import types
from loguru import logger


class KeyboardManager:
    @staticmethod
    async def get_paid_kb() -> types.InlineKeyboardMarkup:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Загрузить чек', callback_data='download_check'))
        kb.add(types.InlineKeyboardButton(text='Личный кабинет', callback_data='personal_area'))
        return kb

    @staticmethod
    async def get_personal_area_kb() -> types.InlineKeyboardMarkup:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Статистика чеков', callback_data='check_statistic'))
        return kb
