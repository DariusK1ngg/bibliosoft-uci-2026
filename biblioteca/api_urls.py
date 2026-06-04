from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    MaterialViewSet, CategoriaViewSet, GeneroViewSet,
    AutorViewSet, FacultadViewSet, CarreraViewSet, EditorialViewSet
)

router = DefaultRouter()
router.register(r'materiales', MaterialViewSet, basename='api-material')
router.register(r'categorias', CategoriaViewSet, basename='api-categoria')
router.register(r'generos', GeneroViewSet, basename='api-genero')
router.register(r'autores', AutorViewSet, basename='api-autor')
router.register(r'facultades', FacultadViewSet, basename='api-facultad')
router.register(r'carreras', CarreraViewSet, basename='api-carrera')
router.register(r'editoriales', EditorialViewSet, basename='api-editorial')

urlpatterns = [
    path('', include(router.urls)),
]
