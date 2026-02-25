# Arquitectura del Sistema de Retiros

## Descripción General

El Sistema de Retiros es una aplicación de escritorio construida con Python y tkinter que sigue un patrón de arquitectura Model-View por módulo, centralizado con una capa de acceso a datos (DAO) única usando SQLite.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    MainWindow (UI)                       │
│                 (sidebar + content area)                 │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴──────────────────┐
        ↓                                    ↓
   ┌─────────────┐                  ┌────────────────┐
   │   Models    │                  │     Views      │
   │ (model.py)  │←────────────────→│    (view.py)   │
   └─────────────┘                  └────────────────┘
        ↓
   ┌─────────────────────────────────────────┐
   │   Database Layer (app/db/)              │
   │   - connection.py (get_conn, init_db)   │
   │   - schema.sql (CREATE TABLE statements)│
   │   - seed.py (initial data loading)      │
   └─────────────────────────────────────────┘
        ↓
   ┌─────────────────────────────────────────┐
   │   SQLite Database (data/retiros.db)     │
   │   - usuarios                            │
   │   - cajas                               │
   │   - retiros                             │
   │   - reportes_generados                  │
   └─────────────────────────────────────────┘
```

## Estructura de Directorios

```
sistema_retiros/
├── main.py                          # Punto de entrada
│
├── app/
│   ├── __init__.py
│   │
│   ├── db/                          # Capa de Datos
│   │   ├── __init__.py
│   │   ├── connection.py            # Cifunciones get_conn(), init_db()
│   │   ├── schema.sql               # Esquema de BD
│   │   └── seed.py                  # Datos iniciales
│   │
│   ├── auth/                        # Autenticación
│   │   ├── __init__.py
│   │   ├── login.py                 # Ventana de login
│   │   └── session.py               # Gestión de sesión
│   │
│   ├── modules/                     # Módulos Funcionales (Model-View)
│   │   ├── __init__.py
│   │   ├── retiros/
│   │   │   ├── __init__.py
│   │   │   ├── model.py             # CRUD + lógica
│   │   │   └── view.py              # Interfaz gráfica
│   │   ├── cajas/
│   │   │   ├── __init__.py
│   │   │   ├── model.py
│   │   │   └── view.py
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   ├── model.py
│   │   │   └── view.py
│   │   ├── reportes/
│   │   │   ├── __init__.py
│   │   │   ├── model.py
│   │   │   ├── view.py
│   │   │   ├── export_pdf.py        # Exportación PDF
│   │   │   └── export_excel.py      # Exportación Excel
│   │   └── calculos/
│   │       ├── __init__.py
│   │       └── totales.py           # Funciones de cálculo
│   │
│   ├── ui/                          # Interfaz Gráfica General
│   │   ├── __init__.py
│   │   ├── main_window.py           # Ventana principal
│   │   ├── dashboard.py             # Vista del dashboard
│   │   └── components.py            # Componentes reutilizables
│   │
│   └── utils/                       # Utilidades
│       ├── __init__.py
│       └── helpers.py               # Funciones auxiliares
│
├── data/                            # Almacenamiento de datos
│   └── retiros.db                   # BD SQLite
│
├── exports/                         # Reportes generados
│   ├── *.pdf
│   └── *.xlsx
│
├── tests/                           # Pruebas unitarias
│   ├── __init__.py
│   ├── test_retiros.py
│   ├── test_cajas.py
│   ├── test_usuarios.py
│   ├── test_calculos.py
│   └── test_reportes.py
│
├── docs/                            # Documentación
│   ├── manual_usuario.md
│   ├── arquitectura.md
│   └── assets/
│
├── requirements.txt                 # Dependencias del proyecto
├── .gitignore                       # Archivos excluidos de git
└── README.md                        # Información del proyecto
```

## Patrones de Arquitectura

### 1. Model-View por Módulo

Cada módulo funcional tiene dos responsabilidades claramente separadas:

```python
# model.py: Todo lo relacionado con datos y lógica
# - Gestión de BD
# - Consultas SQL
# - Cálculos
# - Reglas de negocio
insertar_retiro(id_usuario, id_caja, monto, ...)
obtener_retiros_por_fecha(fecha)
calcular_total_diario()

# view.py: Todo lo relacionado con la interfaz
# - Componentes gráficos (widgets)
# - Validación de entrada del usuario
# - Actualización de la pantalla
# - Manejo de eventos de usuario
class RetirosView(tk.Frame):
    def __init__(self, parent):
        pass
    def _on_nuevo_retiro(self):
        pass
```

### 2. Singleton para Session

La sesión del usuario se gestiona como un Singleton para garantizar una única instancia en toda la aplicación:

```python
from app.auth.session import Session

# En cualquier parte del código
session = Session()
session.set_user(id, nombre, usuario, rol)
user = session.get_user()
if session.is_admin():
    # Ejecutar lógica de admin
```

### 3. Centralización de Conexión a BD

Todos los módulos usan la misma función para obtener conexiones:

```python
from app.db.connection import get_conn

# En cualquier model.py
def obtener_retiros():
    conn = get_conn()
    cursor = conn.cursor()
    # ... SQL queries ...
    conn.close()
```

### 4. Inyección de Dependencias (inversa)

Las vistas reciben referencias a sus padres:

```python
class RetirosView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
```

## Flujo de Datos

### Flujo de Registro de Retiro

```
Usuario (RetirosView)
    ↓
_on_nuevo_retiro() valida entrada
    ↓
model.insertar_retiro() ejecuta INSERT
    ↓
Retorno a view, actualiza tabla
    ↓
_refresh_retiros() obtiene datos actualizados
    ↓
Tabla actualizada en pantalla
```

### Flujo de Login

```
Usuario escribe credenciales (LoginWindow)
    ↓
_validate_login()
    ↓
model.obtener_usuario_por_username()
    ↓
verify_password() valida contraseña
    ↓
Session.set_user() si es válido
    ↓
Abre MainWindow
```

### Flujo de Generación de Reporte

```
Usuario selecciona período (ReportesView)
    ↓
_on_generar_reporte()
    ↓
reportes_model.total_diario() / semanal / mensual
    ↓
Retorna datos
    ↓
Tabla se llena en view
    ↓
_on_exportar_pdf() o _on_exportar_excel()
    ↓
Llama a export_pdf.py o export_excel.py
    ↓
Archivo se crea en exports/
```

## Paleta de Colores

```python
C_BG = "#F0F2F5"        # Fondo gris claro
C_SIDEBAR = "#1565C0"   # Azul principal (navbar)
C_ACCENT = "#1976D2"    # Azul secundario
C_WHITE = "#FFFFFF"     # Blanco
C_TEXT = "#212121"      # Texto gris oscuro
C_HEADER = "#1565C0"    # Encabezados azul
C_BTN = "#1565C0"       # Botones azul
C_DANGER = "#C62828"    # Rojo para acciones peligrosas
```

## Modelo de Datos

### Tabla: usuarios
```sql
id (int, PK)
nombre (text)
usuario (text, UNIQUE)
password_hash (text)
rol (text: administrador, gerente, operador)
activo (int: 0=no, 1=si)
fecha_creacion (datetime)
fecha_modificacion (datetime)
```

### Tabla: cajas
```sql
id (int, PK)
nombre (text, UNIQUE)
numero_caja (text)
ubicacion (text)
activa (int: 0=no, 1=si)
fecha_creacion (datetime)
fecha_modificacion (datetime)
```

### Tabla: retiros
```sql
id (int, PK)
id_usuario (int, FK)
id_caja (int, FK)
monto (float)
motivo (text)
fecha_retiro (datetime)
fecha_registro (datetime)
observaciones (text)
```

### Tabla: reportes_generados
```sql
id (int, PK)
tipo_reporte (text)
periodo (text)
fecha_inicio (date)
fecha_fin (date)
total_retiros (float)
cantidad_retiros (int)
ruta_archivo (text)
formato (text: PDF, Excel)
fecha_generacion (datetime)
```

## Roles y Permisos

| Función | Admin | Gerente | Operador |
|---------|-------|---------|----------|
| Registrar retiros | ✓ | ✓ | ✓ |
| Ver reportes | ✓ | ✓ | ✓ |
| Exportar reportes | ✓ | ✓ | ✓ |
| Administrar cajas | ✓ | ✓ | ✗ |
| Administrar usuarios | ✓ | ✗ | ✗ |
| Ver dashboard | ✓ | ✓ | ✓ |
| Cambiar contraseña | ✓ | ✓ | ✓ |

## Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje de programación
- **tkinter**: Interfaz gráfica (incluido en Python)
- **SQLite 3**: Base de datos (incluido en Python)
- **ReportLab 4.0+**: Generación de PDF
- **openpyxl 3.1+**: Generación de Excel
- **unittest**: Framework de pruebas (incluido en Python)

## Consideraciones de Seguridad

1. **Contraseñas**: Se hashean con SHA-256
2. **Sesión**: Se mantiene en memoria con Singleton
3. **BD**: SQLite con acceso local
4. **SQL Injection**: Se usan parámetros preparados en todas las queries

## Extensibilidad

El proyecto está diseñado para ser fácilmente extensible:

1. **Nuevos módulos**: Crear carpeta en `app/modules/` con `model.py` y `view.py`
2. **Nuevas funciones**: Agregar a `utils/helpers.py` o nuevos archivos
3. **Nuevos cálculos**: Agregar a `modules/calculos/totales.py`
4. **Nuevos tipos de reporte**: Crear nueva vista en `modules/reportes/view.py`

## Performance

- **Índices en BD**: Optimizados para consultas frecuentes (fecha, usuario, caja)
- **Lazy loading**: Datos se cargan bajo demanda
- **Caché de sesión**: Usuario/rol en memoria durante sesión
- **Row Factory**: Permite acceso a columnas por nombre sin overhead

## Testing

Ejecutar pruebas:

```bash
python -m unittest discover tests/
```

Cobertura:

```bash
coverage run -m unittest discover tests/
coverage report
```
