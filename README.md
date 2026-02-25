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

- Python 3.8+
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
sistema_retiros/
├── main.py                 # Punto de entrada
├── app/
│   ├── db/                # Módulo de base de datos
│   ├── auth/              # Módulo de autenticación
│   ├── modules/           # Módulos funcionales (retiros, cajas, usuarios, reportes)
│   ├── ui/                # Interfaz gráfica (ventanas principales)
│   └── utils/             # Funciones auxiliares
├── data/                  # Almacenamiento de archivos (DB, etc)
├── exports/               # Archivos exportados (PDF, Excel)
├── tests/                 # Pruebas unitarias
└── docs/                  # Documentación
```

## Arquitectura

El proyecto sigue un patrón Model-View por módulo:
- `model.py`: Lógica de negocio y acceso a base de datos
- `view.py`: Interfaz gráfica con tkinter

Todos los módulos centralizan la conexión a SQLite a través de `app/db/connection.py`

## Usuarios por Defecto

- **Usuario**: admin
- **Contraseña**: admin123
- **Rol**: Administrador

## Desarrollo

Para información sobre la arquitectura, consultar `docs/arquitectura.md`

Para el manual del usuario, consultar `docs/manual_usuario.md`

## Autor

Equipo 2 - GDR 2.0

## Licencia

Privada
