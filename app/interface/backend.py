from asgiref.sync import sync_to_async
from django.db import transaction

from applications.users.models import Code, Users, Check, CodeWord
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

    @sync_to_async
    def give_bonus_write_qr(self, qr_raw, chat_id):
        """
        Записывает qr в базу данных и начисляет бонусы
        """
        try:
            with transaction.atomic():
                owner = Users.objects.get(tg_id=chat_id)
                Check.objects.create(owner=owner, qr_data=qr_raw)
                # TODO: узнать сколько баланса начислить
                owner.bonus_balance = 100
                owner.save()
                return True
        except Exception as err:
            log.error(err)
            return False

    @sync_to_async
    def is_have_qr(self, qr_raw):
        try:
            if Check.objects.filter(qr_data=qr_raw).exists():
                return True
            return False
        except Exception as err:
            log.error(err)
            return False


class OutputInterfaceMixin:
    pass


class CodeWordMixin:
    @sync_to_async
    def get_codeword_in_text(self, text):
        try:
            codewords = [codeword.word for codeword in CodeWord.objects.all()]
            if any(codeword in text for codeword in codewords):
                return True
            return False
        except Exception as err:
            log.error(err)
            return False


class BackendInterface(UserInterfaceMixin, CodeInterfaceMixin, CheckInterfaceMixin, OutputInterfaceMixin,
                       CodeWordMixin):
    pass
