# Generated by Django 4.2.2 on 2023-07-13 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_code_excel_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='username',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]