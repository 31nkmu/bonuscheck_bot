from enum import Enum

from django.db import models


class Users(models.Model):
    """
    Пользователи
    """
    code = models.ForeignKey("Code", on_delete=models.SET_NULL, related_name="users", verbose_name='Код', null=True)

    is_banned = models.BooleanField(default=False, verbose_name='Забанен')
    registered_at = models.DateTimeField(auto_now=True, verbose_name='Зарегистрироан')
    tg_id = models.CharField(unique=True, max_length=120, verbose_name='Телеграм id')
    bonus_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Бонусны')
    is_admin = models.BooleanField(default=False, verbose_name='Админ')
    username = models.CharField(max_length=120)

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


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    NOT_ACTIVE = "not_active"
    BAN = "ban"
