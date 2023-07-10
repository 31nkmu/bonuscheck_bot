from aiogram import executor, Dispatcher, types

from bot.handlers.user_handler import BotHandler
from bot.keyboards.keyboards import KeyboardManager
from config.settings import TELEGRAM_LOGGER as log

from loguru._logger import Logger

from interface.backend import BackendInterface
from interface.proverkacheka import ProverkachekaInterface


class BotService:
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

    @log.catch
    def start(self):
        """Запуск бот сервиса. Регистрирует обработчики и запускает поллинг."""
        user_handler = BotHandler(self.dp, self.log, self.bi, self.kb, self.pchi)

        start_command = types.BotCommand(command="start", description="Start the bot")
        self.dp.bot.set_my_commands([start_command])

        # Работа с ролями тут. Этот фильтр ставит роли!!!
        # self.dp.middleware.setup(RoleMiddleware())

        # Тут проверяем если роль юзера Role.USER
        # self.dp.filters_factory.bind(RoleFilter)

        # Он проверяет просто если роль у юзера Role.admin - то мы исполняем этот метод
        # self.dp.filters_factory.bind(AdminFilter)
        user_handler.register_user_handlers()
        self.log.info("Запуск бот сервиса")
        executor.start_polling(self.dp, skip_updates=True)
