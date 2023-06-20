from django.db import models
from django.core.validators import RegexValidator


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        help_text='Укажите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Укажите единицы измерения',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        help_text='Укажите название тега',
    )
    color = models.CharField(
        max_length=7,
        null=True,
        verbose_name='Цвет тега',
        help_text='Укажите цвет тега'
    )
    slug = models.CharField(
        max_length=200,
        null=True,
        verbose_name='Слуг',
        help_text='Укажите слуг',
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=(
                    'Max length 200, regex [-a-zA-Z0-9_]+$'
                ),
            ),
        ]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
