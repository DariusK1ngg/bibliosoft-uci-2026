# 📚 Sistema de Biblioteca UCI 2026

¡Bienvenido al **Sistema de Biblioteca UCI 2026**! Esta es una plataforma moderna e integral diseñada para gestionar de manera eficiente el acervo bibliográfico, los préstamos, las devoluciones y las credenciales de los estudiantes de la Universidad Científica del Sur (UCI).

El ecosistema está compuesto por:
1. 🌐 **Landing Page y Panel Administrativo (Backend)**: Desarrollado en Django con un diseño interactivo (Bootstrap 5, AOS para animaciones).
2. 📱 **Aplicación Móvil**: Desarrollada en Flutter (Material 3) para que los alumnos y administradores puedan consultar el catálogo y gestionar préstamos en tiempo real.
3. ⚡ **REST API**: Una API robusta implementada con Django REST Framework para conectar la aplicación móvil con la base de datos central de Django.

---

## 🛠️ Tecnologías y Requisitos

### Backend & Web (Django)
* **Python** 3.10 o superior.
* **Django 6.0+**
* **Django REST Framework** para la API.
* **SQLite** (Base de datos local preconfigurada para desarrollo rápido).
* **Bootstrap 5 & AOS** (Animaciones en el frontend).

### Aplicación Móvil (Flutter)
* **Flutter SDK** 3.x.
* **Dart** 3.x.
* **Material 3** para diseño moderno y consistente.

---

## 🚀 Guía de Instalación y Configuración

Sigue estos pasos detallados para clonar y ejecutar el proyecto localmente.

### 1. Clonar el repositorio
Abre una terminal y clona el proyecto con el siguiente comando:
```bash
git clone https://github.com/DariusK1ngg/bibliosoft-uci-2026.git
cd proyecto-biblioteca-uci-2026
```

---

### 2. Configuración del Servidor Web & API (Django)

Se recomienda utilizar un entorno virtual de Python para mantener limpias las dependencias.

#### A. Crear y Activar el Entorno Virtual
* **En Windows (PowerShell / CMD):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **En macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### B. Instalar Dependencias
Instala los paquetes de Python requeridos usando `requirements.txt`:
```bash
pip install -r requirements.txt
```

#### C. Aplicar Migraciones
Prepara y aplica la estructura de la base de datos local:
```bash
python manage.py migrate
```

#### D. Sembrar Datos de Prueba (Seed Database)
Para facilitar el testeo, el proyecto incluye un script de siembra que crea facultades, carreras, alumnos, materiales, categorías y un **superusuario administrador**:
```bash
python seed_db.py
```
* **Credenciales de Administrador generadas:**
  * **Usuario:** `admin`
  * **Contraseña:** `admin1234`
  * **Correo:** `admin@example.com`

#### E. Correr el Servidor
Inicia el servidor de desarrollo de Django:
```bash
python manage.py runserver
```
El servidor web estará disponible en [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
* **Página principal (Landing page):** `http://127.0.0.1:8000/`
* **Panel de administración de Django:** `http://127.0.0.1:8000/admin/` (Inicia sesión con `admin` / `admin1234`)
* **Panel de gestión de biblioteca:** `http://127.0.0.1:8000/panel/`
* **Endpoints de la API:** `http://127.0.0.1:8000/api/`

---

### 3. Configuración de la Aplicación Móvil (Flutter)

La aplicación móvil se encuentra en la carpeta `/mobile_app`.

#### A. Navegar a la carpeta
```bash
cd mobile_app
```

#### B. Instalar dependencias de Flutter
```bash
flutter pub get
```

#### C. Ejecutar la aplicación en modo desarrollo
* **Ejecutar normalmente (Dispositivo físico, emulador o Chrome local):**
  ```bash
  flutter run
  ```
  *Selecciona el navegador Chrome o tu emulador preferido.*

* **Ejecutar como Servidor Web Local (ideal para probar en tu celular real):**
  Si deseas acceder al sistema web móvil desde tu propio celular conectado a la misma red Wi-Fi:
  1. Ejecuta el servidor web escuchando en todas las interfaces:
     ```bash
     flutter run -d web-server --web-hostname 0.0.0.0 --web-port 8080
     ```
  2. En otra terminal de tu computadora, averigua tu IP local (IPv4):
     * **En Windows:** Ejecuta `ipconfig` y busca la sección "Dirección IPv4" (ej. `192.168.1.45`).
     * **En macOS/Linux:** Ejecuta `ifconfig` o `ip route`.
  3. Abre el navegador en tu teléfono celular e ingresa a: `http://<TU_IP_LOCAL>:8080` (ejemplo: `http://192.168.1.45:8080`).
  4. Para apagar el servidor de Flutter, presiona la tecla `q` en la terminal.

---

## 📁 Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

```text
├── biblioteca/             # Aplicación Django principal (Modelos, Vistas y Lógica de negocio)
├── config/                 # Configuraciones globales de Django (settings, urls, etc.)
├── landing/                # Aplicación Django encargada de la página de inicio (Landing page)
├── static/                 # Archivos estáticos compartidos (Imágenes corporativas, logos)
├── mobile_app/             # Aplicación móvil Flutter (Frontend móvil/web)
│   ├── lib/                # Código fuente de Dart (pantallas, servicios, modelos)
│   ├── assets/             # Recursos de la app (imágenes, fuentes)
│   └── pubspec.yaml        # Archivo de configuración de Flutter y dependencias
├── requirements.txt        # Dependencias de Python necesarias para Django
├── seed_db.py              # Script para llenar la base de datos con registros demo y superusuario
├── .gitignore              # Configuración de Git para evitar subir archivos temporales o pesados
└── README.md               # Este archivo de documentación
```

---

## 🔒 Buenas Prácticas y Políticas del Repositorio
* **No subir archivos innecesarios:** Antes de hacer un commit, asegúrate de no estar subiendo bases de datos locales (`db.sqlite3`), carpetas de entornos virtuales (`.venv/`), carpetas de dependencias temporales de Flutter o configuraciones locales del IDE. El `.gitignore` ya viene preconfigurado para evitar esto.
* **Ramas y flujo de trabajo:** Crea ramas descriptivas para nuevas funcionalidades (ej: `feature/nueva-vista`) y abre un Pull Request hacia `master` (o `main`) para revisión.
