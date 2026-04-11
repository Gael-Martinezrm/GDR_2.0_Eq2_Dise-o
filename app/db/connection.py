"""
app/db/connection.py

Gestion de conexion a la base de datos SQLite.
Proporciona funcion centralizada para obtener conexiones.
"""

import sqlite3
import sys
import os
from pathlib import Path


def _get_base_dir() -> Path:
    """
    Devuelve la carpeta raiz donde vive el ejecutable (o el proyecto en dev).

    - En desarrollo normal: carpeta raiz del proyecto (3 niveles arriba de este archivo)
    - Dentro del .exe generado por PyInstaller: carpeta donde esta SistemaRetiros.exe
    """
    if getattr(sys, "frozen", False):
        # Ejecutando como .exe — sys.executable es la ruta al .exe
        return Path(sys.executable).parent
    else:
        # Ejecutando como script Python normal
        return Path(__file__).parent.parent.parent


BASE_DIR = _get_base_dir()

# Ruta de la base de datos — siempre junto al ejecutable en data/retiros.db
DB_PATH = BASE_DIR / "data" / "retiros.db"

# Ruta del esquema SQL — empaquetado dentro del exe en app/db/schema.sql
if getattr(sys, "frozen", False):
    SCHEMA_PATH = Path(sys._MEIPASS) / "app" / "db" / "schema.sql"
else:
    SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_conn():
    """
    Obtiene una conexion a la base de datos SQLite.

    Returns:
        sqlite3.Connection: Conexion a la base de datos con row_factory configurado.
    """
    # Crear directorio data si no existe
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Inicializa la base de datos creando las tablas si no existen.

    Lee el archivo schema.sql y ejecuta los comandos para crear las tablas.
    Luego ejecuta seed() para cargar datos iniciales.
    """
    conn = get_conn()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

    # Cargar datos iniciales (usuario admin + cajas base)
    from app.db.seed import seed
    seed()


def close_conn(conn):
    """
    Cierra la conexion a la base de datos.

    Args:
        conn (sqlite3.Connection): Conexion a cerrar.
    """
    if conn:
        conn.close()