from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Material, Alumno, Prestamo, Autor, Editorial, Categoria, Genero,
    TipoDocumento, Facultad, Carrera, Devolucion, ConfiguracionGeneral
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

    def _optimize_queryset(self, field_name, model_class):
        if field_name not in self.fields:
            return
        
        if self.is_bound:
            if isinstance(self.fields[field_name], forms.ModelMultipleChoiceField):
                val_list = self.data.getlist(field_name)
            else:
                val_list = [self.data.get(field_name)]
            val_list = [v for v in val_list if v]
            if val_list:
                self.fields[field_name].queryset = model_class.objects.filter(pk__in=val_list)
            else:
                self.fields[field_name].queryset = model_class.objects.none()
        else:
            if self.instance and self.instance.pk:
                if isinstance(self.fields[field_name], forms.ModelMultipleChoiceField):
                    self.fields[field_name].queryset = getattr(self.instance, field_name).all()
                else:
                    val = getattr(self.instance, field_name)
                    if val:
                        self.fields[field_name].queryset = model_class.objects.filter(pk=val.pk)
                    else:
                        self.fields[field_name].queryset = model_class.objects.none()
            else:
                self.fields[field_name].queryset = model_class.objects.none()


class LibroForm(BootstrapModelForm):
    estado_material = forms.ChoiceField(
        choices=[
            ('Permanente', 'Permanente'),
            ('Disponible', 'Disponible'),
            ('Prestado', 'Prestado'),
            ('No Disponible', 'No Disponible')
        ],
        initial='Disponible',
        label='Estado'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('fecha_ingreso'):
            self.initial['fecha_ingreso'] = timezone.localdate()
        
        # Set fields as required based on visual mockup asterisks
        required_fields = [
            'año_publicacion', 'titulo', 'numeracion_dewey',
            'editoriales_id_editorial', 'numero_entrada', 'estado_material',
            'fecha_ingreso', 'autores_id_autor', 'carreras', 'generos', 'edicion',
            'cantidad_total'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
        
        self._optimize_queryset('autores_id_autor', Autor)
        self._optimize_queryset('editoriales_id_editorial', Editorial)
        self._optimize_queryset('carreras', Carrera)
        self._optimize_queryset('generos', Genero)

    def clean(self):
        cleaned_data = super().clean()
        cantidad_total = cleaned_data.get('cantidad_total')
        numero_entrada = cleaned_data.get('numero_entrada')

        if cantidad_total is not None and numero_entrada:
            import re
            def parse_entry_numbers(val):
                if not val:
                    return []
                parts = re.split(r'[,/;]', val)
                parts = [p.strip() for p in parts if p.strip()]
                return parts

            def count_entry_numbers(val):
                parts = parse_entry_numbers(val)
                total_count = 0
                for part in parts:
                    match = re.match(r'^(\d+)\s*-\s*(\d+)$', part)
                    if match:
                        start = int(match.group(1))
                        end = int(match.group(2))
                        if end >= start:
                            total_count += (end - start + 1)
                        else:
                            total_count += 1
                    else:
                        total_count += 1
                return total_count

            count = count_entry_numbers(numero_entrada)
            if cantidad_total > 1:
                if count > cantidad_total:
                    self.add_error('numero_entrada', f"El número de entradas ingresadas ({count}) supera la cantidad máxima de libros ({cantidad_total}).")
            else:
                if count > 1:
                    self.add_error('numero_entrada', f"Solo se permite 1 número de entrada cuando la cantidad de libros es 1.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not self.instance.pk:
            instance.cantidad_disponible = instance.cantidad_total
        else:
            original = Material.objects.get(pk=self.instance.pk)
            diff = instance.cantidad_total - original.cantidad_total
            instance.cantidad_disponible = max(0, original.cantidad_disponible + diff)
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Material
        fields = [
            'isbn', 'año_publicacion', 'titulo', 'numeracion_dewey',
            'editoriales_id_editorial', 'numero_entrada', 'estado_material',
            'fecha_ingreso', 'autores_id_autor', 'carreras', 'generos', 'edicion',
            'cantidad_total', 'numero_paginas'
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
            'cantidad_total': 'Cantidad',
            'numero_paginas': 'Número de Páginas',
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
            self.initial['fecha_ingreso'] = timezone.localdate()
        
        if self.instance.pk and self.instance.tipo_trabajo:
            tipo_doc = TipoDocumento.objects.filter(descripcion=self.instance.tipo_trabajo).first()
            if tipo_doc:
                self.initial['tipo_trabajo'] = tipo_doc.pk
        
        # Set fields as required based on visual mockup asterisks
        required_fields = [
            'titulo', 'titulo_grado', 'autores_id_autor',
            'carreras', 'año_publicacion', 'estado_material', 'fecha_ingreso',
            'numero_entrada', 'tipo_trabajo', 'cantidad_total'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        self._optimize_queryset('autores_id_autor', Autor)
        self._optimize_queryset('carreras', Carrera)
        self._optimize_queryset('tipo_trabajo', TipoDocumento)

    def clean(self):
        cleaned_data = super().clean()
        cantidad_total = cleaned_data.get('cantidad_total')
        numero_entrada = cleaned_data.get('numero_entrada')

        if cantidad_total is not None and numero_entrada:
            import re
            def parse_entry_numbers(val):
                if not val:
                    return []
                parts = re.split(r'[,/;]', val)
                parts = [p.strip() for p in parts if p.strip()]
                return parts

            def count_entry_numbers(val):
                parts = parse_entry_numbers(val)
                total_count = 0
                for part in parts:
                    match = re.match(r'^(\d+)\s*-\s*(\d+)$', part)
                    if match:
                        start = int(match.group(1))
                        end = int(match.group(2))
                        if end >= start:
                            total_count += (end - start + 1)
                        else:
                            total_count += 1
                    else:
                        total_count += 1
                return total_count

            count = count_entry_numbers(numero_entrada)
            if cantidad_total > 1:
                if count > cantidad_total:
                    self.add_error('numero_entrada', f"El número de entradas ingresadas ({count}) supera la cantidad máxima de materiales ({cantidad_total}).")
            else:
                if count > 1:
                    self.add_error('numero_entrada', f"Solo se permite 1 número de entrada cuando la cantidad de materiales es 1.")

        return cleaned_data



    def save(self, commit=True):
        instance = super().save(commit=False)
        tipo_doc = self.cleaned_data.get('tipo_trabajo')
        if tipo_doc:
            instance.tipo_trabajo = tipo_doc.descripcion
        else:
            instance.tipo_trabajo = ""
            
        if not self.instance.pk:
            instance.cantidad_disponible = instance.cantidad_total
        else:
            original = Material.objects.get(pk=self.instance.pk)
            diff = instance.cantidad_total - original.cantidad_total
            instance.cantidad_disponible = max(0, original.cantidad_disponible + diff)
            
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Material
        fields = [
            'titulo', 'titulo_grado', 'autores_id_autor',
            'carreras', 'año_publicacion', 'estado_material', 'fecha_ingreso',
            'numero_entrada', 'tipo_trabajo', 'cantidad_total'
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
            'cantidad_total': 'Cantidad',
        }

class OtrosMaterialesForm(BootstrapModelForm):
    estado_material = forms.ChoiceField(
        choices=[
            ('Permanente', 'Permanente'),
            ('Disponible', 'Disponible'),
            ('Prestado', 'Prestado'),
            ('No Disponible', 'No Disponible')
        ],
        initial='Disponible',
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
            self.initial['fecha_ingreso'] = timezone.localdate()

        if self.instance.pk and self.instance.tipo_material:
            tipo_doc = TipoDocumento.objects.filter(descripcion=self.instance.tipo_material).first()
            if tipo_doc:
                self.initial['tipo_material'] = tipo_doc.pk

        # Set fields as required based on visual mockup asterisks
        required_fields = [
            'titulo', 'año_publicacion',
            'numero_entrada', 'estado_material', 'fecha_ingreso', 'tipo_material', 'cantidad_total'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        self._optimize_queryset('tipo_material', TipoDocumento)

    def clean(self):
        cleaned_data = super().clean()
        cantidad_total = cleaned_data.get('cantidad_total')
        numero_entrada = cleaned_data.get('numero_entrada')

        if cantidad_total is not None and numero_entrada:
            import re
            def parse_entry_numbers(val):
                if not val:
                    return []
                parts = re.split(r'[,/;]', val)
                parts = [p.strip() for p in parts if p.strip()]
                return parts

            def count_entry_numbers(val):
                parts = parse_entry_numbers(val)
                total_count = 0
                for part in parts:
                    match = re.match(r'^(\d+)\s*-\s*(\d+)$', part)
                    if match:
                        start = int(match.group(1))
                        end = int(match.group(2))
                        if end >= start:
                            total_count += (end - start + 1)
                        else:
                            total_count += 1
                    else:
                        total_count += 1
                return total_count

            count = count_entry_numbers(numero_entrada)
            if cantidad_total > 1:
                if count > cantidad_total:
                    self.add_error('numero_entrada', f"El número de entradas ingresadas ({count}) supera la cantidad máxima de materiales ({cantidad_total}).")
            else:
                if count > 1:
                    self.add_error('numero_entrada', f"Solo se permite 1 número de entrada cuando la cantidad de materiales es 1.")

        return cleaned_data



    def save(self, commit=True):
        instance = super().save(commit=False)
        tipo_doc = self.cleaned_data.get('tipo_material')
        if tipo_doc:
            instance.tipo_material = tipo_doc.descripcion
        else:
            instance.tipo_material = ""
            
        if not self.instance.pk:
            instance.cantidad_disponible = instance.cantidad_total
        else:
            original = Material.objects.get(pk=self.instance.pk)
            diff = instance.cantidad_total - original.cantidad_total
            instance.cantidad_disponible = max(0, original.cantidad_disponible + diff)
            
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Material
        fields = [
            'issn', 'titulo', 'año_publicacion',
            'numero_entrada', 'estado_material', 'fecha_ingreso', 'tipo_material', 'cantidad_total'
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
            'cantidad_total': 'Cantidad',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._optimize_queryset('carreras_id_carrera', Carrera)

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
        cedula = obj.numero_documento or obj.matricula or ""
        return f"{obj.nombre} {obj.apellido} (Cédula: {cedula}) - Carrera: {obj.carreras_id_carrera.nombre}"

class MaterialModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        autores = obj.autores_id_autor.all()
        autor_desc = ", ".join([a.descripcion for a in autores]) if autores.exists() else "Sin autor"
        isbn_str = f" | ISBN: {obj.isbn}" if obj.isbn else ""
        entrada_str = f" | N° Entrada: {obj.numero_entrada}" if obj.numero_entrada else ""
        return f"{obj.titulo} (Autor: {autor_desc}{isbn_str}{entrada_str}) - Disp: {obj.cantidad_disponible}"

class PrestamoForm(BootstrapModelForm):
    ALUMNOS_id_alumno = AlumnoModelChoiceField(
        queryset=Alumno.objects.none(),
        label='Alumno'
    )
    MATERIALES_id_material = MaterialModelChoiceField(
        queryset=Material.objects.none(),
        label='Material'
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Cantidad a prestar'
    )
    numero_entrada = forms.MultipleChoiceField(
        required=False,
        label='Número de Entrada',
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Prestamo
        fields = ['ALUMNOS_id_alumno', 'MATERIALES_id_material', 'cantidad', 'numero_entrada']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Optimize querysets
        self._optimize_queryset('ALUMNOS_id_alumno', Alumno)
        self._optimize_queryset('MATERIALES_id_material', Material)
        
        # Set required fields
        if 'cantidad' in self.fields:
            self.fields['cantidad'].required = True
            
        material_id = None
        if self.is_bound:
            material_id = self.data.get('MATERIALES_id_material')
        elif self.instance and self.instance.pk:
            material_id = self.instance.MATERIALES_id_material_id
            
        if material_id:
            try:
                m = Material.objects.get(pk=material_id)
                disponibles = m.numeros_entrada_disponibles(exclude_prestamo_id=self.instance.pk if self.instance and self.instance.pk else None)
                
                current_nes = []
                if self.instance and self.instance.pk and self.instance.MATERIALES_id_material_id == m.pk:
                    current_ne = self.instance.numero_entrada
                    current_nes = [x.strip() for x in current_ne.split(',') if x.strip()] if current_ne else []
                
                choices = []
                # Include currently selected ones
                for c_ne in current_nes:
                    choices.append((c_ne, c_ne))
                # Add available ones
                for n in disponibles:
                    if n not in current_nes:
                        choices.append((n, n))
                        
                self.fields['numero_entrada'].choices = choices
                if not self.is_bound:
                    self.initial['numero_entrada'] = current_nes
            except Material.DoesNotExist:
                self.fields['numero_entrada'].choices = []
        else:
            self.fields['numero_entrada'].choices = []

    def clean(self):
        cleaned_data = super().clean()
        alumno = cleaned_data.get('ALUMNOS_id_alumno')
        material = cleaned_data.get('MATERIALES_id_material')
        cantidad = cleaned_data.get('cantidad')
        ne_list = cleaned_data.get('numero_entrada')

        if alumno:
            if not alumno.carnet_activo:
                self.add_error('ALUMNOS_id_alumno', "El alumno no tiene un carnet activo.")
            elif alumno.carnet_expirado:
                self.add_error('ALUMNOS_id_alumno', "El carnet del alumno está expirado. Debe ser reactivado.")

        if material:
            disp = material.cantidad_disponible
            if self.instance and self.instance.pk:
                if self.instance.MATERIALES_id_material == material:
                    disp += self.instance.cantidad

            if cantidad and cantidad > disp:
                self.add_error('cantidad', f"No hay stock suficiente. Máximo disponible: {disp}.")

            total_numeros = material.lista_numeros_entrada
            if total_numeros:
                if not ne_list:
                    self.add_error('numero_entrada', "Este material requiere seleccionar al menos un número de entrada.")
                else:
                    if cantidad and len(ne_list) != cantidad:
                        self.add_error('numero_entrada', f"Debe seleccionar exactamente {cantidad} número(s) de entrada para la cantidad ingresada.")
                    
                    disponibles = material.numeros_entrada_disponibles(exclude_prestamo_id=self.instance.pk)
                    current_ne = getattr(self.instance, 'numero_entrada', None)
                    current_nes = [x.strip() for x in current_ne.split(',') if x.strip()] if current_ne else []
                    
                    for ne in ne_list:
                        if ne not in disponibles and ne not in current_nes:
                            self.add_error('numero_entrada', f"El número de entrada '{ne}' ya se encuentra prestado o no existe.")
                            
        # Convert list to comma-separated string for saving to CharField
        if isinstance(ne_list, list):
            cleaned_data['numero_entrada'] = ", ".join(ne_list)
            
        return cleaned_data

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
        cedula = obj.ALUMNOS_id_alumno.numero_documento or obj.ALUMNOS_id_alumno.matricula or ""
        entrada_str = f" [N° Entrada: {obj.numero_entrada}]" if obj.numero_entrada else ""
        return f"Préstamo #{obj.id_prestamo} - Alumno: {obj.ALUMNOS_id_alumno.nombre} {obj.ALUMNOS_id_alumno.apellido} (Cédula: {cedula}) — Material: {obj.MATERIALES_id_material.titulo}{entrada_str} (Vence: {obj.fecha_vencimiento.strftime('%d/%m/%Y')})"

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
        self._optimize_queryset('prestamos_id_prestamo', Prestamo)


class ConfiguracionGeneralForm(BootstrapModelForm):
    class Meta:
        model = ConfiguracionGeneral
        fields = [
            'monto_recargo', 'recargo_activo', 
            'horario_lunes_viernes', 'abren_sabados', 'horario_sabados'
        ]
        labels = {
            'monto_recargo': 'Monto del recargo por día (Gs)',
            'recargo_activo': '¿El recargo está activo?',
            'horario_lunes_viernes': 'Horario de atención Lunes a Viernes',
            'abren_sabados': '¿Abren los Sábados?',
            'horario_sabados': 'Horario de atención Sábados',
        }


