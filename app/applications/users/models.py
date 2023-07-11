from enum import Enum

from django.core.exceptions import ValidationError
from django.db import models


class Users(models.Model):
    """
    Пользователи
    """
    code = models.ForeignKey("Code", on_delete=models.CASCADE, related_name="users")

    is_banned = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now=True)
    tg_id = models.CharField(unique=True, max_length=120)
    bonus_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.tg_id


class Code(models.Model):
    """
    Коды
    """
    keycode = models.CharField(max_length=120, verbose_name='Код')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def __str__(self):
        return self.keycode

    class Meta:
        verbose_name = "Код"
        verbose_name_plural = "Коды"


class Check(models.Model):
    """
    Чеки
    """
    owner = models.ForeignKey("Users", on_delete=models.CASCADE, related_name="checks", verbose_name='Владелец')

    qr_data = models.CharField(max_length=120, unique=True, verbose_name='qr код')
    # Обработан
    is_processed = models.BooleanField(default=False, verbose_name='Обработан')
    # Принят
    is_accepted = models.BooleanField(default=True, verbose_name='Принят')
    # Отклонен
    is_reject = models.BooleanField(default=False, verbose_name='Отклонен')
    bonus_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Бонусный баланс')

    def __str__(self):
        return self.qr_data

    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"


class Product(models.Model):
    """
    Продукты этих чеков
    """
    check_field = models.ForeignKey(Check, on_delete=models.CASCADE, related_name='products', verbose_name='Чек')

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    name = models.TextField(verbose_name='Название')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class Output(models.Model):
    """
    Заявка на вывод
    """
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]

    owner = models.ForeignKey("Users", on_delete=models.CASCADE, related_name="outputs", verbose_name='Владелец')

    amount = models.PositiveIntegerField(default=1, verbose_name='Количество')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачено')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', verbose_name='Статус')

    def __str__(self):
        return str(self.amount)

    class Meta:
        verbose_name = "Вывод"
        verbose_name_plural = "Выводы"


class CodeWord(models.Model):
    word = models.CharField(max_length=120, unique=True, verbose_name='Слово')

    def __str__(self):
        return self.word

    def save(self, *args, **kwargs):
        self.word = str(self.word).lower()  # Преобразование в нижний регистр
        super(CodeWord, self).save(*args, **kwargs)

    def clean(self):
        # Проверка уникальности с учетом разного регистра
        existing_word = CodeWord.objects.filter(word__iexact=self.word).exclude(pk=self.pk).first()
        if existing_word:
            raise ValidationError('Такое слово уже существует.')

    class Meta:
        verbose_name = "Проверочное слово"
        verbose_name_plural = "Проверочные слова"


class Gtin(models.Model):
    gtin = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.gtin

    class Meta:
        verbose_name = "Gtin"
        verbose_name_plural = "Gtin"


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    NOT_ACTIVE = "not_active"
    BAN = "ban"
