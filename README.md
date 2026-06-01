# 📚 Sistema de Biblioteca UCI 2026 - Universidad Católica Campus Itapúa

¡Bienvenido al **Sistema de Biblioteca UCI 2026**! Esta es una plataforma integral, moderna y robusta diseñada específicamente para la gestión eficiente del acervo bibliográfico, control de préstamos y devoluciones, y administración de credenciales de los estudiantes de la **Universidad Católica Campus Itapúa (UCI)**.

El ecosistema digital está optimizado para brindar una experiencia de usuario fluida y transparente tanto para el personal administrativo de la biblioteca como para la comunidad académica (estudiantes y docentes).

---

## 🌟 Características Principales

### 🌐 Portal Web & Backend de Administración
* **Catálogo Público Integrado:** Búsqueda rápida y avanzada de libros, tesis, proyectos de investigación y revistas por carrera, autor, categoría y disponibilidad.
* **Panel de Control Administrativo:** Gestión centralizada de autores, géneros, libros, stock físico, alumnos, carreras y facultades.
* **Control Inteligente de Préstamos:** Registro rápido de entregas y devoluciones con cálculo automático de estados de préstamo (vigentes, devueltos y retrasados).
* **Generación de Reportes PDF:** Exportación de listados de acervo bibliográfico y materiales de investigación organizados por carrera, listos para impresión profesional.

### 📱 Aplicación Móvil (Flutter)
* **Diseño Moderno & Accesible:** Interfaz nativa desarrollada bajo los lineamientos de **Material Design 3** con soporte para múltiples dispositivos.
* **Consulta de Catálogo en Tiempo Real:** Filtros dinámicos y visualización detallada del stock disponible.
* **Historial Personal:** Los alumnos pueden consultar el estado de sus préstamos activos y su historial de lecturas de manera instantánea.
* **Conectividad Eficiente:** Sincronización transparente con el servidor central mediante una API REST de alto rendimiento.

### ⚡ REST API de Integración
* Arquitectura basada en **Django REST Framework (DRF)**.
* Endpoints seguros para la consulta de catálogo, verificación de credenciales de alumnos y validación de disponibilidad de materiales en tiempo real.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología Principal | Propósito / Librerías clave |
| :--- | :--- | :--- |
| **Backend & Web App** | Python 3.10+, Django 6.0+ | Núcleo del sistema, ORM, Panel de Administración |
| **REST API** | Django REST Framework (DRF) | Comunicación desacoplada con la app móvil |
| **Base de Datos** | SQLite (Entorno de desarrollo) | Persistencia ligera, escalable a PostgreSQL en producción |
| **Frontend Web** | HTML5, CSS3, Bootstrap 5, AOS | Interfaz de usuario responsiva y animaciones dinámicas |
| **Aplicación Móvil** | Flutter SDK 3.x, Dart 3.x | Aplicación multiplataforma (Android / iOS / Web) |

---

## 🚀 Guía de Instalación y Configuración

Siga los pasos descritos a continuación para clonar, configurar e iniciar el entorno de desarrollo local.

### 1. Clonar el Repositorio

Abra una terminal y ejecute el siguiente comando para descargar el proyecto:
```bash
git clone https://github.com/DariusK1ngg/bibliosoft-uci-2026.git
cd proyecto-biblioteca-uci-2026
```

---

### 2. Configuración del Backend & API (Django)

Se recomienda encarecidamente utilizar un entorno virtual de Python para aislar las dependencias del proyecto.

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
Instale los paquetes requeridos especificados en `requirements.txt`:
```bash
pip install -r requirements.txt
```

#### C. Aplicar Migraciones
Prepare y aplique el esquema inicial en la base de datos local:
```bash
python manage.py migrate
```

#### D. Sembrar Datos de Prueba (Seed Database)
Para facilitar el proceso de pruebas y demostración, el proyecto cuenta con un script que pre-carga facultades de la UCI, carreras correspondientes, registros de alumnos, categorías de libros y un **superusuario administrador**:
```bash
python seed_db.py
```
* **Credenciales de Administrador creadas por defecto:**
  * **Usuario:** `admin`
  * **Contraseña:** `admin1234`
  * **Correo:** `admin@example.com`

#### E. Iniciar el Servidor de Desarrollo
Ejecute el servidor de Django:
```bash
python manage.py runserver
```
La aplicación web estará disponible en los siguientes enlaces locales:
* **Página principal (Landing page y catálogo público):** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Panel de administración nativo de Django:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) *(Inicie sesión con las credenciales de administrador)*
* **Panel de Gestión de Biblioteca personalizado:** [http://127.0.0.1:8000/panel/](http://127.0.0.1:8000/panel/)
* **Documentación / Raíz de la API REST:** [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

---

### 3. Configuración de la Aplicación Móvil (Flutter)

El código fuente de la aplicación móvil se localiza en el directorio `/mobile_app`.

#### A. Acceder al directorio del frontend móvil
```bash
cd mobile_app
```

#### B. Obtener Paquetes y Dependencias de Flutter
```bash
flutter pub get
```

#### C. Ejecutar la Aplicación en Modo Desarrollo
* **Ejecución Estándar (Emulador, dispositivo conectado o Chrome):**
  ```bash
  flutter run
  ```
  *(Seleccione el navegador Chrome o el emulador de su preferencia).*

* **Ejecución como Servidor Web Local (Permite pruebas en teléfonos físicos en la misma red):**
  Si desea acceder a la aplicación desde su dispositivo móvil personal conectado a la misma red Wi-Fi:
  1. Ejecute el servidor web con la interfaz expuesta:
     ```bash
     flutter run -d web-server --web-hostname 0.0.0.0 --web-port 8080
     ```
  2. Identifique su dirección IP local (IPv4) en su computadora:
     * **En Windows:** Ejecute `ipconfig` en la consola y localice la "Dirección IPv4" (ej. `192.168.1.45`).
     * **En macOS/Linux:** Ejecute `ifconfig` o `ip route`.
  3. Abra el navegador en su smartphone e ingrese a: `http://<TU_IP_LOCAL>:8080` (ejemplo: `http://192.168.1.45:8080`).
  4. Para detener la ejecución del servidor de desarrollo de Flutter, presione `q` en la terminal.

---

## 📁 Estructura General del Proyecto

```text
├── biblioteca/             # Aplicación Django principal (Modelos, Vistas y Lógica de negocio de la biblioteca)
├── config/                 # Directorio de configuración global de Django (settings, urls, wsgi)
├── landing/                # Vistas y plantillas de la Landing Page principal y catálogo de cara al público
├── static/                 # Recursos multimedia estáticos globales (Logotipos y estilos compartidos)
├── mobile_app/             # Proyecto Flutter (Frontend móvil y web adaptable)
│   ├── lib/                # Lógica del cliente en Dart (Vistas, Controladores, Modelos e integración con la API)
│   ├── assets/             # Recursos propios de la aplicación (Imágenes de marca, iconos, fuentes)
│   └── pubspec.yaml        # Manifiesto de dependencias y configuración de Flutter
├── requirements.txt        # Paquetes y dependencias de Python
├── seed_db.py              # Script automático de población para base de datos de demostración
├── .gitignore              # Reglas de exclusión para Git (Excluye base de datos local y dependencias temporales)
└── README.md               # Documentación general del proyecto (este archivo)
```

---

## 🔒 Estándares de Desarrollo del Repositorio

* **Exclusión de archivos locales:** Evite realizar commits que incluyan archivos autogenerados de bases de datos locales (`db.sqlite3`), carpetas de entornos virtuales (`.venv/`), compilados de Flutter (`build/`) o metadatos de su IDE (como `.idea/` o `.vscode/`). Asegúrese de que el archivo `.gitignore` cubra adecuadamente estas rutas.
* **Control de versiones:** Se recomienda crear ramas descriptivas para el desarrollo de funcionalidades y correcciones (`feature/nombre-de-funcion`, `bugfix/nombre-de-error`) y someter los cambios a revisión mediante Pull Requests hacia la rama principal.

