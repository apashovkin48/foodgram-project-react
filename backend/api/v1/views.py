from rest_framework import (
    views,
    viewsets
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
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
    serializer_class = RecipeSerializer
