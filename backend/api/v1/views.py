from rest_framework import (
    views,
    viewsets
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
)
from recipes.models import (
    Tag,
    Ingredient,
)


class TagView(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientView(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
