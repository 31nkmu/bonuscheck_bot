from asgiref.sync import sync_to_async

from applications.users.models import Code, Users
from config.settings import BACKEND_LOGGER as log


class UserInterfaceMixin:
    @staticmethod
    def __get_user(tg_id: str):
        user = Users.objects.select_related().get(tg_id=tg_id)
        return user

    def get_all_admin_tg_id(self):
        try:
            admins = Users.objects.filter(is_admin=True).all()
            return [admin.tg_id for admin in admins]
        except Exception as err:
            return []

    @staticmethod
    @sync_to_async
    def create_user(code: Code, tg_id, username):
        try:
            user_obj = Users.objects.filter(tg_id=tg_id).first()
            if user_obj:
                user_obj.code = code
                user_obj.save()
                return True
            Users.objects.create(
                code=code,
                tg_id=tg_id,
                username=username
            )
            return True
        except Exception as err:
            log.warning(err)
            return False

    @sync_to_async
    def check_code_user(self, user_obj):
        try:
            if user_obj.code is None:
                return False
            return user_obj.code.is_active
        except Exception as err:
            log.warning(err)

    @sync_to_async
    def get_user(self, tg_id):
        try:
            return self.__get_user(tg_id)
        except Exception as err:
            log.warning(err)
            return False

    @sync_to_async
    def get_user_with_code(self, tg_id):
        try:
            user_obj = self.__get_user(tg_id)
            is_active = user_obj.code.is_active
            return is_active
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
            code_obj = self.__get_code(code)
            is_active_code = code_obj.is_active
            if code_obj and is_active_code:
                return code_obj
            return False
        except Exception as err:
            log.warning(err)
            return False

    @sync_to_async
    def get_keycode(self, user_obj):
        try:
            return user_obj.code.keycode
        except Exception as err:
            log.error(err)
            return False
