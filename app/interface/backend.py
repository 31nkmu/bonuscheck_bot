from asgiref.sync import sync_to_async

from applications.users.models import Code, Users, Check
from config.settings import BACKEND_LOGGER as log


class UserInterfaceMixin:
    @staticmethod
    def __get_user(tg_id: str):
        user = Users.objects.get(tg_id=tg_id)
        return user

    @staticmethod
    @sync_to_async
    def create_user(code: Code, tg_id):
        try:
            Users.objects.create(
                code=code,
                tg_id=tg_id
            )
            return True
        except Exception as err:
            log.warning(err)
            return False

    @sync_to_async
    def get_user(self, tg_id):
        try:
            return self.__get_user(tg_id)
        except Exception as err:
            log.warning(err)
            return False


class CodeInterfaceMixin:
    @staticmethod
    def __get_code(code: str):
        code = Code.objects.get(keycode=code)
        return code

    @sync_to_async
    def get_code(self, code: str):
        try:
            return self.__get_code(code)
        except Exception as err:
            log.warning(err)
            return False


class CheckInterfaceMixin:
    @sync_to_async
    def get_all_check_amount(self, user):
        """
        Выводит количество чеков пользователя
        """
        try:
            return len(Check.objects.filter(owner=user))
        except Exception as err:
            log.warning(err)
            return 0


class OutputInterfaceMixin:
    pass


class BackendInterface(UserInterfaceMixin, CodeInterfaceMixin, CheckInterfaceMixin, OutputInterfaceMixin):
    pass
