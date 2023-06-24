from django.urls import path, include
from .v1 import urls as v1_urls

app_name = 'api'

urlpatterns = [
    path('', include(v1_urls))
]
