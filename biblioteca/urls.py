from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    DashboardView,
    MaterialListView, MaterialCreateView, MaterialUpdateView, MaterialDeleteView,
    PrestamoListView, PrestamoCreateView, PrestamoUpdateView, PrestamoProrrogaView, PrestamoDeleteView,
    AlumnoListView, AlumnoCreateView, AlumnoUpdateView, AlumnoDeleteView, AlumnoActivarCarnetView, AlumnoDesactivarCarnetView,
    UserProfileView,
    AutorListView, AutorCreateView, AutorUpdateView, AutorDeleteView,
    EditorialListView, EditorialCreateView, EditorialUpdateView, EditorialDeleteView,
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    GeneroListView, GeneroCreateView, GeneroUpdateView, GeneroDeleteView,
    TipoDocumentoListView, TipoDocumentoCreateView, TipoDocumentoUpdateView, TipoDocumentoDeleteView,
    FacultadListView, FacultadCreateView, FacultadUpdateView, FacultadDeleteView,
    CarreraListView, CarreraCreateView, CarreraUpdateView, CarreraDeleteView,
    DevolucionListView, DevolucionCreateView,
    ReportesView, ReportePrintView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Materiales
    path('materiales/', MaterialListView.as_view(), name='material-list'),
    path('materiales/nuevo/', MaterialCreateView.as_view(), name='material-create'),
    path('materiales/<int:pk>/editar/', MaterialUpdateView.as_view(), name='material-update'),
    path('materiales/<int:pk>/borrar/', MaterialDeleteView.as_view(), name='material-delete'),


    # Préstamos
    path('prestamos/', PrestamoListView.as_view(), name='prestamo-list'),
    path('prestamos/nuevo/', PrestamoCreateView.as_view(), name='prestamo-create'),
    path('prestamos/<int:pk>/editar/', PrestamoUpdateView.as_view(), name='prestamo-update'),
    path('prestamos/<int:pk>/prorroga/', PrestamoProrrogaView.as_view(), name='prestamo-prorroga'),
    path('prestamos/<int:pk>/borrar/', PrestamoDeleteView.as_view(), name='prestamo-delete'),

    # Alumnos
    path('alumnos/', AlumnoListView.as_view(), name='alumno-list'),
    path('alumnos/nuevo/', AlumnoCreateView.as_view(), name='alumno-create'),
    path('alumnos/<int:pk>/editar/', AlumnoUpdateView.as_view(), name='alumno-update'),
    path('alumnos/<int:pk>/borrar/', AlumnoDeleteView.as_view(), name='alumno-delete'),
    path('alumnos/<int:pk>/activar-carnet/', AlumnoActivarCarnetView.as_view(), name='alumno-activar-carnet'),
    path('alumnos/<int:pk>/desactivar-carnet/', AlumnoDesactivarCarnetView.as_view(), name='alumno-desactivar-carnet'),

    # Autores
    path('autores/', AutorListView.as_view(), name='autor-list'),
    path('autores/nuevo/', AutorCreateView.as_view(), name='autor-create'),
    path('autores/<int:pk>/editar/', AutorUpdateView.as_view(), name='autor-update'),
    path('autores/<int:pk>/borrar/', AutorDeleteView.as_view(), name='autor-delete'),

    # Editoriales
    path('editoriales/', EditorialListView.as_view(), name='editorial-list'),
    path('editoriales/nuevo/', EditorialCreateView.as_view(), name='editorial-create'),
    path('editoriales/<int:pk>/editar/', EditorialUpdateView.as_view(), name='editorial-update'),
    path('editoriales/<int:pk>/borrar/', EditorialDeleteView.as_view(), name='editorial-delete'),

    # Categorías
    path('categorias/', CategoriaListView.as_view(), name='categoria-list'),
    path('categorias/nuevo/', CategoriaCreateView.as_view(), name='categoria-create'),
    path('categorias/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria-update'),
    path('categorias/<int:pk>/borrar/', CategoriaDeleteView.as_view(), name='categoria-delete'),

    # Géneros
    path('generos/', GeneroListView.as_view(), name='genero-list'),
    path('generos/nuevo/', GeneroCreateView.as_view(), name='genero-create'),
    path('generos/<int:pk>/editar/', GeneroUpdateView.as_view(), name='genero-update'),
    path('generos/<int:pk>/borrar/', GeneroDeleteView.as_view(), name='genero-delete'),

    # Tipos de Documento
    path('tipodocumentos/', TipoDocumentoListView.as_view(), name='tipodocumento-list'),
    path('tipodocumentos/nuevo/', TipoDocumentoCreateView.as_view(), name='tipodocumento-create'),
    path('tipodocumentos/<int:pk>/editar/', TipoDocumentoUpdateView.as_view(), name='tipodocumento-update'),
    path('tipodocumentos/<int:pk>/borrar/', TipoDocumentoDeleteView.as_view(), name='tipodocumento-delete'),

    # Facultades
    path('facultades/', FacultadListView.as_view(), name='facultad-list'),
    path('facultades/nuevo/', FacultadCreateView.as_view(), name='facultad-create'),
    path('facultades/<int:pk>/editar/', FacultadUpdateView.as_view(), name='facultad-update'),
    path('facultades/<int:pk>/borrar/', FacultadDeleteView.as_view(), name='facultad-delete'),

    # Carreras
    path('carreras/', CarreraListView.as_view(), name='carrera-list'),
    path('carreras/nuevo/', CarreraCreateView.as_view(), name='carrera-create'),
    path('carreras/<int:pk>/editar/', CarreraUpdateView.as_view(), name='carrera-update'),
    path('carreras/<int:pk>/borrar/', CarreraDeleteView.as_view(), name='carrera-delete'),

    # Devoluciones
    path('devoluciones/', DevolucionListView.as_view(), name='devolucion-list'),
    path('devoluciones/nuevo/', DevolucionCreateView.as_view(), name='devolucion-create'),

    # Reportes
    path('reportes/', ReportesView.as_view(), name='reportes'),
    path('reportes/imprimir/', ReportePrintView.as_view(), name='reporte-print'),

    # Perfil y Contraseña
    path('perfil/', UserProfileView.as_view(), name='user-profile'),
    path('cambiar-password/', auth_views.PasswordChangeView.as_view(
        template_name='biblioteca/password_change_form.html',
        success_url=reverse_lazy('custom_password_change_done')
    ), name='custom_password_change'),
    path('cambiar-password/hecho/', auth_views.PasswordChangeDoneView.as_view(
        template_name='biblioteca/password_change_done.html'
    ), name='custom_password_change_done'),
]

