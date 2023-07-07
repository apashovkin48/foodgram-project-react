from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from recipes.models import (
    Tag,
    Ingredient,
    IngredientAmount,
    Recipe,
    FavoriteRecipe,
)
from users.models import FollowingAuthor
from django.contrib.auth import get_user_model
from django.db.transaction import atomic


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug'
        ]


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class IngredientAmountSerializer(serializers.ModelSerializer):

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

    ingredients = CreateIngredientAmountSerializer(many=True)

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

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(ingredients, many=True).data


class MinRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class FavoriteRecipeSerializer(serializers.ModelSerializer):

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

    def to_representation(self, instance):
        request = self.context.get('request')
        return ReprFollowingAuthorSerializer(
            instance.author,
            context={'request': request}
        ).data
