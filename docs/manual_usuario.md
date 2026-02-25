# Manual del Usuario - Sistema de Retiros

## Introducción

El Sistema de Retiros es una aplicación de escritorio que permite administrar y registrar retiros de efectivo en múltiples cajas físicas de una empresa.

## Requerimientos del Sistema

- Windows 7 o superior
- Python 3.8+
- Mínimo 100 MB de espacio en disco

## Instalación

### Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 2: Ejecutar la Aplicación

```bash
python main.py
```

## Uso de la Aplicación

### 1. Autenticación

Al iniciar la aplicación, será necesario ingresar credenciales:

- **Usuario**: admin
- **Contraseña**: admin123

> Nota: El administrador debe cambiar esta contraseña después del primer acceso.

### 2. Dashboard Principal

Después de autenticarse, accederá al dashboard que muestra:

- **Total de retiros hoy**: Suma total de retiros del día actual
- **Total de retiros semana**: Acumulado de la semana actual
- **Total de retiros mes**: Acumulado del mes actual en curso
- **Número de retiros**: Cantidad de transacciones registradas hoy
- **Distribución por cajas**: Desglose de retiros por caja

### 3. Registro de Retiros

Para registrar un nuevo retiro:

1. Seleccionar "Retiros" en el menú lateral
2. Hacer clic en "Nuevo Retiro"
3. Completar el formulario:
   - **Caja**: Seleccionar la caja de donde se retira dinero
   - **Monto**: Cantidad de dinero retirado
   - **Motivo**: Razón del retiro
   - **Observaciones**: Notas adicionales (opcional)
4. Hacer clic en "Guardar"

### 4. Consulta de Retiros

Para consultar retiros:

1. Seleccionar "Retiros" en el menú lateral
2. Usar los filtros disponibles:
   - **Por fecha**: Seleccionar rango de fechas
   - **Por caja**: Filtrar por caja específica
3. Los resultados se mostrarán en la tabla

### 5. Reportes

Para generar reportes:

1. Seleccionar "Reportes" en el menú lateral
2. Seleccionar tipo de reporte:
   - **Diario**: Retiros de un día específico
   - **Semanal**: Retiros de una semana completa
   - **Mensual**: Retiros del mes completo
3. Los datos se mostrarán en una tabla
4. Para exportar:
   - Hacer clic en "Exportar a PDF" o "Exportar a Excel"
   - Seleccionar ubicación y nombre del archivo

### 6. Administración de Cajas (Admin/Gerente)

Para administrar cajas:

1. Seleccionar "Cajas" en el menú lateral (solo disponible para Admin y Gerente)
2. Ver lista de cajas existentes
3. Crear nueva caja:
   - Hacer clic en "Nueva Caja"
   - Completar datos
4. Editar caja:
   - Seleccionar caja y hacer clic en "Editar"
5. Activar/Desactivar:
   - Seleccionar caja y usar botón "Toggle"
6. Eliminar caja:
   - Seleccionar caja y hacer clic en "Eliminar"

### 7. Administración de Usuarios (Admin)

Para administrar usuarios:

1. Seleccionar "Usuarios" en el menú lateral (solo disponible para Admin)
2. Ver lista de usuarios del sistema
3. Crear nuevo usuario:
   - Hacer clic en "Nuevo Usuario"
   - Completar datos y seleccionar rol
4. Cambiar contraseña:
   - Seleccionar usuario y hacer clic en "Cambiar Password"
5. Activar/Desactivar:
   - Seleccionar usuario y usar botón "Toggle"
6. Eliminar usuario:
   - Seleccionar usuario y hacer clic en "Eliminar"

## Roles de Usuario

### Admin (Administrador)

Acceso completo a todas las funciones:
- Registrar retiros
- Ver reportes
- Administrar cajas
- Administrar usuarios
- Cambiar contraseña

### Gerente

Acceso a funciones de operación y control:
- Registrar retiros
- Ver reportes
- Administrar cajas
- Cambiar contraseña
- NO puede administrar usuarios

### Operador

Acceso limitado a funciones básicas:
- Registrar retiros
- Ver reportes básicos
- Cambiar contraseña
- NO puede administrar cajas ni usuarios

## Atajos de Teclado

- **Ctrl+Q**: Cerrar aplicación
- **Ctrl+L**: Cerrar sesión (logout)
- **F5**: Refrescar datos

## Solución de Problemas

### La aplicación no inicia

- Verificar que Python 3.8+ esté instalado: `python --version`
- Verificar que las dependencias están instaladas: `pip install -r requirements.txt`

### No puedo conectarme a la BD

- Asegurar que la carpeta `data/` existe y tiene permisos de lectura/escritura
- Verificar espacio disponible en disco

### Olvidé la contraseña

- Contactar al administrador del sistema
- El administrador puede restablecer la contraseña

## Contacto y Soporte

Para reportar problemas o solicitar asistencia:

- Email: soporte@empresa.com
- Teléfono: Extension IT
- Horario de atención: Lunes a Viernes, 8:00 AM - 5:00 PM

## Historial de Versiones

### v1.0.0 (Inicial)

- Registro y consulta de retiros
- Administración de cajas
- Administración de usuarios
- Reportes diarios, semanales y mensuales
- Exportación a PDF y Excel
