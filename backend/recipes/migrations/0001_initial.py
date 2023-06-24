# Generated by Django 3.2.3 on 2023-06-20 17:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название ингредиента', max_length=200, unique=True, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(help_text='Укажите единицы измерения', max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название тега', max_length=200, unique=True, verbose_name='Название тега')),
                ('color', models.CharField(help_text='Укажите цвет тега', max_length=7, null=True, verbose_name='Цвет тега')),
                ('slug', models.CharField(help_text='Укажите слуг', max_length=200, null=True, validators=[django.core.validators.RegexValidator(message='Max length 200, regex [-a-zA-Z0-9_]+$', regex='^[-a-zA-Z0-9_]+$')], verbose_name='Слуг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['name'],
            },
        ),
    ]