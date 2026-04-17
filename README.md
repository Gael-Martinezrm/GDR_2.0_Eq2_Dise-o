# Sistema de Retiros - OfficeMax

Sistema de control de retiros de efectivo para OfficeMax.

## Descripción

Sistema de escritorio construido con Python, tkinter y SQLite que permite:
- Registro y seguimiento de retiros de efectivo por caja
- Gestión de usuarios con roles (administrador, gerente, operador)
- Consulta y filtrado de retiros por fecha y caja
- Generación de reportes diarios y semanales
- Exportación a PDF y Excel
- Administración de cajas y usuarios del sistema

## Características

- **Autenticación**: Sistema de login con hashing de contraseñas
- **3 Roles de Usuario**: Administrador, Gerente, Operador
- **3 Cajas Físicas**: Múltiples puntos de retiro
- **Base de Datos SQLite**: Persistencia en `data/retiros.db`
- **Reportes**: Diarios, semanales y mensuales
- **Exportación**: PDF y Excel para análisis
- **Interfaz Gráfica**: Tkinter con diseño moderno azul

## Requisitos

- Python 3.13+
- tkinter (incluido con Python)
- SQLite3 (incluido con Python)
- Ver `requirements.txt` para dependencias adicionales

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## Estructura del Proyecto

```
GDR_2.0_Eq2_Dise-o/
├── main.py                         # Punto de entrada: inicializa DB y lanza login
├── requirements.txt                # Dependencias del proyecto (openpyxl, reportlab)
├── compilar.bat                    # Script para generar el ejecutable con PyInstaller
├── dependencias.bat                # Script para instalar dependencias offline
├── GDR_Sistema_Retiros.spec        # Configuración de PyInstaller
│
├── app/                            # Paquete principal de la aplicación
│   ├── __init__.py
│   ├── auth/                       # Módulo de autenticación
│   │   ├── __init__.py
│   │   ├── login.py                # Ventana de login
│   │   └── session.py              # Manejo de sesión activa
│   │
│   ├── db/                         # Módulo de base de datos
│   │   ├── __init__.py
│   │   ├── connection.py           # Conexión SQLite e inicialización
│   │   ├── schema.sql              # Definición del esquema de tablas
│   │   └── seed.py                 # Datos iniciales (usuario admin, cajas)
│   │
│   ├── modules/                    # Módulos funcionales (patrón Model-View)
│   │   ├── __init__.py
│   │   ├── cajas/                  # Gestión de cajas físicas
│   │   │   ├── __init__.py
│   │   │   ├── model.py            # Lógica y acceso a datos de cajas
│   │   │   └── view.py             # Pantalla de administración de cajas
│   │   │
│   │   ├── calculos/               # Cálculos de totales y agregaciones
│   │   │   ├── __init__.py
│   │   │   └── totales.py          # Funciones para dashboard y reportes
│   │   │
│   │   ├── reportes/               # Generación y exportación de reportes
│   │   │   ├── __init__.py
│   │   │   ├── model.py            # Consultas y lógica de reportes
│   │   │   └── view.py             # Pantalla de reportes
│   │   │
│   │   ├── retiros/                # Registro y consulta de retiros
│   │   │   ├── __init__.py
│   │   │   ├── model.py            # Lógica y acceso a datos de retiros
│   │   │   └── view.py             # Pantalla de retiros
│   │   │
│   │   └── usuarios/               # Administración de usuarios
│   │       ├── __init__.py
│   │       ├── model.py            # Lógica y acceso a datos de usuarios
│   │       └── view.py             # Pantalla de administración de usuarios
│   │
│   ├── ui/                         # Interfaz principal de la aplicación
│   │   ├── __init__.py
│   │   ├── components.py           # Widgets y componentes reutilizables
│   │   ├── dashboard.py            # Pantalla principal / dashboard
│   │   └── main_window.py          # Ventana principal con navegación
│   │
│   └── utils/                      # Utilidades y funciones auxiliares
│       ├── __init__.py
│       └── helpers.py              # Funciones de fechas, formateo, etc.
│
├── data/                           # Almacenamiento en tiempo de ejecución
│   └── retiros.db                  # Base de datos SQLite (generada al iniciar)
│
├── packages/                       # Paquetes offline para instalación sin internet
│   ├── altgraph-0.17.5-py2.py3-none-any.whl
│   ├── charset_normalizer-3.4.7-cp312-cp312-win_amd64.whl
│   ├── et_xmlfile-2.0.0-py3-none-any.whl
│   ├── openpyxl-3.1.5-py2.py3-none-any.whl
│   ├── packaging-26.1-py3-none-any.whl
│   ├── pefile-2024.8.26-py3-none-any.whl
│   ├── pillow-12.2.0-cp312-cp312-win_amd64.whl
│   ├── pyinstaller-6.19.0-py3-none-win_amd64.whl
│   ├── pyinstaller_hooks_contrib-2026.4-py3-none-any.whl
│   ├── pywin32_ctypes-0.2.3-py3-none-any.whl
│   ├── reportlab-4.4.10-py3-none-any.whl
│   └── setuptools-82.0.1-py3-none-any.whl
│
├── python-3.14.4-amd64.exe         # Instalador de Python (distribución offline)
│
└── tests/                          # Pruebas unitarias
    ├── __init__.py
    ├── test_cajas.py
    ├── test_calculos.py
    ├── test_reportes.py
    ├── test_retiros.py
    └── test_usuarios.py
```

> **Nota:** Los directorios `build/` y `dist/` son generados automáticamente por PyInstaller al compilar el ejecutable con `compilar.bat`. No forman parte del código fuente.

## Arquitectura

El proyecto sigue un patrón Model-View por módulo:
- `model.py`: Lógica de negocio y acceso a base de datos
- `view.py`: Interfaz gráfica con tkinter

Todos los módulos centralizan la conexión a SQLite a través de `app/db/connection.py`

## Usuarios por Defecto

| Usuario  | Contraseña   | Rol           |
|----------|--------------|---------------|
| admin    | admin123     | Administrador |
| gerente  | gerente123   | Gerente       |
| operador | operador123  | Operador      |


## Compilar a Ejecutable

Para generar el ejecutable de Windows:

```bat
compilar.bat
```

El ejecutable resultante se encontrará en `dist/SistemaRetiros/SistemaRetiros.exe`.