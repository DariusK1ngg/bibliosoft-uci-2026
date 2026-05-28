from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# 1. Parámetros Base
class Autor(models.Model):
    id_autor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')

    class Meta:
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def descripcion(self):
        return f"{self.nombre} {self.apellido}".strip()

class Editorial(models.Model):
    id_editorial = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    direccion = models.CharField(max_length=200, verbose_name='Dirección')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')

    class Meta:
        verbose_name = 'Editorial'
        verbose_name_plural = 'Editoriales'

    def __str__(self):
        return self.nombre

    @property
    def descripcion(self):
        return self.nombre

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre

class Genero(models.Model):
    id_genero = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'

    def __str__(self):
        return self.nombre

    @property
    def descripcion(self):
        return self.nombre

class TipoDocumento(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, verbose_name='Descripción')

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'

    def __str__(self):
        return self.descripcion


# 2. Organización Académica
class Facultad(models.Model):
    id_facultad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Facultad'
        verbose_name_plural = 'Facultades'

    def __str__(self):
        return self.nombre

class Carrera(models.Model):
    id_carrera = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    facultades_id_facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT, db_column='facultades_id_facultad', verbose_name='Facultad')

    class Meta:
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'

    def __str__(self):
        return self.nombre


# 3. Usuarios del Sistema
class Alumno(models.Model):
    id_alumno = models.AutoField(primary_key=True)
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula/Cédula')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    email = models.EmailField(verbose_name='Email')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    carreras_id_carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, db_column='carreras_id_carrera', verbose_name='Carrera')
    estado = models.BooleanField(default=True, verbose_name='Estado')

    # Nuevos campos del formulario físico
    tipo_documento = models.CharField(max_length=10, choices=[('CI', 'CI'), ('DNI', 'DNI')], default='CI', null=True, blank=True, verbose_name='Tipo de Documento')
    numero_documento = models.CharField(max_length=50, null=True, blank=True, verbose_name='Número de Documento')
    nacionalidad = models.CharField(max_length=50, default='Paraguaya', null=True, blank=True, verbose_name='Nacionalidad')
    nacionalidad_otros = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nacionalidad (Otros)')
    
    direccion_actual = models.CharField(max_length=255, null=True, blank=True, verbose_name='Actual (Barrio y nombre de Calle)')
    ciudad = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ciudad')
    ciudad_origen = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ciudad de Origen')
    direccion = models.CharField(max_length=255, null=True, blank=True, verbose_name='Dirección')
    departamento = models.CharField(max_length=100, null=True, blank=True, verbose_name='Departamento')
    
    celular = models.CharField(max_length=50, null=True, blank=True, verbose_name='Número de celular')
    otros_numeros = models.CharField(max_length=100, null=True, blank=True, verbose_name='Otros números')

    # Campos académicos adicionales y carnet
    curso = models.CharField(max_length=100, null=True, blank=True, verbose_name='Curso')
    numero_matricula = models.CharField(max_length=50, null=True, blank=True, verbose_name='Número de Matrícula')
    lector_numero = models.CharField(max_length=50, null=True, blank=True, verbose_name='Lector N°')
    carnet_activo = models.BooleanField(default=False, verbose_name='Carnet Activo')
    carnet_fecha_entrega = models.DateField(null=True, blank=True, verbose_name='Fecha de Entrega del Carnet')

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __str__(self):
        return f"{self.matricula} - {self.nombre} {self.apellido}"

    @property
    def tiene_prestamos(self):
        return self.prestamo_set.exists()

    def save(self, *args, **kwargs):
        # Sincronizar matricula con numero_documento
        if not self.matricula and self.numero_documento:
            self.matricula = self.numero_documento
        elif self.matricula and not self.numero_documento:
            self.numero_documento = self.matricula
            
        # Sincronizar telefono con celular
        if self.celular:
            self.telefono = self.celular
        elif self.telefono and not self.celular:
            self.celular = self.telefono
            
        super().save(*args, **kwargs)


# 4. Inventario (Acervo Bibliográfico)
class Material(models.Model):
    id_material = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200, verbose_name='Título')
    autores_id_autor = models.ManyToManyField(Autor, blank=True, verbose_name='Autor/es')
    editoriales_id_editorial = models.ForeignKey(Editorial, on_delete=models.SET_NULL, null=True, blank=True, db_column='editoriales_id_editorial', verbose_name='Editorial')
    categorias_id_categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='categorias_id_categoria', verbose_name='Categoría')
    tipodocumento_id_tipo = models.ForeignKey(TipoDocumento, on_delete=models.SET_NULL, null=True, blank=True, db_column='tipodocumento_id_tipo', verbose_name='Tipo de Documento')
    
    # M:M
    carreras = models.ManyToManyField(Carrera, through='MaterialCarrera', verbose_name='Carreras Asociadas')
    generos = models.ManyToManyField(Genero, through='MaterialGenero', verbose_name='Géneros')

    isbn = models.CharField(max_length=20, null=True, blank=True, verbose_name='ISBN')
    issn = models.CharField(max_length=20, null=True, blank=True, verbose_name='ISSN')
    año_publicacion = models.IntegerField(null=True, blank=True, verbose_name='Año de Publicación')
    cantidad_total = models.IntegerField(default=1, verbose_name='Cantidad Total')
    cantidad_disponible = models.IntegerField(default=1, verbose_name='Cantidad Disponible')
    ubicacion_fisica = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ubicación Física')

    # Nuevos campos solicitados
    numeracion_dewey = models.CharField(max_length=50, null=True, blank=True, verbose_name='Numeración Dewey')
    numero_entrada = models.CharField(max_length=50, null=True, blank=True, verbose_name='Número de Entrada')
    estado_material = models.CharField(max_length=50, default='DISPONIBLE', verbose_name='Estado')
    fecha_ingreso = models.DateField(null=True, blank=True, verbose_name='Fecha de Ingreso')
    edicion = models.CharField(max_length=50, null=True, blank=True, verbose_name='Edición')
    numero_paginas = models.IntegerField(null=True, blank=True, verbose_name='Número de Páginas')
    descripcion = models.TextField(null=True, blank=True, verbose_name='Descripción')
    titulo_grado = models.CharField(max_length=100, null=True, blank=True, verbose_name='Título de Grado')
    tipo_trabajo = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tipo de Trabajo')
    tipo_material = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tipo de Material')
    tipo_registro = models.CharField(max_length=50, choices=[('LIBRO', 'Libro'), ('TRABAJO_INVESTIGACION', 'Trabajo de Investigación'), ('OTROS', 'Otros Materiales')], default='LIBRO', verbose_name='Tipo de Registro')

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'

    def __str__(self):
        return self.titulo

    @property
    def tiene_prestamos(self):
        return self.prestamo_set.exists()

    @property
    def tipo_documento(self):
        return self.tipodocumento_id_tipo

    @property
    def editorial(self):
        return self.editoriales_id_editorial

    @property
    def categoria(self):
        return self.categorias_id_categoria

    @property
    def autor(self):
        autores = self.autores_id_autor.all()
        return ", ".join([str(a) for a in autores]) if autores.exists() else "Sin autor"

class MaterialCarrera(models.Model):
    materiales_id_material = models.ForeignKey(Material, on_delete=models.CASCADE, db_column='materiales_id_material')
    carreras_id_carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, db_column='carreras_id_carrera')

    class Meta:
        db_table = 'materiales_y_carreras'
        verbose_name = 'Material - Carrera'
        verbose_name_plural = 'Materiales - Carreras'

class MaterialGenero(models.Model):
    materiales_id_material = models.ForeignKey(Material, on_delete=models.CASCADE, db_column='materiales_id_material')
    generos_id_genero = models.ForeignKey(Genero, on_delete=models.CASCADE, db_column='generos_id_genero')

    class Meta:
        db_table = 'materiales_y_generos'
        verbose_name = 'Material - Género'
        verbose_name_plural = 'Materiales - Géneros'


# 5. Circulación (Lógica Relacional)
class Prestamo(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('DEVUELTO', 'Devuelto'),
        ('VENCIDO', 'Vencido'),
    ]

    id_prestamo = models.AutoField(primary_key=True)
    ALUMNOS_id_alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT, db_column='ALUMNOS_id_alumno', verbose_name='Alumno')
    MATERIALES_id_material = models.ForeignKey(Material, on_delete=models.PROTECT, db_column='MATERIALES_id_material', verbose_name='Material')
    administrador_usuariosbibliosoft_id = models.ForeignKey(User, on_delete=models.PROTECT, db_column='administrador_usuariosbibliosoft_id', verbose_name='Usuario que presta')
    fecha_prestamo = models.DateField(auto_now_add=True, verbose_name='Fecha de Préstamo')
    fecha_vencimiento = models.DateField(verbose_name='Fecha de Vencimiento')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO', verbose_name='Estado')

    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

    def __str__(self):
        return f"Préstamo {self.id_prestamo} - {self.ALUMNOS_id_alumno} - {self.MATERIALES_id_material.titulo}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        from django.utils import timezone
        
        # Fallback to calculate due date (2 days from today) if not set
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = timezone.now().date() + timezone.timedelta(days=2)

        if is_new:
            # Validar disponibilidad
            if self.MATERIALES_id_material.cantidad_disponible <= 0:
                raise ValidationError("No hay stock disponible para este material.")
            # Decrementar cantidad disponible
            self.MATERIALES_id_material.cantidad_disponible -= 1
            self.MATERIALES_id_material.save()
        else:
            # Handle case where material was changed during edit
            orig = Prestamo.objects.get(pk=self.pk)
            if orig.MATERIALES_id_material != self.MATERIALES_id_material:
                # Return stock to the previous material
                orig.MATERIALES_id_material.cantidad_disponible += 1
                orig.MATERIALES_id_material.save()
                # Deduct stock from the new material
                if self.MATERIALES_id_material.cantidad_disponible <= 0:
                    raise ValidationError("No hay stock disponible para este material.")
                self.MATERIALES_id_material.cantidad_disponible -= 1
                self.MATERIALES_id_material.save()

        super().save(*args, **kwargs)

    @classmethod
    def actualizar_vencidos(cls):
        from django.utils import timezone
        cls.objects.filter(estado='ACTIVO', fecha_vencimiento__lt=timezone.now().date()).update(estado='VENCIDO')

class Devolucion(models.Model):
    id_devolucion = models.AutoField(primary_key=True)
    prestamos_id_prestamo = models.OneToOneField(Prestamo, on_delete=models.PROTECT, db_column='prestamos_id_prestamo', verbose_name='Préstamo')
    fecha_devolucion = models.DateField(auto_now_add=True, verbose_name='Fecha de Devolución')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    multa = models.DecimalField(max_digits=8, decimal_places=0, default=0, verbose_name='Multa')
    
    estado_material = models.CharField(
        max_length=50, 
        choices=[('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo')], 
        default='BUENO', 
        verbose_name='Estado del Material'
    )
    pago_multa = models.BooleanField(default=False, verbose_name='¿Pagó la Multa?')

    class Meta:
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'

    def __str__(self):
        return f"Devolución de Préstamo {self.prestamos_id_prestamo.id_prestamo}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            # Calcular multa automáticamente
            from django.utils import timezone
            prestamo = self.prestamos_id_prestamo
            if prestamo.fecha_vencimiento < timezone.now().date():
                dias_retraso = (timezone.now().date() - prestamo.fecha_vencimiento).days
                self.multa = dias_retraso * 1500
            else:
                self.multa = 0
                self.pago_multa = False  # Si no hay multa, se guarda por defecto falso/no aplica

        super().save(*args, **kwargs)
        if is_new:
            # Lógica requerida: Sumar 1 a la cantidad disponible y cambiar estado a 'DEVUELTO'
            self.prestamos_id_prestamo.estado = 'DEVUELTO'
            self.prestamos_id_prestamo.save()
            
            self.prestamos_id_prestamo.MATERIALES_id_material.cantidad_disponible += 1
            self.prestamos_id_prestamo.MATERIALES_id_material.save()
