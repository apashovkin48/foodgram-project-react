from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator


User = get_user_model()


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


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название блюда',
        help_text='Укажите название блюда',
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        help_text='Укажите автора рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        help_text='Укажите теги рецепта',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        help_text='Укажите ингредиенты блюда',
        related_name='recipes',
        through='IngredientAmount',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Дата публикации',
        help_text='Укажите дату для публикации',
    )
    image = models.ImageField(
        'Изображение блюда',
        upload_to='recipes_img/',
    )
    text = models.TextField(
        verbose_name='Описание блюда',
        help_text='Укажите описание блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления',
        validators=(
            MinValueValidator(1),
        ),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(1),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ['recipe']

    def __str__(self) -> str:
        return f'{self.ingredients} - {self.amount}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        help_text='Укажите пользователя',
        related_name='favorites',
        on_delete=models.SET_NULL,
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Репецт',
        help_text='Укажите понравившейся рецепт',
        related_name='in_favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="Нельзя добавить рецепт в избранное более одного раза."
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} - {self.recipe}"


class BasketRecipe(models.Model):
    user = models.ForeignKey(
        verbose_name="Владелец списка",
        related_name="carts",
        to=User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        verbose_name="Рецепты в списке покупок",
        related_name="in_carts",
        to=Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="Нельзя добавить рецепт в корзину более одного раза."
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} - {self.recipe}"
