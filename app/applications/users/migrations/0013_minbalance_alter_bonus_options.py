# Generated by Django 4.2.2 on 2023-07-12 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_bonus_alter_users_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='MinBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=500, max_digits=10)),
            ],
            options={
                'verbose_name': 'Минимальный баланс',
                'verbose_name_plural': 'Минимальный баланс',
            },
        ),
        migrations.AlterModelOptions(
            name='bonus',
            options={'verbose_name': 'Начислять бонусов', 'verbose_name_plural': 'Начислять бонусов'},
        ),
    ]
