from django.db import models


class Token(models.Model):
    token = models.CharField(verbose_name='токен', max_length=200)
    created_at = models.DateTimeField(auto_now=True, verbose_name='дата создания')

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'
