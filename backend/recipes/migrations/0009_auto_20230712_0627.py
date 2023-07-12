# Generated by Django 3.2.3 on 2023-07-12 06:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_basketrecipe_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Укажите название ингредиента', max_length=200, unique=True, verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='Укажите цвет тега', max_length=7, verbose_name='Цвет тега'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(help_text='Укажите название тега', max_length=200, unique=True, verbose_name='Название тега'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.CharField(help_text='Укажите слуг', max_length=200, unique=True, validators=[django.core.validators.RegexValidator(message='Max length 200, regex [-a-zA-Z0-9_]+$', regex='^[-a-zA-Z0-9_]+$')], verbose_name='Слуг'),
        ),
    ]
