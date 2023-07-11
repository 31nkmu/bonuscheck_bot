# Generated by Django 4.2.2 on 2023-07-11 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_output_owner'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='check',
            options={'verbose_name': 'Чек', 'verbose_name_plural': 'Чеки'},
        ),
        migrations.AlterModelOptions(
            name='code',
            options={'verbose_name': 'Код', 'verbose_name_plural': 'Коды'},
        ),
        migrations.AlterModelOptions(
            name='codeword',
            options={'verbose_name': 'Проверочное слово', 'verbose_name_plural': 'Проверочные слова'},
        ),
        migrations.AlterModelOptions(
            name='gtin',
            options={'verbose_name': 'Gtin', 'verbose_name_plural': 'Gtin'},
        ),
        migrations.AlterModelOptions(
            name='output',
            options={'verbose_name': 'Вывод', 'verbose_name_plural': 'Выводы'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Продукт', 'verbose_name_plural': 'Продукты'},
        ),
        migrations.AlterModelOptions(
            name='users',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.RemoveField(
            model_name='code',
            name='title',
        ),
        migrations.AddField(
            model_name='output',
            name='created_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Создан'),
        ),
        migrations.AlterField(
            model_name='check',
            name='bonus_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Бонусный баланс'),
        ),
        migrations.AlterField(
            model_name='check',
            name='is_accepted',
            field=models.BooleanField(default=True, verbose_name='Принят'),
        ),
        migrations.AlterField(
            model_name='check',
            name='is_processed',
            field=models.BooleanField(default=False, verbose_name='Обработан'),
        ),
        migrations.AlterField(
            model_name='check',
            name='is_reject',
            field=models.BooleanField(default=False, verbose_name='Отклонен'),
        ),
        migrations.AlterField(
            model_name='check',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checks', to='users.users', verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='check',
            name='qr_data',
            field=models.CharField(max_length=120, unique=True, verbose_name='qr код'),
        ),
        migrations.AlterField(
            model_name='code',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
        migrations.AlterField(
            model_name='code',
            name='keycode',
            field=models.CharField(max_length=120, verbose_name='Код'),
        ),
        migrations.AlterField(
            model_name='codeword',
            name='word',
            field=models.CharField(max_length=120, unique=True, verbose_name='Слово'),
        ),
        migrations.AlterField(
            model_name='output',
            name='amount',
            field=models.PositiveIntegerField(default=1, verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='output',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Оплачено'),
        ),
        migrations.AlterField(
            model_name='output',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='users.users', verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='output',
            name='status',
            field=models.CharField(choices=[('processing', 'В обработке'), ('accepted', 'Принят'), ('rejected', 'Отклонен')], default='processing', max_length=20, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='product',
            name='check_field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='users.check', verbose_name='Чек'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.TextField(verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.PositiveIntegerField(verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='users',
            name='bonus_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Бонусны'),
        ),
        migrations.AlterField(
            model_name='users',
            name='code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='users.code', verbose_name='Код'),
        ),
        migrations.AlterField(
            model_name='users',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Админ'),
        ),
        migrations.AlterField(
            model_name='users',
            name='is_banned',
            field=models.BooleanField(default=False, verbose_name='Забанен'),
        ),
        migrations.AlterField(
            model_name='users',
            name='registered_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Зарегистрироан'),
        ),
        migrations.AlterField(
            model_name='users',
            name='tg_id',
            field=models.CharField(max_length=120, unique=True, verbose_name='Телеграм id'),
        ),
    ]
