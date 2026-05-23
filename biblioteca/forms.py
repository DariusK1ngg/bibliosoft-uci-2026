from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Material, Alumno, Prestamo, Autor, Editorial, Categoria, Genero,
    TipoDocumento, Facultad, Carrera, Devolucion
)

class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Change default "---------" empty label to empty string for clean placeholders
            if isinstance(field, forms.ModelChoiceField) and hasattr(field, 'empty_label'):
                if isinstance(field, forms.ModelMultipleChoiceField):
                    field.empty_label = None
                else:
                    field.empty_label = ""

            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'


class LibroForm(BootstrapModelForm):
    estado_material = forms.ChoiceField(
        choices=[
            ('Permanente', 'Permanente'),
            ('Disponible', 'Disponible'),
            ('Prestado', 'Prestado'),
            ('No Disponible', 'No Disponible')
        ],
        initial='Permanente',
        label='Estado'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('fecha_ingreso'):
            self.initial['fecha_ingreso'] = timezone.now().date()
        
        # Set fields as required based on visual mockup asterisks
        required_fields = [
            'año_publicacion', 'titulo', 'numeracion_dewey',
            'editoriales_id_editorial', 'numero_entrada', 'estado_material',
            'fecha_ingreso', 'autores_id_autor', 'carreras', 'generos', 'edicion'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True



    class Meta:
        model = Material
        fields = [
            'isbn', 'año_publicacion', 'titulo', 'numeracion_dewey',
            'editoriales_id_editorial', 'numero_entrada', 'estado_material',
            'fecha_ingreso', 'autores_id_autor', 'carreras', 'generos', 'edicion'
        ]
        widgets = {
            'fecha_ingreso': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }
        labels = {
            'isbn': 'ISBN',
            'año_publicacion': 'Año de Publicación',
            'titulo': 'Título',
            'numeracion_dewey': 'Numeración Dewey',
            'editoriales_id_editorial': 'Editorial',
            'numero_entrada': 'Número de Entrada',
            'estado_material': 'Estado',
            'fecha_ingreso': 'Fecha de Ingreso',
            'autores_id_autor': 'Autor/es',
            'carreras': 'Carrera/s',
            'generos': 'Género/s',
            'edicion': 'Edición',
        }

class TrabajoInvestigacionForm(BootstrapModelForm):
    estado_material = forms.ChoiceField(
        choices=[
            ('Permanente', 'Permanente'),
            ('Disponible', 'Disponible'),
            ('Prestado', 'Prestado'),
            ('No Disponible', 'No Disponible')
        ],
        initial='Permanente',
        label='Estado'
    )
    tipo_trabajo = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.all(),
        label='Tipo de Trabajo',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('fecha_ingreso'):
            self.initial['fecha_ingreso'] = timezone.now().date()
        
        if self.instance.pk and self.instance.tipo_trabajo:
            tipo_doc = TipoDocumento.objects.filter(descripcion=self.instance.tipo_trabajo).first()
            if tipo_doc:
                self.initial['tipo_trabajo'] = tipo_doc.pk
        
        # Set fields as required based on visual mockup asterisks
        required_fields = [
            'titulo', 'titulo_grado', 'autores_id_autor',
            'carreras', 'año_publicacion', 'estado_material', 'fecha_ingreso',
            'numero_entrada', 'tipo_trabajo'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True



    def save(self, commit=True):
        instance = super().save(commit=False)
        tipo_doc = self.cleaned_data.get('tipo_trabajo')
        if tipo_doc:
            instance.tipo_trabajo = tipo_doc.descripcion
        else:
            instance.tipo_trabajo = ""
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Material
        fields = [
            'titulo', 'titulo_grado', 'autores_id_autor',
            'carreras', 'año_publicacion', 'estado_material', 'fecha_ingreso',
            'numero_entrada', 'tipo_trabajo'
        ]
        widgets = {
            'fecha_ingreso': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }
        labels = {
            'titulo': 'Título',
            'titulo_grado': 'Título de Grado',
            'autores_id_autor': 'Autor/es',
            'carreras': 'Carrera',
            'año_publicacion': 'Año de Elaboración',
            'estado_material': 'Estado',
            'fecha_ingreso': 'Fecha de Ingreso',
            'numero_entrada': 'Número de Entrada',
            'tipo_trabajo': 'Tipo de Trabajo',
        }

class OtrosMaterialesForm(BootstrapModelForm):
    estado_material = forms.ChoiceField(
        choices=[
            ('Permanente', 'Permanente'),
            ('Disponible', 'Disponible'),
            ('Prestado', 'Prestado'),
            ('No Disponible', 'No Disponible')
        ],
        initial='Permanente',
        label='Estado'
    )
    tipo_material = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.all(),
        label='Tipo de Material',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('fecha_ingreso'):
            self.initial['fecha_ingreso'] = timezone.now().date()

        if self.instance.pk and self.instance.tipo_material:
            tipo_doc = TipoDocumento.objects.filter(descripcion=self.instance.tipo_material).first()
            if tipo_doc:
                self.initial['tipo_material'] = tipo_doc.pk

        # Set fields as required based on visual mockup asterisks
        required_fields = [
            'titulo', 'año_publicacion',
            'numero_entrada', 'estado_material', 'fecha_ingreso', 'tipo_material'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True



    def save(self, commit=True):
        instance = super().save(commit=False)
        tipo_doc = self.cleaned_data.get('tipo_material')
        if tipo_doc:
            instance.tipo_material = tipo_doc.descripcion
        else:
            instance.tipo_material = ""
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Material
        fields = [
            'issn', 'titulo', 'año_publicacion',
            'numero_entrada', 'estado_material', 'fecha_ingreso', 'tipo_material'
        ]
        widgets = {
            'fecha_ingreso': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }
        labels = {
            'issn': 'ISSN',
            'titulo': 'Título',
            'año_publicacion': 'Año de Publicación',
            'numero_entrada': 'Número de Entrada',
            'estado_material': 'Estado',
            'fecha_ingreso': 'Fecha de Ingreso',
            'tipo_material': 'Tipo de Material',
        }


class AlumnoForm(BootstrapModelForm):
    tipo_documento = forms.ChoiceField(
        choices=[('CI', 'CI'), ('DNI', 'DNI')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='CI',
        label='Tipo de Documento'
    )
    nacionalidad = forms.ChoiceField(
        choices=[
            ('Paraguaya', 'Paraguaya'),
            ('Argentina', 'Argentina'),
            ('Brasilera', 'Brasilera'),
            ('Otros', 'Otros')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='Paraguaya',
        label='Nacionalidad'
    )

    class Meta:
        model = Alumno
        fields = [
            'apellido', 'nombre', 'tipo_documento', 'numero_documento', 
            'nacionalidad', 'nacionalidad_otros', 'direccion_actual', 
            'ciudad', 'ciudad_origen', 'direccion', 'departamento',
            'celular', 'email', 'otros_numeros', 'carreras_id_carrera', 
            'curso', 'numero_matricula', 'lector_numero', 'estado'
        ]
        labels = {
            'apellido': 'Apellidos',
            'nombre': 'Nombres',
            'numero_documento': 'Número de Documento',
            'nacionalidad_otros': 'Otros (Especifique)',
            'direccion_actual': 'Actual (Barrio y nombre de Calle)',
            'ciudad': 'Ciudad',
            'ciudad_origen': 'Ciudad de Origen',
            'direccion': 'Dirección',
            'departamento': 'Departamento',
            'celular': 'Número de celular',
            'email': 'Correo electrónico',
            'otros_numeros': 'Otros números',
            'carreras_id_carrera': 'Carrera',
            'curso': 'Curso',
            'numero_matricula': 'Número de Matrícula',
            'lector_numero': 'Lector N°',
            'estado': 'Estado Activo'
        }

    def clean(self):
        cleaned_data = super().clean()
        num_doc = cleaned_data.get('numero_documento')
        if num_doc:
            self.instance.matricula = num_doc
            
        celular = cleaned_data.get('celular')
        if celular:
            self.instance.telefono = celular
            
        nac = cleaned_data.get('nacionalidad')
        if nac == 'Otros':
            nac_otros = cleaned_data.get('nacionalidad_otros')
            if nac_otros:
                self.instance.nacionalidad = nac_otros
                
        return cleaned_data

class AlumnoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.nombre} {obj.apellido} ({obj.matricula})"

class MaterialModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        autores = obj.autores_id_autor.all()
        autor_desc = ", ".join([a.descripcion for a in autores]) if autores.exists() else "Sin autor"
        return f"{obj.titulo} (Autor: {autor_desc}) - Disponible: {obj.cantidad_disponible}"

class PrestamoForm(BootstrapModelForm):
    ALUMNOS_id_alumno = AlumnoModelChoiceField(
        queryset=Alumno.objects.none(),
        label='Alumno'
    )
    MATERIALES_id_material = MaterialModelChoiceField(
        queryset=Material.objects.none(),
        label='Material'
    )

    class Meta:
        model = Prestamo
        fields = ['ALUMNOS_id_alumno', 'MATERIALES_id_material']

    def __init__(self, *args, **kwargs):
        from django.db.models import Q
        super().__init__(*args, **kwargs)
        self.fields['ALUMNOS_id_alumno'].queryset = Alumno.objects.filter(estado=True)
        if self.instance and self.instance.pk:
            self.fields['MATERIALES_id_material'].queryset = Material.objects.filter(
                Q(cantidad_disponible__gt=0) | Q(pk=self.instance.MATERIALES_id_material.pk)
            )
        else:
            self.fields['MATERIALES_id_material'].queryset = Material.objects.filter(cantidad_disponible__gt=0)

    def clean_MATERIALES_id_material(self):
        material = self.cleaned_data.get('MATERIALES_id_material')
        if not self.instance.pk:
            if material and material.cantidad_disponible <= 0:
                raise forms.ValidationError("No hay stock disponible para este material.")
        return material

class UserProfileForm(BootstrapModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre(s)',
            'last_name': 'Apellido(s)',
            'email': 'Correo Electrónico',
        }

class AutorForm(BootstrapModelForm):
    descripcion = forms.CharField(label='Descripción', max_length=200)

    class Meta:
        model = Autor
        fields = ['descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['descripcion'] = f"{self.instance.nombre} {self.instance.apellido}".strip()

    def save(self, commit=True):
        instance = super().save(commit=False)
        desc = self.cleaned_data.get('descripcion', '').strip()
        parts = desc.split(' ', 1)
        if len(parts) > 1:
            instance.nombre = parts[0]
            instance.apellido = parts[1]
        else:
            instance.nombre = desc
            instance.apellido = ""
        if commit:
            instance.save()
        return instance

class EditorialForm(BootstrapModelForm):
    descripcion = forms.CharField(label='Descripción', max_length=100)

    class Meta:
        model = Editorial
        fields = ['descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['descripcion'] = self.instance.nombre

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.nombre = self.cleaned_data.get('descripcion')
        if not instance.direccion:
            instance.direccion = "—"
        if not instance.telefono:
            instance.telefono = "—"
        if commit:
            instance.save()
        return instance

class CategoriaForm(BootstrapModelForm):
    descripcion = forms.CharField(label='Descripción', widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Categoria
        fields = ['descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['descripcion'] = self.instance.descripcion

    def save(self, commit=True):
        instance = super().save(commit=False)
        desc = self.cleaned_data.get('descripcion')
        instance.descripcion = desc
        instance.nombre = desc[:100]
        if commit:
            instance.save()
        return instance

class GeneroForm(BootstrapModelForm):
    class Meta:
        model = Genero
        fields = ['nombre']
        labels = {
            'nombre': 'Descripción',
        }

class TipoDocumentoForm(BootstrapModelForm):
    class Meta:
        model = TipoDocumento
        fields = '__all__'

class FacultadForm(BootstrapModelForm):
    class Meta:
        model = Facultad
        fields = '__all__'

class CarreraForm(BootstrapModelForm):
    class Meta:
        model = Carrera
        fields = '__all__'

class PrestamoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"Préstamo #{obj.id_prestamo} - {obj.ALUMNOS_id_alumno.nombre} {obj.ALUMNOS_id_alumno.apellido} — {obj.MATERIALES_id_material.titulo} (Vence: {obj.fecha_vencimiento.strftime('%d/%m/%Y')})"

class DevolucionForm(BootstrapModelForm):
    prestamos_id_prestamo = PrestamoModelChoiceField(
        queryset=Prestamo.objects.none(),
        label='Préstamo'
    )
    multa = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'readonly': 'readonly', 'id': 'id_multa'})
    )
    pago_multa = forms.BooleanField(
        required=False,
        label='¿Se pagó la multa?',
        widget=forms.CheckboxInput(attrs={'id': 'id_pago_multa'})
    )
    estado_material = forms.ChoiceField(
        choices=[('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo')],
        initial='BUENO',
        label='Estado del Material',
        widget=forms.Select(attrs={'id': 'id_estado_material'})
    )

    class Meta:
        model = Devolucion
        fields = ['prestamos_id_prestamo', 'estado_material', 'multa', 'pago_multa', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prestamos_id_prestamo'].queryset = Prestamo.objects.filter(
            estado__in=['ACTIVO', 'VENCIDO']
        ).select_related('ALUMNOS_id_alumno', 'MATERIALES_id_material')

