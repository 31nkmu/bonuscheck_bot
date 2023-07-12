import decimal

from asgiref.sync import sync_to_async
from django.db import transaction, IntegrityError

from applications.outputs.models import Output, MinBalance
from applications.users.models import Users
from config.settings import BACKEND_LOGGER as log


class OutputInterfaceMixin:
    @sync_to_async
    def create_output(self, tg_id, balance):
        try:
            user_obj = Users.objects.get(tg_id=tg_id)
            if user_obj.outputs.filter(status='processing').first():
                raise IntegrityError
            Output.objects.create(owner=user_obj, amount=balance)
            return True
        except IntegrityError:
            return 'have_output'
        except Exception as err:
            log.error(err)
            return False

    @sync_to_async
    def get_all_processing_app(self):
        """
        Получает все заявки на вывод, находящиеся в обработке
        """
        try:
            res = Output.objects.filter(status='processing').all()
            return list(res)
        except Exception as err:
            log.error(err)
            return []

    @sync_to_async
    def get_split_data(self, output_obj):
        try:
            owner = output_obj.owner.tg_id
            amount = output_obj.amount
            balance = output_obj.owner.bonus_balance
            return owner, amount, balance
        except Exception as err:
            log.error(err)
            return None, None, None

    @sync_to_async
    def accrue_output(self, owner, amount):
        try:
            with transaction.atomic():
                user_obj = Users.objects.get(tg_id=owner)
                user_obj.bonus_balance -= decimal.Decimal(float(amount))
                output_obj = user_obj.outputs.filter(amount=amount, status='processing').first()
                output_obj.status = 'accepted'
                output_obj.save()
                user_obj.save()
                return True
        except Exception as err:
            log.error(err)
            return False

    @sync_to_async
    def reject_output(self, owner, amount):
        try:
            with transaction.atomic():
                user_obj = Users.objects.get(tg_id=owner)
                output_obj = user_obj.outputs.filter(amount=amount, status='processing').first()
                output_obj.status = 'rejected'
                output_obj.save()
                return True
        except Exception as err:
            log.error(err)
            return False

    @sync_to_async
    def del_output(self, tg_id):
        try:
            user_obj = Users.objects.get(tg_id=tg_id)
            output_obj = user_obj.outputs.filter(status='processing').first()
            if output_obj:
                output_obj.status = 'rejected'
                output_obj.save()
                return True
            return False
        except Exception as err:
            log.error(err)
            return False


class BalanceMixin:
    @sync_to_async
    def get_min_balance_to_output(self):
        try:
            min_balance = MinBalance.objects.all().first()
            if min_balance:
                return min_balance.balance
            min_balance = MinBalance.objects.create()
            return min_balance.balance
        except Exception as err:
            log.error(err)
            return 500
