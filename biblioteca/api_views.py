from rest_framework import viewsets, filters
from .models import Material, Categoria
from .serializers import MaterialSerializer, CategoriaSerializer

class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'autor__nombre', 'autor__apellido', 'categoria__nombre']

class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

