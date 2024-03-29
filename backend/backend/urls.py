from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='docs/redoc.html'),
        name='redoc'
    ),
    path('api/auth/', include('djoser.urls.authtoken')),
    path(
        'api/',
        include('api.urls', namespace='api')
    ),
]
