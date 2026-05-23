from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import MaterialViewSet, CategoriaViewSet

router = DefaultRouter()
router.register(r'materiales', MaterialViewSet, basename='api-material')
router.register(r'categorias', CategoriaViewSet, basename='api-categoria')

urlpatterns = [
    path('', include(router.urls)),
]
