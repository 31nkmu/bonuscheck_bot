# Generated by Django 4.2.2 on 2023-07-13 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_code_excel_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='code',
            name='keycode',
            field=models.CharField(max_length=120, unique=True, verbose_name='Код'),
        ),
    ]