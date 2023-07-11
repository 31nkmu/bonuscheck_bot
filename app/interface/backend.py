import decimal

from asgiref.sync import sync_to_async
from django.db import transaction, IntegrityError

from applications.users.models import Code, Users, Check, CodeWord, Product, Output, Gtin
from config.settings import BACKEND_LOGGER as log


class ProductInterfaceMixin:
    @sync_to_async
    def get_products_text(self, check) -> str:
        """
        Получает информацию о продуктах чека
        """
        product_list = check.products.all()
        info = [f'Название: {product.name}\nКоличество {product.quantity}\nЦена {product.price}\nЧек: {check}' for
                product in product_list]
        res = ('\n\n').join(info)
        return res


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
    def give_bonus_write_qr(self, qr_raw, chat_id, product_list):
        """
        Записывает qr в базу данных и начисляет бонусы
        """
        try:
            with transaction.atomic():
                owner = Users.objects.get(tg_id=chat_id)
                check_obj = Check.objects.create(owner=owner, qr_data=qr_raw, is_processed=True, bonus_balance=100,
                                                 is_accepted=False)
                product_obj_list = []
                for product in product_list:
                    product_obj_list.append(
                        Product(check_field=check_obj, price=product['price'], name=product['name'],
                                quantity=product['quantity'])
                    )

                # TODO: узнать сколько баланса начислить
                owner.bonus_balance += 100
                owner.save()
                Product.objects.bulk_create(product_obj_list)
                return True
        except Exception as err:
            log.error(err)
            return False

    @sync_to_async
    def write_bad_qr_to_db(self, qr_raw, chat_id, product_list):
        """
        Записывает qr в базу данных без начисления бонусов
        """
        try:
            with transaction.atomic():
                owner = Users.objects.get(tg_id=chat_id)
                check_obj = Check.objects.create(owner=owner, qr_data=qr_raw)
                product_obj_list = []
                for product in product_list:
                    product_obj_list.append(
                        Product(check_field=check_obj, price=product['price'], name=product['name'],
                                quantity=product['quantity'])
                    )
                Product.objects.bulk_create(product_obj_list)
            return True
        except Exception as err:
            log.error(err)
            return False

    @sync_to_async
    def is_have_qr(self, qr_raw):
        """
        Проверяет есть ли qr code в бд
        """
        try:
            if Check.objects.filter(qr_data=qr_raw).exists():
                return True
            return False
        except Exception as err:
            log.error(err)
            return False

    @sync_to_async
    def get_processed_count(self, user_obj):
        """
        Получает количесто обработанных чеков
        """
        try:
            return user_obj.checks.filter(is_processed=True).count()
        except Exception as err:
            log.error(err)
            return 0

    @sync_to_async
    def get_accepted_count(self, user_obj):
        """
        Получает количество принятых чеков
        """
        try:
            return user_obj.checks.filter(is_accepted=True, is_processed=False).count()
        except Exception as err:
            log.error(err)
            return 0

    @sync_to_async
    def get_reject_count(self, user_obj):
        """
        Получает количество отклоненных чеков
        """
        try:
            return user_obj.checks.filter(is_reject=True).count()
        except Exception as err:
            log.error(err)
            return 0

    @sync_to_async
    def get_all_accepted_qr(self):
        """
        Получает все принятые чеки
        """
        try:
            res = Check.objects.filter(is_accepted=True).all()
            return list(res)
        except Exception as err:
            log.error(err)
            return []

    @sync_to_async
    def write_bonus_accepted_qr(self, qr_row, bonus):
        """
        Админ дает бонусы
        """
        try:
            with transaction.atomic():
                check = Check.objects.select_related().get(qr_data=qr_row)
                owner = check.owner
                owner.bonus_balance += bonus
                check.is_processed = True
                check.is_accepted = False
                check.bonus_balance = bonus
                check.save()
                owner.save(update_fields=('bonus_balance',))
        except Exception as err:
            log.error(err)

    @sync_to_async
    def reject_qr(self, qr_row):
        try:
            check = Check.objects.select_related().get(qr_data=qr_row)
            check.is_accepted = False
            check.is_reject = True
            check.save(update_fields=('is_accepted', 'is_reject'))
        except Exception as err:
            log.error(err)


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


class CodeWordMixin:
    def check_text(self, text, gtin):
        try:
            codewords = [codeword.word for codeword in CodeWord.objects.all()]
            gtins = [i.gtin for i in Gtin.objects.all()]
            if gtin in gtins:
                return True
            if any(codeword in text for codeword in codewords):
                return True
            return False
        except Exception as err:
            log.error(err)
            return False

    @sync_to_async
    def get_have_codeword_products(self, product_list) -> list:
        try:
            return [i for i in product_list if self.check_text(i['name'], i['gtin'])]
        except Exception as err:
            log.error(err)
            return []


class BackendInterface(UserInterfaceMixin, CodeInterfaceMixin, CheckInterfaceMixin, OutputInterfaceMixin,
                       CodeWordMixin, ProductInterfaceMixin):
    pass
