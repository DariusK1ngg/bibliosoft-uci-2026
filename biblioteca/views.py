from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import (
    Material, Alumno, Prestamo, Autor, Editorial, Categoria, Genero,
    TipoDocumento, Facultad, Carrera, Devolucion, ConfiguracionGeneral
)
from .forms import (
    PrestamoForm, AlumnoForm, UserProfileForm,
    AutorForm, EditorialForm, CategoriaForm, GeneroForm,
    TipoDocumentoForm, FacultadForm, CarreraForm, DevolucionForm,
    LibroForm, TrabajoInvestigacionForm, OtrosMaterialesForm, ConfiguracionGeneralForm
)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'biblioteca/dashboard.html'

    def get_context_data(self, **kwargs):
        Prestamo.actualizar_vencidos()
        context = super().get_context_data(**kwargs)
        context['total_materiales'] = Material.objects.count()
        context['total_alumnos'] = Alumno.objects.count()
        context['prestamos_activos'] = Prestamo.objects.filter(estado='ACTIVO').count()
        return context

# --- MATERIAL CRUD ---
class MaterialListView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'biblioteca/material_list.html'
    context_object_name = 'materiales'

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(autores_id_autor__nombre__icontains=q) |
                Q(autores_id_autor__apellido__icontains=q) |
                Q(isbn__icontains=q)
            )
        return queryset

class MaterialCreateView(LoginRequiredMixin, CreateView):
    model = Material
    template_name = 'biblioteca/material_form.html'
    success_url = reverse_lazy('material-list')

    def get_form_class(self):
        tipo = self.request.GET.get('tipo', 'libro')
        if tipo == 'trabajo':
            return TrabajoInvestigacionForm
        elif tipo == 'otro':
            return OtrosMaterialesForm
        return LibroForm

    def form_valid(self, form):
        tipo = self.request.GET.get('tipo', 'libro')
        if tipo == 'trabajo':
            form.instance.tipo_registro = 'TRABAJO_INVESTIGACION'
        elif tipo == 'otro':
            form.instance.tipo_registro = 'OTROS'
        else:
            form.instance.tipo_registro = 'LIBRO'
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo = self.request.GET.get('tipo', 'libro')
        if tipo == 'trabajo':
            context['tipo_label'] = 'Trabajo de Investigación'
            context['tipo_registro'] = 'TRABAJO_INVESTIGACION'
        elif tipo == 'otro':
            context['tipo_label'] = 'Otro Material'
            context['tipo_registro'] = 'OTROS'
        else:
            context['tipo_label'] = 'Libro'
            context['tipo_registro'] = 'LIBRO'
        
        # Pass list of materials for list background overlay
        queryset = Material.objects.all()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(autores_id_autor__nombre__icontains=q) |
                Q(autores_id_autor__apellido__icontains=q) |
                Q(isbn__icontains=q)
            )
        context['materiales'] = queryset
        return context

class MaterialUpdateView(LoginRequiredMixin, UpdateView):
    model = Material
    template_name = 'biblioteca/material_form.html'
    success_url = reverse_lazy('material-list')

    def get_form_class(self):
        obj = self.get_object()
        if obj.tipo_registro == 'TRABAJO_INVESTIGACION':
            return TrabajoInvestigacionForm
        elif obj.tipo_registro == 'OTROS':
            return OtrosMaterialesForm
        return LibroForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        if obj.tipo_registro == 'TRABAJO_INVESTIGACION':
            context['tipo_label'] = 'Trabajo de Investigación'
            context['tipo_registro'] = 'TRABAJO_INVESTIGACION'
        elif obj.tipo_registro == 'OTROS':
            context['tipo_label'] = 'Otro Material'
            context['tipo_registro'] = 'OTROS'
        else:
            context['tipo_label'] = 'Libro'
            context['tipo_registro'] = 'LIBRO'
            
        # Pass list of materials for list background overlay
        queryset = Material.objects.all()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(autores_id_autor__nombre__icontains=q) |
                Q(autores_id_autor__apellido__icontains=q) |
                Q(isbn__icontains=q)
            )
        context['materiales'] = queryset
        return context

class MaterialDeleteView(LoginRequiredMixin, DeleteView):
    model = Material
    template_name = 'biblioteca/material_confirm_delete.html'
    success_url = reverse_lazy('material-list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.tiene_prestamos:
            messages.error(request, f"No se puede eliminar el material '{self.object.titulo}' porque tiene préstamos asociados en el historial.")
            return redirect('material-list')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.tiene_prestamos:
            messages.error(request, f"No se puede eliminar el material '{self.object.titulo}' porque tiene préstamos asociados en el historial.")
            return redirect('material-list')
        response = super().post(request, *args, **kwargs)
        messages.success(request, "Material eliminado correctamente.")
        return response



# --- PRESTAMO CRUD ---
class PrestamoListView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'biblioteca/prestamo_list.html'
    context_object_name = 'prestamos'

    def get_queryset(self):
        Prestamo.actualizar_vencidos()
        queryset = Prestamo.objects.all().order_by('-id_prestamo')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(id_prestamo__icontains=q) |
                Q(ALUMNOS_id_alumno__nombre__icontains=q) |
                Q(ALUMNOS_id_alumno__apellido__icontains=q) |
                Q(ALUMNOS_id_alumno__matricula__icontains=q) |
                Q(MATERIALES_id_material__titulo__icontains=q) |
                Q(numero_entrada__icontains=q) |
                Q(estado__icontains=q)
            )
        return queryset

class PrestamoCreateView(LoginRequiredMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'biblioteca/prestamo_form.html'
    success_url = reverse_lazy('prestamo-list')

    def form_valid(self, form):
        from django.core.exceptions import ValidationError
        form.instance.administrador_usuariosbibliosoft_id = self.request.user
        form.instance.fecha_vencimiento = timezone.now().date() + timezone.timedelta(days=2)
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materiales_data = {}
        materiales = Material.objects.all()
        for m in materiales:
            materiales_data[m.id_material] = {
                'numeros': m.numeros_entrada_disponibles(),
                'titulo': m.titulo,
                'disponible': m.cantidad_disponible
            }
        context['materiales_json'] = materiales_data
        return context

class PrestamoUpdateView(LoginRequiredMixin, UpdateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'biblioteca/prestamo_form.html'
    success_url = reverse_lazy('prestamo-list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.estado == 'DEVUELTO':
            messages.error(request, "No se puede editar un préstamo que ya ha sido devuelto.")
            return redirect('prestamo-list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materiales_data = {}
        materiales = Material.objects.all()
        prestamo = self.get_object()
        for m in materiales:
            disp = m.cantidad_disponible
            if prestamo.MATERIALES_id_material == m:
                disp += prestamo.cantidad
            materiales_data[m.id_material] = {
                'numeros': m.numeros_entrada_disponibles(exclude_prestamo_id=prestamo.pk),
                'titulo': m.titulo,
                'disponible': disp
            }
        context['materiales_json'] = materiales_data
        return context

class PrestamoProrrogaView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        prestamo = Prestamo.objects.filter(pk=pk).first()
        if prestamo:
            if prestamo.estado in ['ACTIVO', 'VENCIDO']:
                prestamo.fecha_prestamo = timezone.now().date()
                prestamo.fecha_vencimiento = timezone.now().date() + timezone.timedelta(days=2)
                prestamo.estado = 'ACTIVO'
                prestamo.prorrogado = True
                prestamo.save()
                messages.success(request, f"Se ha concedido una prórroga de 2 días para el préstamo #{prestamo.id_prestamo}.")
            else:
                messages.error(request, "Solo se pueden prorrogar préstamos activos o vencidos.")
        else:
            messages.error(request, "Préstamo no encontrado.")
        return redirect('prestamo-list')

class PrestamoDeleteView(LoginRequiredMixin, DeleteView):
    model = Prestamo
    template_name = 'biblioteca/prestamo_confirm_delete.html'
    success_url = reverse_lazy('prestamo-list')

    def get(self, request, *args, **kwargs):
        messages.error(request, "No se permite eliminar registros de préstamos para preservar el historial de circulación.")
        return redirect('prestamo-list')

    def post(self, request, *args, **kwargs):
        messages.error(request, "No se permite eliminar registros de préstamos para preservar el historial de circulación.")
        return redirect('prestamo-list')

# --- ALUMNO CRUD ---
class AlumnoListView(LoginRequiredMixin, ListView):
    model = Alumno
    template_name = 'biblioteca/alumno_list.html'
    context_object_name = 'alumnos'

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(apellido__icontains=q) |
                Q(matricula__icontains=q)
            )
        return queryset

class AlumnoCreateView(LoginRequiredMixin, CreateView):
    model = Alumno
    form_class = AlumnoForm
    template_name = 'biblioteca/alumno_form.html'
    success_url = reverse_lazy('alumno-list')

class AlumnoUpdateView(LoginRequiredMixin, UpdateView):
    model = Alumno
    form_class = AlumnoForm
    template_name = 'biblioteca/alumno_form.html'
    success_url = reverse_lazy('alumno-list')

class AlumnoDeleteView(LoginRequiredMixin, DeleteView):
    model = Alumno
    template_name = 'biblioteca/alumno_confirm_delete.html'
    success_url = reverse_lazy('alumno-list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if Prestamo.objects.filter(ALUMNOS_id_alumno=self.object).exists():
            messages.error(request, f"No se puede eliminar al alumno {self.object.nombre} {self.object.apellido} porque tiene préstamos asociados.")
            return redirect('alumno-list')
        if self.object.carnet_activo:
            messages.error(request, f"No se puede eliminar al alumno {self.object.nombre} {self.object.apellido} porque tiene un carnet activo.")
            return redirect('alumno-list')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if Prestamo.objects.filter(ALUMNOS_id_alumno=self.object).exists():
            messages.error(request, f"No se puede eliminar al alumno {self.object.nombre} {self.object.apellido} porque tiene préstamos asociados.")
            return redirect('alumno-list')
        if self.object.carnet_activo:
            messages.error(request, f"No se puede eliminar al alumno {self.object.nombre} {self.object.apellido} porque tiene un carnet activo.")
            return redirect('alumno-list')
        response = super().post(request, *args, **kwargs)
        messages.success(request, "Alumno eliminado correctamente.")
        return response

class AlumnoActivarCarnetView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        alumno = Alumno.objects.filter(pk=pk).first()
        if alumno:
            fecha_str = request.POST.get('fecha_entrega')
            if fecha_str:
                from datetime import datetime
                try:
                    fecha_entrega = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except ValueError:
                    fecha_entrega = timezone.now().date()
            else:
                fecha_entrega = timezone.now().date()
            
            alumno.carnet_activo = True
            alumno.carnet_fecha_entrega = fecha_entrega
            alumno.save()
            messages.success(request, f"Se ha activado el carnet para {alumno.nombre} {alumno.apellido} con fecha {fecha_entrega.strftime('%d/%m/%Y')}.")
        else:
            messages.error(request, "Alumno no encontrado.")
        return redirect('alumno-list')

class AlumnoDesactivarCarnetView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        alumno = Alumno.objects.filter(pk=pk).first()
        if alumno:
            alumno.carnet_activo = False
            alumno.carnet_fecha_entrega = None
            alumno.save()
            messages.success(request, f"Se ha retirado/desactivado el carnet para {alumno.nombre} {alumno.apellido}.")
        else:
            messages.error(request, "Alumno no encontrado.")
        return redirect('alumno-list')


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'biblioteca/profile.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user


# --- BASE GENERIC CATALOG VIEWS ---
class BaseCatalogListView(LoginRequiredMixin, ListView):
    template_name = 'biblioteca/generic_list.html'
    col_class = 'col-lg-7 col-md-9'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = []
        for obj in self.get_queryset():
            row_data = {
                'pk': obj.pk,
                'cells': []
            }
            for field in self.fields:
                val = getattr(obj, field)
                if val is None:
                    cell_val = "—"
                elif isinstance(val, bool):
                    cell_val = "Sí" if val else "No"
                elif hasattr(val, '__str__'):
                    cell_val = str(val)
                else:
                    cell_val = val
                row_data['cells'].append(cell_val)
            rows.append(row_data)
        
        # Guess delete_url_name from edit_url_name
        delete_url_name = None
        if self.edit_url_name:
            delete_url_name = self.edit_url_name.replace('-update', '-delete')
            
        context['rows'] = rows
        context['headers'] = self.headers
        context['title'] = self.title
        context['subtitle'] = self.subtitle
        context['create_url_name'] = self.create_url_name
        context['edit_url_name'] = self.edit_url_name
        context['delete_url_name'] = delete_url_name
        context['col_class'] = self.col_class
        return context

class BaseCatalogCreateView(LoginRequiredMixin, CreateView):
    template_name = 'biblioteca/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Nuevo {self.model._meta.verbose_name}'
        context['subtitle'] = f'Carga un nuevo registro en el catálogo de {self.model._meta.verbose_name_plural.lower()}'
        context['cancel_url'] = self.success_url
        return context

    def form_valid(self, form):
        self.object = form.save()
        if self.request.GET.get('popup') == '1' or self.request.POST.get('popup') == '1':
            field_name = self.request.GET.get('field_name') or self.request.POST.get('field_name') or ''
            obj_pk = self.object.pk
            obj_repr = getattr(self.object, 'descripcion', str(self.object))
            from django.http import HttpResponse
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Guardado</title>
            </head>
            <body>
                <script>
                    const parentWin = window.opener || (window.parent !== window ? window.parent : null);
                    if (parentWin) {{
                        parentWin.handlePopupResponse("{field_name}", "{obj_pk}", "{obj_repr}");
                    }}
                    if (window.opener) {{
                        window.close();
                    }} else if (parentWin && parentWin.closePopupModal) {{
                        parentWin.closePopupModal();
                    }}
                </script>
            </body>
            </html>
            """
            return HttpResponse(html)
        return super().form_valid(form)

class BaseCatalogUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'biblioteca/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar {self.model._meta.verbose_name}'
        context['subtitle'] = f'Modifica la información de un registro del catálogo de {self.model._meta.verbose_name_plural.lower()}'
        context['cancel_url'] = self.success_url
        
        # Add delete_url dynamically if reverse works
        from django.urls import reverse, NoReverseMatch
        try:
            model_name = self.model.__name__.lower()
            context['delete_url'] = reverse(f'{model_name}-delete', kwargs={'pk': self.object.pk})
        except NoReverseMatch:
            pass
            
        return context

class BaseCatalogDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'biblioteca/generic_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.success_url
        context['title'] = f'Eliminar {self.model._meta.verbose_name}'
        context['subtitle'] = f'Esta acción eliminará permanentemente este registro del catálogo.'
        return context

    def post(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        self.object = self.get_object()
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(request, f"{self.model._meta.verbose_name} eliminado correctamente.")
            return response
        except ProtectedError:
            messages.error(request, f"No se puede eliminar este/a {self.model._meta.verbose_name.lower()} porque está asociado/a a otros registros del sistema.")
            return redirect(self.success_url)


# --- AUTOR CRUD ---
class AutorListView(BaseCatalogListView):
    model = Autor
    fields = ['id_autor', 'descripcion']
    headers = ['ID', 'Descripción']
    title = 'Autores'
    subtitle = 'Gestión de autores literarios del acervo'
    create_url_name = 'autor-create'
    edit_url_name = 'autor-update'

class AutorCreateView(BaseCatalogCreateView):
    model = Autor
    form_class = AutorForm
    success_url = reverse_lazy('autor-list')

class AutorUpdateView(BaseCatalogUpdateView):
    model = Autor
    form_class = AutorForm
    success_url = reverse_lazy('autor-list')

class AutorDeleteView(BaseCatalogDeleteView):
    model = Autor
    success_url = reverse_lazy('autor-list')


# --- EDITORIAL CRUD ---
class EditorialListView(BaseCatalogListView):
    model = Editorial
    fields = ['id_editorial', 'descripcion']
    headers = ['ID', 'Descripción']
    title = 'Editoriales'
    subtitle = 'Gestión de empresas editoras y proveedoras'
    create_url_name = 'editorial-create'
    edit_url_name = 'editorial-update'

class EditorialCreateView(BaseCatalogCreateView):
    model = Editorial
    form_class = EditorialForm
    success_url = reverse_lazy('editorial-list')

class EditorialUpdateView(BaseCatalogUpdateView):
    model = Editorial
    form_class = EditorialForm
    success_url = reverse_lazy('editorial-list')

class EditorialDeleteView(BaseCatalogDeleteView):
    model = Editorial
    success_url = reverse_lazy('editorial-list')


# --- CATEGORIA CRUD ---
class CategoriaListView(BaseCatalogListView):
    model = Categoria
    fields = ['id_categoria', 'descripcion']
    headers = ['ID', 'Descripción']
    title = 'Categorías'
    subtitle = 'Clasificación temática del acervo'
    create_url_name = 'categoria-create'
    edit_url_name = 'categoria-update'

class CategoriaCreateView(BaseCatalogCreateView):
    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy('categoria-list')

class CategoriaUpdateView(BaseCatalogUpdateView):
    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy('categoria-list')

class CategoriaDeleteView(BaseCatalogDeleteView):
    model = Categoria
    success_url = reverse_lazy('categoria-list')


# --- GENERO CRUD ---
class GeneroListView(BaseCatalogListView):
    model = Genero
    fields = ['id_genero', 'descripcion']
    headers = ['ID', 'Descripción']
    title = 'Géneros'
    subtitle = 'Géneros y estilos literarios asociados a las obras'
    create_url_name = 'genero-create'
    edit_url_name = 'genero-update'

class GeneroCreateView(BaseCatalogCreateView):
    model = Genero
    form_class = GeneroForm
    success_url = reverse_lazy('genero-list')

class GeneroUpdateView(BaseCatalogUpdateView):
    model = Genero
    form_class = GeneroForm
    success_url = reverse_lazy('genero-list')

class GeneroDeleteView(BaseCatalogDeleteView):
    model = Genero
    success_url = reverse_lazy('genero-list')


# --- TIPO DOCUMENTO CRUD ---
class TipoDocumentoListView(BaseCatalogListView):
    model = TipoDocumento
    fields = ['id_tipo', 'descripcion']
    headers = ['ID', 'Descripción']
    title = 'Tipos de Documento'
    subtitle = 'Formatos y soportes físicos/digitales'
    create_url_name = 'tipodocumento-create'
    edit_url_name = 'tipodocumento-update'

class TipoDocumentoCreateView(BaseCatalogCreateView):
    model = TipoDocumento
    form_class = TipoDocumentoForm
    success_url = reverse_lazy('tipodocumento-list')

class TipoDocumentoUpdateView(BaseCatalogUpdateView):
    model = TipoDocumento
    form_class = TipoDocumentoForm
    success_url = reverse_lazy('tipodocumento-list')

class TipoDocumentoDeleteView(BaseCatalogDeleteView):
    model = TipoDocumento
    success_url = reverse_lazy('tipodocumento-list')


# --- FACULTAD CRUD ---
class FacultadListView(BaseCatalogListView):
    model = Facultad
    fields = ['id_facultad', 'nombre']
    headers = ['ID', 'Nombre de la Facultad']
    title = 'Facultades'
    subtitle = 'Unidades académicas de la Universidad'
    create_url_name = 'facultad-create'
    edit_url_name = 'facultad-update'

class FacultadCreateView(BaseCatalogCreateView):
    model = Facultad
    form_class = FacultadForm
    success_url = reverse_lazy('facultad-list')

class FacultadUpdateView(BaseCatalogUpdateView):
    model = Facultad
    form_class = FacultadForm
    success_url = reverse_lazy('facultad-list')

class FacultadDeleteView(BaseCatalogDeleteView):
    model = Facultad
    success_url = reverse_lazy('facultad-list')


# --- CARRERA CRUD ---
class CarreraListView(BaseCatalogListView):
    model = Carrera
    fields = ['id_carrera', 'nombre', 'facultades_id_facultad']
    headers = ['ID', 'Carrera', 'Facultad']
    title = 'Carreras'
    subtitle = 'Programas académicos activos'
    create_url_name = 'carrera-create'
    edit_url_name = 'carrera-update'
    col_class = 'col-lg-9 col-md-11'

class CarreraCreateView(BaseCatalogCreateView):
    model = Carrera
    form_class = CarreraForm
    success_url = reverse_lazy('carrera-list')

class CarreraUpdateView(BaseCatalogUpdateView):
    model = Carrera
    form_class = CarreraForm
    success_url = reverse_lazy('carrera-list')

class CarreraDeleteView(BaseCatalogDeleteView):
    model = Carrera
    success_url = reverse_lazy('carrera-list')


class DevolucionListView(LoginRequiredMixin, ListView):
    model = Devolucion
    template_name = 'biblioteca/devolucion_list.html'
    context_object_name = 'devoluciones'

    def get_queryset(self):
        queryset = Devolucion.objects.all().select_related(
            'prestamos_id_prestamo__ALUMNOS_id_alumno', 
            'prestamos_id_prestamo__MATERIALES_id_material'
        ).order_by('-id_devolucion')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(id_devolucion__icontains=q) |
                Q(prestamos_id_prestamo__id_prestamo__icontains=q) |
                Q(prestamos_id_prestamo__ALUMNOS_id_alumno__nombre__icontains=q) |
                Q(prestamos_id_prestamo__ALUMNOS_id_alumno__apellido__icontains=q) |
                Q(prestamos_id_prestamo__ALUMNOS_id_alumno__matricula__icontains=q) |
                Q(prestamos_id_prestamo__MATERIALES_id_material__titulo__icontains=q) |
                Q(prestamos_id_prestamo__numero_entrada__icontains=q) |
                Q(estado_material__icontains=q) |
                Q(observaciones__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = ConfiguracionGeneral.get_solo()
        context['recargo_activo'] = config.recargo_activo
        return context

class DevolucionCreateView(LoginRequiredMixin, CreateView):
    model = Devolucion
    form_class = DevolucionForm
    template_name = 'biblioteca/devolucion_form.html'
    success_url = reverse_lazy('devolucion-list')

    def get_initial(self):
        initial = super().get_initial()
        prestamo_id = self.request.GET.get('prestamo')
        if prestamo_id:
            initial['prestamos_id_prestamo'] = prestamo_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Devolución'
        context['subtitle'] = 'Registra la devolución de un préstamo físico y calcula la multa si aplica'
        prestamos = Prestamo.objects.filter(estado__in=['ACTIVO', 'VENCIDO']).select_related('ALUMNOS_id_alumno', 'MATERIALES_id_material')
        context['prestamos_disponibles'] = prestamos
        
        import json
        prestamos_data = {}
        for p in prestamos:
            prestamos_data[p.id_prestamo] = {
                'vencimiento': p.fecha_vencimiento.strftime('%Y-%m-%d'),
                'alumno': f"{p.ALUMNOS_id_alumno.nombre} {p.ALUMNOS_id_alumno.apellido}",
                'material': p.MATERIALES_id_material.titulo
            }
        context['prestamos_json'] = json.dumps(prestamos_data)
        context['hoy'] = timezone.now().date().strftime('%Y-%m-%d')
        
        # Add dynamic configuration for Javascript
        config = ConfiguracionGeneral.get_solo()
        context['recargo_activo'] = config.recargo_activo
        context['monto_recargo'] = int(config.monto_recargo)
        return context


class ConfiguracionGeneralUpdateView(LoginRequiredMixin, UpdateView):
    model = ConfiguracionGeneral
    form_class = ConfiguracionGeneralForm
    template_name = 'biblioteca/configuracion_form.html'
    success_url = reverse_lazy('configuracion-general')

    def get_object(self, queryset=None):
        return ConfiguracionGeneral.get_solo()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Configuración General'
        context['subtitle'] = 'Configure los parámetros generales del sistema, incluyendo recargos y horarios de atención.'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Configuración guardada correctamente.")
        return super().form_valid(form)



# --- REPORTES ---
class ReportesView(LoginRequiredMixin, TemplateView):
    template_name = 'biblioteca/reportes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carreras'] = Carrera.objects.all().order_by('nombre')
        return context


class ReportePrintView(LoginRequiredMixin, TemplateView):
    template_name = 'biblioteca/reporte_print.html'

    def get_context_data(self, **kwargs):
        Prestamo.actualizar_vencidos()
        context = super().get_context_data(**kwargs)
        tipo = self.request.GET.get('tipo')
        carrera_id = self.request.GET.get('carrera')
        fecha_inicio_str = self.request.GET.get('fecha_inicio')
        fecha_fin_str = self.request.GET.get('fecha_fin')

        title = "Reporte"
        subtitle = ""
        headers = []
        rows = []
        
        from datetime import datetime
        now = datetime.now()
        months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        weekdays = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        
        wd = weekdays[now.weekday()]
        day = now.day
        month = months[now.month - 1]
        time_str = now.strftime('%H:%M')
        context['fecha_hora'] = f"{wd} {day} {month} {time_str}"

        if tipo == 'alumnos_alfa':
            title = "Reporte de Alumnos"
            subtitle = "Ordenados Alfabéticamente"
            headers = ["Matrícula/Cédula", "Nombre y Apellido", "Email", "Teléfono", "Carrera", "Estado"]
            alumnos = Alumno.objects.all().select_related('carreras_id_carrera').order_by('apellido', 'nombre')
            for a in alumnos:
                rows.append([
                    a.matricula,
                    f"{a.apellido}, {a.nombre}",
                    a.email,
                    a.telefono,
                    a.carreras_id_carrera.nombre,
                    "Activo" if a.estado else "Inactivo"
                ])
                
        elif tipo == 'alumnos_carrera':
            title = "Reporte de Alumnos"
            subtitle = "Por Carreras, Ordenados Alfabéticamente"
            carreras_list = Carrera.objects.all().order_by('nombre')
            grouped_data = []
            for c in carreras_list:
                alumnos = Alumno.objects.filter(carreras_id_carrera=c).order_by('apellido', 'nombre')
                if alumnos.exists():
                    grouped_data.append({
                        'carrera': c.nombre,
                        'alumnos': [
                            [
                                a.matricula,
                                f"{a.apellido}, {a.nombre}",
                                a.email,
                                a.telefono,
                                "Activo" if a.estado else "Inactivo"
                            ]
                            for a in alumnos
                        ]
                    })
            context['grouped_data'] = grouped_data
            context['is_grouped'] = True
            headers = ["Matrícula/Cédula", "Nombre y Apellido", "Email", "Teléfono", "Estado"]
            
        elif tipo == 'prestamos_rango':
            title = "Reporte de Préstamos"
            # Format dates to DD/MM/YYYY for title
            fi_formatted = ""
            ff_formatted = ""
            if fecha_inicio_str:
                try:
                    fi_dt = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                    fi_formatted = fi_dt.strftime('%d/%m/%Y')
                except ValueError:
                    fi_formatted = fecha_inicio_str
            if fecha_fin_str:
                try:
                    ff_dt = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
                    ff_formatted = ff_dt.strftime('%d/%m/%Y')
                except ValueError:
                    ff_formatted = fecha_fin_str

            subtitle = f"Según el Rango de Fecha ({fi_formatted} al {ff_formatted})"
            headers = ["ID", "Alumno", "Material", "Fecha Préstamo", "Fecha Vencimiento", "Estado"]
            
            prestamos = Prestamo.objects.filter(
                fecha_prestamo__range=[fecha_inicio_str, fecha_fin_str]
            ).select_related('ALUMNOS_id_alumno', 'MATERIALES_id_material').order_by('fecha_prestamo')
            
            for p in prestamos:
                rows.append([
                    p.id_prestamo,
                    f"{p.ALUMNOS_id_alumno.apellido}, {p.ALUMNOS_id_alumno.nombre}",
                    p.MATERIALES_id_material.titulo,
                    p.fecha_prestamo.strftime('%d/%m/%Y'),
                    p.fecha_vencimiento.strftime('%d/%m/%Y'),
                    p.get_estado_display()
                ])
                
        elif tipo == 'prestamos_pendientes':
            title = "Reporte de Préstamos Pendientes"
            subtitle = "Préstamos activos y vencidos a la fecha"
            headers = ["ID", "Alumno", "Material", "Fecha Préstamo", "Fecha Vencimiento", "Estado"]
            prestamos = Prestamo.objects.filter(estado__in=['ACTIVO', 'VENCIDO']).select_related('ALUMNOS_id_alumno', 'MATERIALES_id_material').order_by('fecha_vencimiento')
            for p in prestamos:
                rows.append([
                    p.id_prestamo,
                    f"{p.ALUMNOS_id_alumno.apellido}, {p.ALUMNOS_id_alumno.nombre}",
                    p.MATERIALES_id_material.titulo,
                    p.fecha_prestamo.strftime('%d/%m/%Y'),
                    p.fecha_vencimiento.strftime('%d/%m/%Y'),
                    p.get_estado_display()
                ])
                
        elif tipo == 'acervo_carrera':
            carrera = Carrera.objects.get(pk=carrera_id)
            title = "Acervo Bibliográfico"
            subtitle = f"Carrera: {carrera.nombre.upper()}"
            headers = ["Dewey", "Título", "Autor/es", "Año", "Edición"]
            
            materiales = Material.objects.filter(
                tipo_registro='LIBRO',
                carreras=carrera
            ).prefetch_related('autores_id_autor').order_by('numeracion_dewey', 'titulo')
            
            for m in materiales:
                autores_desc = ", ".join([a.descripcion for a in m.autores_id_autor.all()]) if m.autores_id_autor.exists() else "—"
                rows.append([
                    m.numeracion_dewey or "—",
                    m.titulo,
                    autores_desc,
                    m.año_publicacion or "—",
                    m.edicion or "—"
                ])
                
        elif tipo == 'investigacion_carrera':
            carrera = Carrera.objects.get(pk=carrera_id)
            title = "Materiales de Investigación"
            subtitle = f"Carrera: {carrera.nombre.upper()}"
            headers = ["N° Entrada", "Título", "Autor/es", "Título de Grado", "Tipo de Trabajo", "Año", "Estado"]
            
            materiales = Material.objects.filter(
                tipo_registro='TRABAJO_INVESTIGACION',
                carreras=carrera
            ).prefetch_related('autores_id_autor').order_by('titulo')
            
            for m in materiales:
                autores_desc = ", ".join([a.descripcion for a in m.autores_id_autor.all()]) if m.autores_id_autor.exists() else "—"
                rows.append([
                    m.numero_entrada or "—",
                    m.titulo,
                    autores_desc,
                    m.titulo_grado or "—",
                    m.tipo_trabajo or m.tipo_material or "—",
                    m.año_publicacion or "—",
                    m.estado_material
                ])

        context['title'] = title
        context['subtitle'] = subtitle
        context['headers'] = headers
        context['rows'] = rows
        context['tipo'] = tipo
        
        return context

