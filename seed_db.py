import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from biblioteca.models import (
    Autor, Editorial, Categoria, Genero, TipoDocumento,
    Facultad, Carrera, Alumno, Material, Prestamo
)
from datetime import date, timedelta

print("Iniciando la siembra de datos (Seeding)...")

# 1. Crear Superusuario
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
    print("Superusuario creado: admin / admin1234")
else:
    print("El superusuario 'admin' ya existe.")

# Obtener usuario administrador para los préstamos
admin_user = User.objects.get(username='admin')

# 2. Crear Facultad y Carrera
facultad, _ = Facultad.objects.get_or_create(nombre="Facultad de Ingeniería y Tecnología")
carrera, _ = Carrera.objects.get_or_create(nombre="Ingeniería en Sistemas de Información", facultades_id_facultad=facultad)
print("Organización Académica creada.")

# 3. Crear Alumnos
alumno1, _ = Alumno.objects.get_or_create(
    matricula="20260001",
    defaults={
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan.perez@uci.edu",
        "telefono": "+595981111222",
        "carreras_id_carrera": carrera,
        "estado": True
    }
)
alumno2, _ = Alumno.objects.get_or_create(
    matricula="20260002",
    defaults={
        "nombre": "María",
        "apellido": "Gómez",
        "email": "maria.gomez@uci.edu",
        "telefono": "+595981333444",
        "carreras_id_carrera": carrera,
        "estado": True
    }
)
print("Alumnos creados.")

# 4. Crear Parámetros Base
autor1, _ = Autor.objects.get_or_create(nombre="Gabriel", apellido="García Márquez")
autor2, _ = Autor.objects.get_or_create(nombre="J.K.", apellido="Rowling")
autor3, _ = Autor.objects.get_or_create(nombre="Robert C.", apellido="Martin")

editorial1, _ = Editorial.objects.get_or_create(nombre="Sudamericana", direccion="Calle Falsa 123", telefono="555-0199")
editorial2, _ = Editorial.objects.get_or_create(nombre="Salamandra", direccion="Av. Diagonal 456", telefono="555-0200")
editorial3, _ = Editorial.objects.get_or_create(nombre="Prentice Hall", direccion="Upper Saddle River, NJ", telefono="555-0300")

cat1, _ = Categoria.objects.get_or_create(nombre="Literatura", descripcion="Novelas, poesía y teatro")
cat2, _ = Categoria.objects.get_or_create(nombre="Fantasía", descripcion="Mundos fantásticos y magia")
cat3, _ = Categoria.objects.get_or_create(nombre="Informática", descripcion="Ingeniería de software y desarrollo")

gen1, _ = Genero.objects.get_or_create(nombre="Realismo Mágico")
gen2, _ = Genero.objects.get_or_create(nombre="Fantasía Épica")
gen3, _ = Genero.objects.get_or_create(nombre="Tecnología / Educación")

tipo1, _ = TipoDocumento.objects.get_or_create(descripcion="Libro")
tipo2, _ = TipoDocumento.objects.get_or_create(descripcion="Revista Científica")
print("Parámetros base creados.")

# 5. Crear Materiales (Inventario)
mat1, mat1_created = Material.objects.get_or_create(
    titulo="Cien años de soledad",
    defaults={
        "editoriales_id_editorial": editorial1,
        "categorias_id_categoria": cat1,
        "tipodocumento_id_tipo": tipo1,
        "isbn": "978-0307474728",
        "año_publicacion": 1967,
        "cantidad_total": 5,
        "cantidad_disponible": 5
    }
)
mat1.autores_id_autor.add(autor1)
mat1.generos.add(gen1)

mat2, mat2_created = Material.objects.get_or_create(
    titulo="Harry Potter y la piedra filosofal",
    defaults={
        "editoriales_id_editorial": editorial2,
        "categorias_id_categoria": cat2,
        "tipodocumento_id_tipo": tipo1,
        "isbn": "978-8478884452",
        "año_publicacion": 1997,
        "cantidad_total": 3,
        "cantidad_disponible": 3
    }
)
mat2.autores_id_autor.add(autor2)
mat2.generos.add(gen2)

mat3, mat3_created = Material.objects.get_or_create(
    titulo="Código Limpio (Clean Code)",
    defaults={
        "editoriales_id_editorial": editorial3,
        "categorias_id_categoria": cat3,
        "tipodocumento_id_tipo": tipo1,
        "isbn": "978-0132350884",
        "año_publicacion": 2008,
        "cantidad_total": 4,
        "cantidad_disponible": 4
    }
)
mat3.autores_id_autor.add(autor3)
mat3.generos.add(gen3)
print("Materiales en el acervo creados.")

# 6. Crear un Préstamo Activo de prueba
if not Prestamo.objects.filter(ALUMNOS_id_alumno=alumno1, MATERIALES_id_material=mat3, estado='ACTIVO').exists():
    try:
        prestamo = Prestamo(
            ALUMNOS_id_alumno=alumno1,
            MATERIALES_id_material=mat3,
            administrador_usuariosbibliosoft_id=admin_user,
            fecha_vencimiento=date.today() + timedelta(days=7),
            estado='ACTIVO'
        )
        prestamo.save()
        print("Préstamo de prueba creado.")
    except Exception as e:
        print(f"No se pudo crear el préstamo: {e}")
else:
    print("El préstamo de prueba ya está registrado.")

print("Siembra de datos finalizada con éxito!")
