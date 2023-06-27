from django.db import models


class Users(models.Model):
    code = models.ForeignKey("Code", on_delete=models.CASCADE, related_name="users")

    is_banned = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now=True)
    tg_id = models.CharField(unique=True, max_length=120)
    bonus_balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.code


class Code(models.Model):
    title = models.CharField(max_length=120)
    keycode = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Check(models.Model):
    owner = models.ForeignKey("Users", on_delete=models.CASCADE, related_name="checks")

    qr_data = models.CharField(max_length=120)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.qr_data


class Output(models.Model):
    owner = models.ForeignKey("Users", on_delete=models.CASCADE, related_name="outputs")

    amount = models.PositiveIntegerField(default=1)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.amount)
