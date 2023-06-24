from . import views
from django.urls import path, include
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(
    r'tags',
    views.TagView,
    basename='tags'
)


urlpatterns = [
    path('', include(router.urls)),
]
