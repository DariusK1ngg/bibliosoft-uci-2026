from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from .models import Material, Categoria, Genero, Autor, Facultad, Carrera, Editorial
from .serializers import (
    MaterialSerializer, CategoriaSerializer,
    GeneroSerializer, AutorSerializer,
    FacultadSerializer, CarreraSerializer,
    EditorialSerializer
)

class MaterialPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MaterialSerializer
    pagination_class = MaterialPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'autores_id_autor__nombre', 'autores_id_autor__apellido', 'categorias_id_categoria__nombre']

    def get_queryset(self):
        queryset = Material.objects.all().select_related(
            'editoriales_id_editorial',
            'categorias_id_categoria',
            'tipodocumento_id_tipo'
        ).prefetch_related('autores_id_autor', 'generos', 'carreras')
        
        # public page catalog filters
        genero_id = self.request.query_params.get('genero')
        autor_id = self.request.query_params.get('autor')
        carrera_id = self.request.query_params.get('carrera')
        facultad_id = self.request.query_params.get('facultad')
        editorial_id = self.request.query_params.get('editorial')
        solo_disponibles = self.request.query_params.get('disponible')
        tipo_registro = self.request.query_params.get('tipo_registro')
        orden = self.request.query_params.get('orden')

        if genero_id:
            queryset = queryset.filter(generos=genero_id)
        if autor_id:
            queryset = queryset.filter(autores_id_autor=autor_id)
        if carrera_id:
            queryset = queryset.filter(carreras=carrera_id)
        if facultad_id:
            queryset = queryset.filter(carreras__facultades_id_facultad=facultad_id)
        if editorial_id:
            queryset = queryset.filter(editoriales_id_editorial=editorial_id)
        if solo_disponibles == '1' or solo_disponibles == 'true':
            queryset = queryset.filter(cantidad_disponible__gt=0)
        if tipo_registro:
            queryset = queryset.filter(tipo_registro=tipo_registro)

        # Ordering
        if orden == 'reciente':
            queryset = queryset.order_by('-año_publicacion', '-id_material')
        elif orden == 'antiguo':
            queryset = queryset.order_by('año_publicacion', '-id_material')
        elif orden == 'agregado':
            queryset = queryset.order_by('-id_material')
        else:
            queryset = queryset.order_by('-id_material')

        return queryset.distinct()

class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']

class GeneroViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genero.objects.all().order_by('nombre')
    serializer_class = GeneroSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']

class AutorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Autor.objects.all().order_by('apellido', 'nombre')
    serializer_class = AutorSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'apellido']

class FacultadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Facultad.objects.all().order_by('nombre')
    serializer_class = FacultadSerializer
    pagination_class = None

class CarreraViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Carrera.objects.all().order_by('nombre')
    serializer_class = CarreraSerializer
    pagination_class = None

class EditorialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Editorial.objects.all().order_by('nombre')
    serializer_class = EditorialSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']

