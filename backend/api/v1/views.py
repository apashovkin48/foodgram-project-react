from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (
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
from .filters import (
    IngredientFilter,
    RecipeFilter,
)
from .mixins import CreateDestroyObjMixinRecipe
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(
    viewsets.ModelViewSet,
    CreateDestroyObjMixinRecipe
):
    """ViewSet для работы с кулинарными рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAdminAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadRecipeSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        """
            Добавляет(POST) / Удалет(DELETE) избранные рецепты.
        """
        if request.method == 'POST':
            return self.mixin_create(request, FavoriteRecipeSerializer, pk)
        return self.mixin_destroy(request, FavoriteRecipe, pk)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        """
            Добавляет(POST) / Удалет(DELETE) рецепты в карзину покупок.
        """
        if request.method == 'POST':
            return self.mixin_create(request, BasketRecipeSerializer, pk)
        return self.mixin_destroy(request, BasketRecipe, pk)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        """
            Выгрузка PDF файла со списком покупок.
        """
        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

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

        filename = "shopping_list.txt"
        response = HttpResponse(
            shopping, content_type="text.txt; charset=utf-8"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
