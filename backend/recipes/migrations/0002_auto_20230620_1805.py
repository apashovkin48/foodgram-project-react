# Generated by Django 3.2.3 on 2023-06-20 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Укажите название ингредиента', max_length=200, verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(help_text='Укажите название тега', max_length=200, verbose_name='Название тега'),
        ),
    ]