# Sistema de Retiros - GDR 2.0

Sistema de control de retiros de efectivo para empresas con múltiples cajas físicas.

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
│   │   │   ├── export_pdf.py       # Exportación a PDF (reportlab)
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
├── tests/                          # Pruebas unitarias
│   ├── __init__.py
│   ├── test_cajas.py
│   ├── test_calculos.py
│   ├── test_reportes.py
│   ├── test_retiros.py
│   └── test_usuarios.py
│

```

> **Nota:** Los directorios `build/` y `dist/` son generados automáticamente por PyInstaller al compilar el ejecutable con `compilar.bat`. No forman parte del código fuente.

## Arquitectura

El proyecto sigue un patrón Model-View por módulo:
- `model.py`: Lógica de negocio y acceso a base de datos
- `view.py`: Interfaz gráfica con tkinter

Todos los módulos centralizan la conexión a SQLite a través de `app/db/connection.py`

## Usuarios por Defecto

- **Usuario**: admin
- **Contraseña**: admin123
- **Rol**: Administrador

- **Usuario**: gerente
- **Contraseña**: gerente123
- **Rol**: Gerente

- **Usuario**: operador
- **Contraseña**: operador123
- **Rol**: Operador

## Compilar a Ejecutable

Para generar el ejecutable de Windows:

```bat
compilar.bat
```

El ejecutable resultante se encontrará en `dist/SistemaRetiros/SistemaRetiros.exe`.


## Autor

Equipo 2 - GDR 2.0
