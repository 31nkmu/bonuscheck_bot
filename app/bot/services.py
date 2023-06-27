from aiogram import executor, Dispatcher

from bot.handlers.user_handler import BotHandler
from config.settings import TELEGRAM_LOGGER as log

from loguru._logger import Logger


class BotService:
    __slots__ = "dp", "bot", "log"

    def __init__(self,
                 dp: Dispatcher,
                 log: Logger):
        self.dp = dp
        self.bot = dp.bot
        self.log = log

    @log.catch
    def start(self):
        """Запуск бот сервиса. Регистрирует обработчики и запускает поллинг."""
        user_handler = BotHandler(self.dp, self.log)

        # Работа с ролями тут. Этот фильтр ставит роли!!!
        # self.dp.middleware.setup(RoleMiddleware())

        # Тут проверяем если роль юзера Role.USER
        # self.dp.filters_factory.bind(RoleFilter)

        # Он проверяет просто если роль у юзера Role.admin - то мы исполняем этот метод
        # self.dp.filters_factory.bind(AdminFilter)
        user_handler.register_user_handlers()
        self.log.info("Запуск бот сервиса")
        executor.start_polling(self.dp, skip_updates=True)
