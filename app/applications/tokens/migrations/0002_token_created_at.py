# Generated by Django 4.2.2 on 2023-07-12 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokens', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='created_at',
            field=models.DateTimeField(auto_now=True, verbose_name='дата создания'),
        ),
    ]
