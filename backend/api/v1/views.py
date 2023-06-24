from rest_framework import (
    views,
    viewsets
)
from .serializers import (
    TagSerializer,
)
from recipes.models import (
    Tag,
)


class TagView(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
