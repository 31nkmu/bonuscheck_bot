from django.db import models

from applications.users.models import Users


class Output(models.Model):
    """
    Заявка на вывод
    """
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]

    owner = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="outputs", verbose_name='Владелец')

    amount = models.PositiveIntegerField(default=1, verbose_name='Количество')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачено')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Создан')

    def __str__(self):
        return str(self.amount)

    class Meta:
        verbose_name = "Вывод"
        verbose_name_plural = "Выводы"


class MinBalance(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500, verbose_name='баланс')

    class Meta:
        verbose_name = 'Минимальный вывод'
        verbose_name_plural = 'Минимальный вывод'

    def __str__(self):
        return str(self.balance)
