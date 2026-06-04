from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import (
    Material, Alumno, Prestamo, Autor, Editorial, Categoria, Genero,
    TipoDocumento, Facultad, Carrera, ConfiguracionGeneral, BajaMaterial,
    RegistroAuditoria
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
    paginate_by = 15

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
        context['materiales'] = queryset[:10]
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
        context['materiales'] = queryset[:10]
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


class MaterialDetailView(LoginRequiredMixin, DetailView):
    model = Material
    template_name = 'biblioteca/material_detail.html'
    context_object_name = 'material'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalles del Material'
        context['subtitle'] = f"Información completa sobre: {self.object.titulo}"
        # Obtener todas las bajas asociadas a este material
        context['bajas'] = self.object.bajamaterial_set.all().order_by('-fecha_baja')
        return context


class MaterialBajaCreateView(LoginRequiredMixin, CreateView):
    model = BajaMaterial
    fields = ['numero_entrada', 'cantidad', 'motivo', 'observaciones']
    template_name = 'biblioteca/material_baja_form.html'
    success_url = reverse_lazy('material-list')

    def dispatch(self, request, *args, **kwargs):
        self.material = get_object_or_404(Material, pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        from django import forms
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            if field_name == 'motivo':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

        disponibles = self.material.numeros_entrada_disponibles()
        if disponibles:
            form.fields['numero_entrada'] = forms.MultipleChoiceField(
                choices=[(n, f"N° {n}") for n in disponibles],
                required=True,
                label='Número(s) de Entrada',
                widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': min(len(disponibles), 5)})
            )
        else:
            form.fields['numero_entrada'].widget = forms.HiddenInput()
            form.fields['numero_entrada'].required = False
            
        form.fields['cantidad'].initial = 1
        form.fields['cantidad'].widget.attrs['min'] = 1
        return form

    def form_valid(self, form):
        form.instance.material = self.material
        cantidad = form.cleaned_data.get('cantidad') or 1
        
        if cantidad > self.material.cantidad_disponible:
            form.add_error('cantidad', f"No se puede dar de baja una cantidad mayor a la disponible en inventario. Stock disponible: {self.material.cantidad_disponible}")
            return self.form_invalid(form)
            
        numeros_entrada = form.cleaned_data.get('numero_entrada')
        disponibles = self.material.numeros_entrada_disponibles()
        
        if disponibles:
            if not numeros_entrada:
                form.add_error('numero_entrada', "Debe seleccionar los números de entrada correspondientes.")
                return self.form_invalid(form)
            if len(numeros_entrada) != cantidad:
                form.add_error('cantidad', f"La cantidad a dar de baja ({cantidad}) debe coincidir con el número de ejemplares seleccionados ({len(numeros_entrada)}).")
                return self.form_invalid(form)
            
            for ne in numeros_entrada:
                if ne not in disponibles:
                    form.add_error('numero_entrada', f"El número de entrada '{ne}' ya no se encuentra disponible.")
                    return self.form_invalid(form)
            
            form.instance.numero_entrada = ", ".join(numeros_entrada)
        else:
            form.instance.numero_entrada = None
            
        response = super().form_valid(form)
        messages.success(self.request, f"Se dio de baja {cantidad} copia(s) del material '{self.material.titulo}' exitosamente.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['material'] = self.material
        context['title'] = 'Dar de Baja Material'
        context['subtitle'] = f"Registrar la baja de una o más copias de: {self.material.titulo}"
        return context


# --- PRESTAMO CRUD ---
class PrestamoListView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'biblioteca/prestamo_list.html'
    context_object_name = 'prestamos'
    paginate_by = 15

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
        
        filtro = self.request.GET.get('filtro_estado')
        if filtro:
            if filtro == 'activo':
                queryset = queryset.filter(estado='ACTIVO')
            elif filtro == 'vencido':
                queryset = queryset.filter(estado='VENCIDO')
            elif filtro == 'devuelto':
                queryset = queryset.filter(estado='DEVUELTO')
        return queryset

class PrestamoCreateView(LoginRequiredMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'biblioteca/prestamo_form.html'
    success_url = reverse_lazy('prestamo-list')

    def form_valid(self, form):
        from django.core.exceptions import ValidationError
        form.instance.administrador_usuariosbibliosoft_id = self.request.user
        form.instance.fecha_vencimiento = timezone.localdate() + timezone.timedelta(days=2)
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materiales_json'] = {}
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
        context['materiales_json'] = {}
        return context


class PrestamoDetailView(LoginRequiredMixin, DetailView):
    model = Prestamo
    template_name = 'biblioteca/prestamo_detail.html'
    context_object_name = 'prestamo'


class PrestamoProrrogaView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        prestamo = Prestamo.objects.filter(pk=pk).first()
        if prestamo:
            if prestamo.estado in ['ACTIVO', 'VENCIDO']:
                prestamo.fecha_prestamo = timezone.localdate()
                prestamo.fecha_vencimiento = timezone.localdate() + timezone.timedelta(days=2)
                prestamo.estado = 'ACTIVO'
                prestamo.prorrogado = True
                prestamo._audit_prorroga = True
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
        obj = self.get_object()
        if obj.estado != 'ACTIVO':
            messages.error(request, "Solo se permite eliminar préstamos con estado Activo.")
            return redirect('prestamo-list')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.estado != 'ACTIVO':
            messages.error(request, "Solo se permite eliminar préstamos con estado Activo.")
            return redirect('prestamo-list')
        response = super().post(request, *args, **kwargs)
        messages.success(request, f"Préstamo #{obj.id_prestamo} eliminado correctamente y el stock fue restaurado.")
        return response

# --- ALUMNO CRUD ---
class AlumnoListView(LoginRequiredMixin, ListView):
    model = Alumno
    template_name = 'biblioteca/alumno_list.html'
    context_object_name = 'alumnos'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(apellido__icontains=q) |
                Q(matricula__icontains=q)
            )
        
        filtro = self.request.GET.get('filtro_carnet')
        if filtro:
            import datetime
            limit = timezone.localdate() - datetime.timedelta(days=365)
            if filtro == 'activo':
                queryset = queryset.filter(carnet_activo=True, carnet_fecha_entrega__gte=limit)
            elif filtro == 'sin_activar':
                queryset = queryset.filter(carnet_activo=False)
            elif filtro == 'expirado':
                queryset = queryset.filter(carnet_activo=True, carnet_fecha_entrega__lt=limit)
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
                    fecha_entrega = timezone.localdate()
            else:
                fecha_entrega = timezone.localdate()
            
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
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            from django.db.models import Q, CharField, TextField
            if self.model.__name__ == 'Autor':
                queryset = queryset.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q))
            elif self.model.__name__ == 'Editorial':
                queryset = queryset.filter(Q(nombre__icontains=q) | Q(direccion__icontains=q) | Q(telefono__icontains=q))
            else:
                query = Q()
                for field in self.model._meta.fields:
                    if isinstance(field, (CharField, TextField)):
                        query |= Q(**{f"{field.name}__icontains": q})
                queryset = queryset.filter(query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = []
        # Use paginated object_list instead of self.get_queryset()
        for obj in context.get('object_list', []):
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
    model = Prestamo
    template_name = 'biblioteca/devolucion_list.html'
    context_object_name = 'devoluciones'
    paginate_by = 15

    def get_queryset(self):
        queryset = Prestamo.objects.filter(estado='DEVUELTO').select_related(
            'ALUMNOS_id_alumno', 
            'MATERIALES_id_material'
        ).order_by('-fecha_devolucion')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(id_prestamo__icontains=q) |
                Q(ALUMNOS_id_alumno__nombre__icontains=q) |
                Q(ALUMNOS_id_alumno__apellido__icontains=q) |
                Q(ALUMNOS_id_alumno__matricula__icontains=q) |
                Q(MATERIALES_id_material__titulo__icontains=q) |
                Q(numero_entrada__icontains=q) |
                Q(estado_material__icontains=q) |
                Q(observaciones_devolucion__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = ConfiguracionGeneral.get_solo()
        context['recargo_activo'] = config.recargo_activo
        return context

class DevolucionCreateView(LoginRequiredMixin, FormView):
    form_class = DevolucionForm
    template_name = 'biblioteca/devolucion_form.html'
    success_url = reverse_lazy('prestamo-list')

    def dispatch(self, request, *args, **kwargs):
        prestamo_id = request.GET.get('prestamo') or request.POST.get('prestamos_id_prestamo')
        if not prestamo_id:
            messages.error(request, "Debe seleccionar un préstamo activo desde el listado de préstamos para registrar una devolución.")
            return redirect('prestamo-list')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        prestamo_id = self.request.GET.get('prestamo') or self.request.POST.get('prestamos_id_prestamo')
        if prestamo_id:
            initial['prestamos_id_prestamo'] = prestamo_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Devolución'
        context['subtitle'] = 'Registra la devolución de un préstamo físico y calcula la multa si aplica'
        context['prestamos_disponibles'] = Prestamo.objects.none()
        context['prestamos_json'] = "{}"
        context['hoy'] = timezone.localdate().strftime('%Y-%m-%d')
        
        prestamo_id = self.request.GET.get('prestamo') or self.request.POST.get('prestamos_id_prestamo')
        selected_prestamo = None
        if prestamo_id:
            try:
                selected_prestamo = Prestamo.objects.select_related('ALUMNOS_id_alumno', 'MATERIALES_id_material').get(pk=prestamo_id)
            except Prestamo.DoesNotExist:
                pass
        context['selected_prestamo'] = selected_prestamo
        
        # Add dynamic configuration for Javascript
        config = ConfiguracionGeneral.get_solo()
        context['recargo_activo'] = config.recargo_activo
        context['monto_recargo'] = int(config.monto_recargo)
        return context

    def form_valid(self, form):
        prestamo = form.cleaned_data['prestamos_id_prestamo']
        prestamo.estado = 'DEVUELTO'
        prestamo.fecha_devolucion = timezone.localdate()
        prestamo.estado_material = form.cleaned_data['estado_material']
        prestamo.multa = form.cleaned_data['multa'] or 0
        prestamo.pago_multa = form.cleaned_data['pago_multa'] or False
        prestamo.observaciones_devolucion = form.cleaned_data['observaciones'] or ''
        prestamo.save()
        
        messages.success(self.request, f"Se registró la devolución del material '{prestamo.MATERIALES_id_material.titulo}' con éxito.")
        
        # Registrar en auditoria
        RegistroAuditoria.objects.create(
            usuario=self.request.user,
            accion='MODIFICACION',
            tabla='Préstamo',
            registro_id=str(prestamo.pk),
            detalle=f"Devolución registrada para préstamo #{prestamo.pk}. Multa: {prestamo.multa}. ¿Pagó?: {'Sí' if prestamo.pago_multa else 'No'}.",
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        return redirect(self.success_url)


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
        now = timezone.localtime()
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
            carrera = None
            if carrera_id:
                if str(carrera_id).isdigit():
                    carrera = Carrera.objects.filter(pk=carrera_id).first()
                else:
                    carrera = Carrera.objects.filter(nombre__icontains=carrera_id).first()

            title = "Acervo Bibliográfico"
            headers = ["Dewey", "Título", "Autor/es", "Género/s", "Págs.", "Editorial", "Año", "Edición"]
            
            if carrera:
                subtitle = f"Carrera: {carrera.nombre.upper()}"
                materiales = Material.objects.filter(
                    tipo_registro='LIBRO',
                    carreras=carrera
                ).prefetch_related('autores_id_autor', 'generos').select_related('editoriales_id_editorial').order_by('numeracion_dewey', 'titulo')
                
                for m in materiales:
                    autores_desc = ", ".join([a.descripcion for a in m.autores_id_autor.all()]) if m.autores_id_autor.exists() else "—"
                    generos_desc = ", ".join([g.nombre for g in m.generos.all()]) if m.generos.exists() else "—"
                    editorial_desc = m.editoriales_id_editorial.nombre if m.editoriales_id_editorial else "—"
                    rows.append([
                        m.numeracion_dewey or "—",
                        m.titulo,
                        autores_desc,
                        generos_desc,
                        m.numero_paginas or "—",
                        editorial_desc,
                        m.año_publicacion or "—",
                        m.edicion or "—"
                    ])
            else:
                subtitle = f"Carrera: {carrera_id or 'No especificada'} (No se encontraron coincidencias)"
                rows = []
                
        elif tipo == 'investigacion_carrera':
            carrera = None
            if carrera_id:
                if str(carrera_id).isdigit():
                    carrera = Carrera.objects.filter(pk=carrera_id).first()
                else:
                    carrera = Carrera.objects.filter(nombre__icontains=carrera_id).first()

            title = "Materiales de Investigación"
            headers = ["Título", "Autor/es", "Título de Grado", "Tipo de Trabajo", "Año"]
            
            if carrera:
                subtitle = f"Carrera: {carrera.nombre.upper()}"
                materiales = Material.objects.filter(
                    tipo_registro='TRABAJO_INVESTIGACION',
                    carreras=carrera
                ).prefetch_related('autores_id_autor').order_by('titulo')
                
                for m in materiales:
                    autores_desc = ", ".join([a.descripcion for a in m.autores_id_autor.all()]) if m.autores_id_autor.exists() else "—"
                    rows.append([
                        m.titulo,
                        autores_desc,
                        m.titulo_grado or "—",
                        m.tipo_trabajo or m.tipo_material or "—",
                        m.año_publicacion or "—"
                    ])
            else:
                subtitle = f"Carrera: {carrera_id or 'No especificada'} (No se encontraron coincidencias)"
                rows = []

        context['title'] = title
        context['subtitle'] = subtitle
        context['headers'] = headers
        context['rows'] = rows
        context['tipo'] = tipo
        
        return context


class AuditoriaListView(LoginRequiredMixin, ListView):
    model = RegistroAuditoria
    template_name = 'biblioteca/auditoria_list.html'
    context_object_name = 'registros'
    paginate_by = 50

    def get_queryset(self):
        queryset = RegistroAuditoria.objects.all().select_related('usuario').order_by('-fecha_hora')
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(usuario__username__icontains=q) |
                Q(tabla__icontains=q) |
                Q(detalle__icontains=q) |
                Q(ip_address__icontains=q)
            )
            
        filtro_accion = self.request.GET.get('filtro_accion')
        if filtro_accion:
            queryset = queryset.filter(accion=filtro_accion)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Auditoría del Sistema'
        context['subtitle'] = 'Registro histórico de acciones, modificaciones y eventos de seguridad.'
        context['acciones_disponibles'] = RegistroAuditoria.ACCIONES
        return context


from django.http import JsonResponse

class BuscarOpcionesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        model_name = request.GET.get('model')
        q = request.GET.get('q', '').strip()
        
        results = []
        if model_name == 'autor':
            queryset = Autor.objects.all()
            if q:
                queryset = queryset.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q))
            results = [{'value': obj.pk, 'text': f"{obj.nombre} {obj.apellido}".strip()} for obj in queryset[:100]]
        elif model_name == 'editorial':
            queryset = Editorial.objects.all()
            if q:
                queryset = queryset.filter(nombre__icontains=q)
            results = [{'value': obj.pk, 'text': obj.nombre} for obj in queryset[:100]]
        elif model_name == 'carrera':
            queryset = Carrera.objects.all()
            if q:
                queryset = queryset.filter(nombre__icontains=q)
            results = [{'value': obj.pk, 'text': obj.nombre} for obj in queryset[:100]]
        elif model_name == 'genero':
            queryset = Genero.objects.all()
            if q:
                queryset = queryset.filter(nombre__icontains=q)
            results = [{'value': obj.pk, 'text': obj.nombre} for obj in queryset[:100]]
        elif model_name == 'tipodocumento':
            queryset = TipoDocumento.objects.all()
            if q:
                queryset = queryset.filter(descripcion__icontains=q)
            results = [{'value': obj.pk, 'text': obj.descripcion} for obj in queryset[:100]]
        elif model_name == 'alumno':
            queryset = Alumno.objects.filter(estado=True)
            if q:
                queryset = queryset.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(matricula__icontains=q))
            for obj in queryset.select_related('carreras_id_carrera')[:100]:
                cedula = obj.numero_documento or obj.matricula or ""
                results.append({
                    'value': obj.pk,
                    'text': f"{obj.nombre} {obj.apellido} (Cédula: {cedula}) - Carrera: {obj.carreras_id_carrera.nombre}"
                })
        elif model_name == 'material':
            queryset = Material.objects.filter(cantidad_disponible__gt=0)
            if q:
                queryset = queryset.filter(Q(titulo__icontains=q) | Q(isbn__icontains=q) | Q(numero_entrada__icontains=q))
            for obj in queryset.prefetch_related('autores_id_autor')[:100]:
                autores = obj.autores_id_autor.all()
                autor_desc = ", ".join([a.descripcion for a in autores]) if autores.exists() else "Sin autor"
                isbn_str = f" | ISBN: {obj.isbn}" if obj.isbn else ""
                entrada_str = f" | N° Entrada: {obj.numero_entrada}" if obj.numero_entrada else ""
                results.append({
                    'value': obj.pk,
                    'text': f"{obj.titulo} (Autor: {autor_desc}{isbn_str}{entrada_str}) - Disp: {obj.cantidad_disponible}"
                })
        elif model_name == 'prestamo':
            queryset = Prestamo.objects.filter(estado__in=['ACTIVO', 'VENCIDO']).select_related('ALUMNOS_id_alumno', 'MATERIALES_id_material')
            if q:
                queryset = queryset.filter(
                    Q(id_prestamo__icontains=q) |
                    Q(ALUMNOS_id_alumno__nombre__icontains=q) |
                    Q(ALUMNOS_id_alumno__apellido__icontains=q) |
                    Q(ALUMNOS_id_alumno__matricula__icontains=q) |
                    Q(MATERIALES_id_material__titulo__icontains=q) |
                    Q(numero_entrada__icontains=q)
                )
            for obj in queryset[:100]:
                cedula = obj.ALUMNOS_id_alumno.numero_documento or obj.ALUMNOS_id_alumno.matricula or ""
                entrada_str = f" [N° Entrada: {obj.numero_entrada}]" if obj.numero_entrada else ""
                results.append({
                    'value': obj.pk,
                    'text': f"Préstamo #{obj.id_prestamo} - Alumno: {obj.ALUMNOS_id_alumno.nombre} {obj.ALUMNOS_id_alumno.apellido} (Cédula: {cedula}) — Material: {obj.MATERIALES_id_material.titulo}{entrada_str} (Vence: {obj.fecha_vencimiento.strftime('%d/%m/%Y')})"
                })
        elif model_name == 'material_detalle':
            pk = request.GET.get('pk')
            if pk:
                try:
                    m = Material.objects.get(pk=pk)
                    exclude_prestamo_id = request.GET.get('exclude_prestamo_id')
                    disp = m.cantidad_disponible
                    if exclude_prestamo_id:
                        try:
                            p = Prestamo.objects.get(pk=exclude_prestamo_id)
                            if p.MATERIALES_id_material == m:
                                disp += 1
                        except Prestamo.DoesNotExist:
                            pass
                    return JsonResponse({
                        'numeros': m.numeros_entrada_disponibles(exclude_prestamo_id=exclude_prestamo_id),
                        'titulo': m.titulo,
                        'disponible': disp
                    })
                except Material.DoesNotExist:
                    pass
            return JsonResponse({}, status=404)
        elif model_name == 'prestamo_detalle':
            pk = request.GET.get('pk')
            if pk:
                try:
                    p = Prestamo.objects.select_related('ALUMNOS_id_alumno', 'MATERIALES_id_material').get(pk=pk)
                    return JsonResponse({
                        'vencimiento': p.fecha_vencimiento.strftime('%Y-%m-%d'),
                        'alumno': f"{p.ALUMNOS_id_alumno.nombre} {p.ALUMNOS_id_alumno.apellido}",
                        'material': p.MATERIALES_id_material.titulo
                    })
                except Prestamo.DoesNotExist:
                    pass
            return JsonResponse({}, status=404)
            
        return JsonResponse(results, safe=False)


