# Generated by Django 4.2.2 on 2023-07-06 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_check_bonus_balance_alter_check_qr_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='check',
            name='is_accepted',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='check',
            name='is_reject',
            field=models.BooleanField(default=False),
        ),
    ]
