from django.db import models
from django.core.exceptions import ValidationError

from applications.users.models import Users


class Check(models.Model):
    """
    Чеки
    """
    owner = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="checks", verbose_name='Владелец')

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


class Bonus(models.Model):
    """
    Сколько бонусов начислять за 1 продукт
    """
    balance = models.DecimalField(default=100, decimal_places=2, max_digits=10, verbose_name='баланс')

    def __str__(self):
        return str(self.balance)

    class Meta:
        verbose_name = 'Начислять бонусов'
        verbose_name_plural = 'Начислять бонусов'
