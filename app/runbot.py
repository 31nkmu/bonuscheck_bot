import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from interface.proverkacheka import ProverkachekaInterface
from interface.backend import BackendInterface
from config.settings import TELEGRAM_API_TOKEN, TELEGRAM_LOGGER
from aiogram import Bot, Dispatcher
from bot.services import BotService
from bot.keyboards.keyboards import KeyboardManager
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bi = BackendInterface()
kb = KeyboardManager()
pchi = ProverkachekaInterface()

if __name__ == "__main__":
    bot = Bot(token=TELEGRAM_API_TOKEN)

    storage = MemoryStorage()

    dp = Dispatcher(bot, storage=storage)

    service = BotService(dp, TELEGRAM_LOGGER, bi, kb, pchi)
    service.start()
