# Generated by Django 4.2.2 on 2023-07-11 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_gtin_alter_output_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='output',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='users.users'),
        ),
    ]
