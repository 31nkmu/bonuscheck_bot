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
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.tg_id


class Code(models.Model):
    """
    Коды
    """
    title = models.CharField(max_length=120)
    keycode = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Check(models.Model):
    """
    Чеки
    """
    owner = models.ForeignKey("Users", on_delete=models.CASCADE, related_name="checks")

    qr_data = models.CharField(max_length=120, unique=True)
    # Обработан
    is_processed = models.BooleanField(default=False)
    # Принят
    is_accepted = models.BooleanField(default=True)
    # Отклонен
    is_reject = models.BooleanField(default=False)
    bonus_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.qr_data


class Product(models.Model):
    """
    Продукты этих чеков
    """
    check_field = models.ForeignKey(Check, on_delete=models.CASCADE, related_name='products')

    price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.TextField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Output(models.Model):
    """
    Заявка на вывод
    """
    owner = models.ForeignKey("Users", on_delete=models.CASCADE, related_name="outputs")

    amount = models.PositiveIntegerField(default=1)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.amount)


class CodeWord(models.Model):
    word = models.CharField(max_length=120, unique=True)

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


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
