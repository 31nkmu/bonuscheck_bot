# Generated by Django 4.2.2 on 2023-07-12 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outputs', '0002_alter_minbalance_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='output',
            name='send_data',
            field=models.CharField(default=2, max_length=200),
            preserve_default=False,
        ),
    ]
