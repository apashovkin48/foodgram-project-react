import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    BasketRecipe,
    Tag,
    Ingredient,
    IngredientAmount,
    Recipe,
    FavoriteRecipe,
)
from users.models import FollowingAuthor


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """
        Serializer для управления пользователями.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and FollowingAuthor.objects.filter(
                user=request.user, author=obj
            ).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """
        Serializer для тегов.
    """

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug'
        ]


class IngredientSerializer(serializers.ModelSerializer):
    """
        Serializer для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class IngredientAmountSerializer(serializers.ModelSerializer):
    """
        Serializer для ингредиентов и их содержание в рецепте.
    """

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]


class CreateIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
        Serializer для создания/изменения кулинарных рецептов.
    """

    ingredients = CreateIngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'ingredients',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    @staticmethod
    def create_ingredient_amount(recipe, ingredients):
        objs = []
        for ing in ingredients:
            id, amount = ing.values()
            ingredient = Ingredient.objects.get(id=id)
            objs.append(
                IngredientAmount(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            )
        IngredientAmount.objects.bulk_create(objs)

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient_amount(recipe, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientAmount.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.create_ingredient_amount(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return ReadRecipeSerializer(
            instance,
            context={'request': request}
        ).data


class ReadRecipeSerializer(serializers.ModelSerializer):
    """
        Serializer для получения полной информации о рецепте.
    """

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return BasketRecipe.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(ingredients, many=True).data


class MinRecipeSerializer(serializers.ModelSerializer):
    """
        Serializer для получения краткой информации о рецепте.
    """

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
        Serializer для добавления избранных рецептов.
    """

    class Meta:
        model = FavoriteRecipe
        fields = [
            'user',
            'recipe'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное!'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return MinRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ReprFollowingAuthorSerializer(UserSerializer):
    """
        Serializer для получения списка избранных авторов и их рецептов.
    """

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return True
        return (
            request.user.is_authenticated
            and FollowingAuthor.objects.filter(
                user=request.user, author=obj
            ).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return MinRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowingAuthorSerializer(serializers.ModelSerializer):
    """
        Serializer для подписки на авторов рецептов.
    """

    class Meta:
        model = FollowingAuthor
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=FollowingAuthor.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на данного автора!'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!',
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return ReprFollowingAuthorSerializer(
            instance.author,
            context={'request': request}
        ).data


class BasketRecipeSerializer(serializers.ModelSerializer):
    """
        Serializer для добавления добавления рецептов в список покупок.
    """

    class Meta:
        model = BasketRecipe
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=BasketRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Данный рецепт уже в списке покупок!'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return MinRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data
