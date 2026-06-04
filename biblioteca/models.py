from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
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

    @property
    def carnet_expirado(self):
        if not self.carnet_activo or not self.carnet_fecha_entrega:
            return False
        from django.utils import timezone
        import datetime
        limit = timezone.localdate() - datetime.timedelta(days=365)
        return self.carnet_fecha_entrega < limit

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
    titulo = models.CharField(max_length=400, verbose_name='Título')
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
    def lista_numeros_entrada(self):
        import re
        if not self.numero_entrada:
            return []
        parts = re.split(r'[,/;]', self.numero_entrada)
        parts = [p.strip() for p in parts if p.strip()]
        numeros = []
        for part in parts:
            match = re.match(r'^(\d+)\s*-\s*(\d+)$', part)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                if end >= start:
                    numeros.extend([str(i) for i in range(start, end + 1)])
                else:
                    numeros.append(part)
            else:
                numeros.append(part)
        return numeros

    def numeros_entrada_disponibles(self, exclude_prestamo_id=None):
        todos = self.lista_numeros_entrada
        if not todos:
            return []
        # Import dynamically to avoid circular import
        from .models import Prestamo
        query = Prestamo.objects.filter(MATERIALES_id_material=self, estado__in=['ACTIVO', 'VENCIDO'])
        if exclude_prestamo_id:
            query = query.exclude(pk=exclude_prestamo_id)
        
        # We clean the list by getting non-empty values
        prestados = query.exclude(numero_entrada__isnull=True).exclude(numero_entrada='').values_list('numero_entrada', flat=True)
        # In case a loan contains multiple entry numbers separated by commas
        prestados_sets = set()
        for p in prestados:
            for item in [x.strip() for x in p.split(',') if x.strip()]:
                prestados_sets.add(item)
                
        disponibles = [n for n in todos if n not in prestados_sets]
        return disponibles

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


class BajaMaterial(models.Model):
    MOTIVOS = [
        ('MOJADO', 'Se mojó'),
        ('ROTO', 'Se rompió'),
        ('NO_ENTREGADO', 'Nunca se entregó'),
        ('PERDIDO', 'Pérdida'),
        ('OTRO', 'Otro')
    ]

    id_baja = models.AutoField(primary_key=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='Material')
    cantidad = models.IntegerField(default=1, verbose_name='Cantidad dada de baja')
    numero_entrada = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número de Entrada')
    motivo = models.CharField(max_length=50, choices=MOTIVOS, verbose_name='Motivo')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    fecha_baja = models.DateField(default=timezone.localdate, verbose_name='Fecha de Baja')

    class Meta:
        verbose_name = 'Baja de Material'
        verbose_name_plural = 'Bajas de Materiales'

    def __str__(self):
        return f"Baja #{self.id_baja} - {self.material.titulo} ({self.get_motivo_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            # 1. Decrementar cantidad total y disponible
            self.material.cantidad_total = max(0, self.material.cantidad_total - self.cantidad)
            self.material.cantidad_disponible = max(0, self.material.cantidad_disponible - self.cantidad)
            
            # 2. Si se especificó un número de entrada, removerlo de la lista
            if self.numero_entrada:
                to_remove = [x.strip() for x in self.numero_entrada.split(',') if x.strip()]
                current_nes = [x.strip() for x in self.material.numero_entrada.split(',') if x.strip()] if self.material.numero_entrada else []
                new_nes = [x for x in current_nes if x not in to_remove]
                self.material.numero_entrada = ", ".join(new_nes)
            
            if self.material.cantidad_total == 0:
                self.material.estado_material = 'INACTIVO'

            self.material.save()
        super().save(*args, **kwargs)


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
    fecha_prestamo = models.DateField(default=timezone.localdate, verbose_name='Fecha de Préstamo')
    fecha_vencimiento = models.DateField(verbose_name='Fecha de Vencimiento')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO', verbose_name='Estado')
    
    # Nuevos campos
    numero_entrada = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de entrada')
    prorrogado = models.BooleanField(default=False, verbose_name='Prorrogado')

    # Atributos de Devolución unificados
    fecha_devolucion = models.DateField(null=True, blank=True, verbose_name='Fecha de Devolución')
    observaciones_devolucion = models.TextField(blank=True, null=True, verbose_name='Observaciones de Devolución')
    multa = models.DecimalField(max_digits=8, decimal_places=0, default=0, verbose_name='Multa')
    estado_material = models.CharField(
        max_length=50, 
        choices=[('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo')], 
        default='BUENO', 
        null=True, 
        blank=True, 
        verbose_name='Estado del Material'
    )
    pago_multa = models.BooleanField(default=False, verbose_name='¿Pagó la Multa?')

    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

    def __str__(self):
        return f"Préstamo {self.id_prestamo} - {self.ALUMNOS_id_alumno} - {self.MATERIALES_id_material.titulo}"

    @property
    def lista_numero_entrada(self):
        if not self.numero_entrada:
            return []
        return [x.strip() for x in self.numero_entrada.split(',') if x.strip()]

    # Aliases de compatibilidad para Devolución
    @property
    def id_devolucion(self):
        return self.id_prestamo

    @property
    def prestamos_id_prestamo(self):
        return self

    @property
    def observaciones(self):
        return self.observaciones_devolucion

    @property
    def devolucion(self):
        if self.estado == 'DEVUELTO':
            return self
        return None

    def delete(self, *args, **kwargs):
        if self.estado in ['ACTIVO', 'VENCIDO']:
            self.MATERIALES_id_material.cantidad_disponible += 1
            self.MATERIALES_id_material.save()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        from django.utils import timezone
        
        # Fallback to calculate due date (2 days from today) if not set
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = timezone.localdate() + timezone.timedelta(days=2)

        if is_new:
            # Validar disponibilidad
            if self.MATERIALES_id_material.cantidad_disponible < 1:
                raise ValidationError("No hay stock disponible suficiente para este material.")
            # Decrementar cantidad disponible
            self.MATERIALES_id_material.cantidad_disponible -= 1
            self.MATERIALES_id_material.save()
        else:
            orig = Prestamo.objects.get(pk=self.pk)
            # Manejar la devolución
            if orig.estado in ['ACTIVO', 'VENCIDO'] and self.estado == 'DEVUELTO':
                self.MATERIALES_id_material.cantidad_disponible += 1
                self.MATERIALES_id_material.save()
                if not self.fecha_devolucion:
                    self.fecha_devolucion = timezone.localdate()
                if self.multa == 0:
                    config = ConfiguracionGeneral.get_solo()
                    if config.recargo_activo and self.fecha_vencimiento < self.fecha_devolucion:
                        dias_retraso = (self.fecha_devolucion - self.fecha_vencimiento).days
                        self.multa = dias_retraso * config.monto_recargo
                    else:
                        self.multa = 0
            # Si se vuelve a activar un préstamo ya devuelto
            elif orig.estado == 'DEVUELTO' and self.estado in ['ACTIVO', 'VENCIDO']:
                if self.MATERIALES_id_material.cantidad_disponible < 1:
                    raise ValidationError("No hay stock disponible suficiente para activar este préstamo.")
                self.MATERIALES_id_material.cantidad_disponible -= 1
                self.MATERIALES_id_material.save()
                self.fecha_devolucion = None
                self.observaciones_devolucion = ""
                self.multa = 0
                self.pago_multa = False
                self.estado_material = 'BUENO'
            # Si cambia el material en un préstamo activo
            elif orig.MATERIALES_id_material != self.MATERIALES_id_material:
                if orig.estado in ['ACTIVO', 'VENCIDO']:
                    orig.MATERIALES_id_material.cantidad_disponible += 1
                    orig.MATERIALES_id_material.save()
                    if self.MATERIALES_id_material.cantidad_disponible < 1:
                        raise ValidationError("No hay stock disponible suficiente para este material.")
                    self.MATERIALES_id_material.cantidad_disponible -= 1
                    self.MATERIALES_id_material.save()

        super().save(*args, **kwargs)

    @classmethod
    def actualizar_vencidos(cls):
        from django.utils import timezone
        cls.objects.filter(estado='ACTIVO', fecha_vencimiento__lt=timezone.localdate()).update(estado='VENCIDO')


class ConfiguracionGeneral(models.Model):
    monto_recargo = models.DecimalField(max_digits=8, decimal_places=0, default=1500, verbose_name='Monto del recargo por día')
    recargo_activo = models.BooleanField(default=True, verbose_name='¿Recargo activo?')
    horario_lunes_viernes = models.CharField(max_length=100, default='07:00 a 21:00 hs.', verbose_name='Horario de atención Lunes a Viernes')
    abren_sabados = models.BooleanField(default=True, verbose_name='¿Abren los Sábados?')
    horario_sabados = models.CharField(max_length=100, default='08:00 a 12:00 hs.', verbose_name='Horario de atención Sábados')

    class Meta:
        verbose_name = 'Configuración General'
        verbose_name_plural = 'Configuraciones Generales'

    def __str__(self):
        return "Configuración General"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class RegistroAuditoria(models.Model):
    ACCIONES = [
        ('CREACION', 'Creación'),
        ('MODIFICACION', 'Modificación'),
        ('ELIMINACION', 'Eliminación'),
        ('INICIO_SESION', 'Inicio de Sesión'),
        ('CERRAR_SESION', 'Cierre de Sesión'),
        ('PRORROGA', 'Prórroga'),
        ('ACTIVACION_CARNET', 'Activación de Carnet'),
        ('DESACTIVACION_CARNET', 'Desactivación de Carnet'),
    ]

    id_auditoria = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuario')
    fecha_hora = models.DateTimeField(default=timezone.now, verbose_name='Fecha y Hora')
    accion = models.CharField(max_length=50, choices=ACCIONES, verbose_name='Acción')
    tabla = models.CharField(max_length=100, verbose_name='Módulo/Tabla')
    registro_id = models.CharField(max_length=50, blank=True, verbose_name='ID Registro')
    detalle = models.TextField(verbose_name='Detalle de la Acción')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Dirección IP')

    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-fecha_hora']

    def __str__(self):
        usr = self.usuario.username if self.usuario else "Sistema"
        return f"{self.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')} - {usr} - {self.get_accion_display()} en {self.tabla}"


