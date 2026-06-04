from django.contrib import admin
from .models import (
    Autor, Editorial, Categoria, Genero, TipoDocumento,
    Facultad, Carrera, Alumno, Material, Prestamo,
    MaterialCarrera, MaterialGenero, BajaMaterial, RegistroAuditoria
)

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('id_autor', 'nombre', 'apellido')
    search_fields = ('nombre', 'apellido')

@admin.register(Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ('id_editorial', 'nombre', 'direccion', 'telefono')
    search_fields = ('nombre',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre')
    search_fields = ('nombre',)

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('id_genero', 'nombre')
    search_fields = ('nombre',)

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id_tipo', 'descripcion')
    search_fields = ('descripcion',)

@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ('id_facultad', 'nombre')
    search_fields = ('nombre',)

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('id_carrera', 'nombre', 'facultades_id_facultad')
    search_fields = ('nombre',)

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('id_alumno', 'matricula', 'nombre', 'apellido', 'carreras_id_carrera', 'curso', 'numero_matricula', 'lector_numero', 'carnet_activo', 'estado')
    search_fields = ('matricula', 'nombre', 'apellido', 'numero_matricula', 'lector_numero')
    list_filter = ('carreras_id_carrera', 'carnet_activo', 'estado')

class MaterialCarreraInline(admin.TabularInline):
    model = MaterialCarrera
    extra = 1

class MaterialGeneroInline(admin.TabularInline):
    model = MaterialGenero
    extra = 1

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id_material', 'titulo', 'get_autores', 'categorias_id_categoria', 'cantidad_disponible', 'cantidad_total')
    search_fields = ('titulo', 'isbn')
    list_filter = ('categorias_id_categoria', 'autores_id_autor', 'editoriales_id_editorial')
    inlines = [MaterialCarreraInline, MaterialGeneroInline]

    def get_autores(self, obj):
        return ", ".join([str(a) for a in obj.autores_id_autor.all()])
    get_autores.short_description = 'Autor/es'

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('id_prestamo', 'ALUMNOS_id_alumno', 'MATERIALES_id_material', 'fecha_prestamo', 'fecha_vencimiento', 'estado', 'fecha_devolucion', 'multa')
    search_fields = ('ALUMNOS_id_alumno__matricula', 'MATERIALES_id_material__titulo')
    list_filter = ('estado', 'fecha_prestamo', 'fecha_devolucion')


@admin.register(BajaMaterial)
class BajaMaterialAdmin(admin.ModelAdmin):
    list_display = ('id_baja', 'material', 'cantidad', 'numero_entrada', 'motivo', 'fecha_baja')
    search_fields = ('material__titulo', 'numero_entrada')
    list_filter = ('motivo', 'fecha_baja')


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario', 'accion', 'tabla', 'registro_id', 'ip_address', 'detalle')
    list_filter = ('accion', 'tabla', 'fecha_hora')
    search_fields = ('usuario__username', 'detalle', 'ip_address')
    readonly_fields = ('fecha_hora', 'usuario', 'accion', 'tabla', 'registro_id', 'ip_address', 'detalle')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
