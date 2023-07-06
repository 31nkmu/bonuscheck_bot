# Generated by Django 4.2.2 on 2023-07-06 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_codeword_word'),
    ]

    operations = [
        migrations.AddField(
            model_name='check',
            name='bonus_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='check',
            name='qr_data',
            field=models.CharField(max_length=120, unique=True),
        ),
    ]
