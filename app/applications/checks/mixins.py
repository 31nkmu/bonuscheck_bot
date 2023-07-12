from asgiref.sync import sync_to_async
from django.db import transaction

from applications.checks.models import Check, Product, Bonus, CodeWord, Gtin
from applications.users.models import Users
from config.settings import BACKEND_LOGGER as log


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
                res_quantity = 0
                for product in product_list:
                    product_obj_list.append(
                        Product(check_field=check_obj, price=product['price'], name=product['name'],
                                quantity=product['quantity'])
                    )
                    res_quantity += product['quantity']

                # TODO: узнать сколько баланса начислить
                bonus = Bonus.objects.all().first()
                if not bonus:
                    bonus = Bonus.objects.create()
                owner.bonus_balance += bonus.balance * res_quantity
                check_obj.bonus_balance = bonus.balance * res_quantity
                owner.save()
                check_obj.save()
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
