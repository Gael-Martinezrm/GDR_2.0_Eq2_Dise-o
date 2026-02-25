-- schema.sql
-- Esquema de la base de datos para Sistema de Retiros

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('administrador', 'gerente', 'operador')),
    activo INTEGER DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Cajas
CREATE TABLE IF NOT EXISTS cajas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    numero_caja TEXT NOT NULL,
    ubicacion TEXT,
    activa INTEGER DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Retiros
CREATE TABLE IF NOT EXISTS retiros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_caja INTEGER NOT NULL,
    monto REAL NOT NULL,
    motivo TEXT,
    fecha_retiro DATETIME NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_caja) REFERENCES cajas(id)
);

-- Tabla de Reportes Generados
CREATE TABLE IF NOT EXISTS reportes_generados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_reporte TEXT NOT NULL,
    periodo TEXT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    total_retiros REAL NOT NULL,
    cantidad_retiros INTEGER NOT NULL,
    ruta_archivo TEXT,
    formato TEXT,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_retiros_fecha ON retiros(fecha_retiro);
CREATE INDEX IF NOT EXISTS idx_retiros_caja ON retiros(id_caja);
CREATE INDEX IF NOT EXISTS idx_retiros_usuario ON retiros(id_usuario);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);
CREATE INDEX IF NOT EXISTS idx_cajas_activa ON cajas(activa);
