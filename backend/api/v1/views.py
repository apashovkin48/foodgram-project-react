from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import (
    viewsets,
    status,
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    RecipeSerializer,
    FavoriteRecipeSerializer,
    FollowingAuthorSerializer,
    ReprFollowingAuthorSerializer,
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    FavoriteRecipe,
    User
)
from users.models import (
    FollowingAuthor,
)


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
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
            FollowingAuthor.objects.filter(
                user=request.user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        data = User.objects.filter(following__user=self.request.user)
        serializer = ReprFollowingAuthorSerializer(data, many=True)
        return self.get_paginated_response(
            self.paginate_queryset(serializer.data)
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadRecipeSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = FavoriteRecipeSerializer(
                data={'user': request.user.id, 'recipe': recipe.id, },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            FavoriteRecipe.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
