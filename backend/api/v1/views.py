from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import (
    filters,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from recipes.models import (
    BasketRecipe,
    FavoriteRecipe,
    Ingredient,
    IngredientAmount,
    Recipe,
    Tag,
    User,
)
from users.models import (
    FollowingAuthor,
)
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (
    BasketRecipeSerializer,
    FavoriteRecipeSerializer,
    FollowingAuthorSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    RecipeSerializer,
    ReprFollowingAuthorSerializer,
    TagSerializer,
)


class CustomUserViewSet(UserViewSet):
    """ViewSet для управлением пользователями."""

    queryset = User.objects.all()
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
        """
            Создаёт(POST) / Удалет(DELETE) связь между пользователями.
        """
        if not request.user.is_authenticated:
            return Response(
                {
                    "detail": "Учетные данные не были предоставлены."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = FollowingAuthorSerializer(
                data={'user': request.user.id, 'author': author.id, },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not FollowingAuthor.objects.filter(
                user=request.user, author=author
            ).exists():
                return Response(
                    {
                        "detail": "Вы не подписаны на данного автора."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            FollowingAuthor.objects.filter(
                user=request.user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """
            Возвращает пользователей, на которых подписан текущий пользователь.
            В выдачу добавляются рецепты.
        """
        if not request.user.is_authenticated:
            return Response(
                {
                    "detail": "Учетные данные не были предоставлены."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        data = User.objects.filter(following__user=self.request.user)
        serializer = ReprFollowingAuthorSerializer(data, many=True)
        return self.get_paginated_response(
            self.paginate_queryset(serializer.data)
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
        ViewSet получения тегов(тега).
        Изменение и создание тэгов разрешено только администраторам.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
        ViewSet получения ингредиентов(ингредиента).
        Изменение и создание ингредиентов разрешено только администраторам.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с кулинарными рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAdminAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadRecipeSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        """
            Добавляет(POST) / Удалет(DELETE) избранные рецепты.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteRecipeSerializer(
                data={'user': request.user.id, 'recipe': recipe.id, },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not FavoriteRecipe.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {
                        "error": "Данный рецепт не является избранным!"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        """
            Добавляет(POST) / Удалет(DELETE) рецепты в карзину покупок.
        """

        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = BasketRecipeSerializer(
                data={'user': request.user.id, 'recipe': recipe.id, },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not BasketRecipe.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {
                        "error": "Данного рецепта нет в корзине!"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            BasketRecipe.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        """
            Выгрузка PDF файла со списком покупок.
        """
        basket_recipes = BasketRecipe.objects.filter(user=request.user)
        ingredients = IngredientAmount.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping = ['Меню для приготовления:\n\n']
        for rcp in basket_recipes:
            shopping.append(f'{rcp.recipe.name}\n')
        shopping.append('\n-------------------------------------\n\n')
        shopping.append('Список покупок:\n\n')
        for ingredient in ingredients:
            shopping.append(
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["ingredient__measurement_unit"]}, '
                f'{ingredient["ingredient_amount"]}\n'
            )
        return FileResponse(
            shopping,
            as_attachment=True,
            filename='Список_Покупок.pdf'
        )
