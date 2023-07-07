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
        # kb.add(types.InlineKeyboardButton(text='Статистика чеков', callback_data='check_statistic'))
        kb.add(types.InlineKeyboardButton(text='Назад', callback_data='get_back'))
        return kb

    @staticmethod
    async def get_back() -> types.InlineKeyboardMarkup:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Назад', callback_data='get_back'))
        return kb

    @staticmethod
    async def get_admin_kb() -> types.InlineKeyboardMarkup:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Статистика чеков', callback_data='check_statistic'))
        kb.add(types.InlineKeyboardButton(text='Обработка чеков', callback_data='check_treatment'))
        kb.add(types.InlineKeyboardButton(text='Назад', callback_data='get_back'))
        return kb

    @staticmethod
    async def get_accepted_kb(check) -> types.InlineKeyboardMarkup:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Начислить', callback_data='accrue'))
        kb.add(types.InlineKeyboardButton(text='Отклонить', callback_data='reject'))
        kb.add(types.InlineKeyboardButton(text='Назад', callback_data='get_back_admin'))
        return kb
