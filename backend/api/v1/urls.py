from . import views
from django.urls import path, include
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(
    r'tags',
    views.TagViewSet,
    basename='tags'
)
router.register(
    r'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)
router.register(
    r'recipes',
    views.RecipeViewSet,
    basename='recipes'
)
router.register(
    r"users",
    views.CustomUserViewSet,
    basename="users"
)


urlpatterns = [
    path('', include(router.urls)),
]
