"""
app/db/connection.py

Gestión de conexión a la base de datos SQLite.
Proporciona función centralizada para obtener conexiones.
"""

import sqlite3
import os
from pathlib import Path


# Ruta de la base de datos
DB_PATH = Path(__file__).parent.parent.parent / "data" / "retiros.db"

# Ruta del esquema SQL
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_conn():
    """
    Obtiene una conexión a la base de datos SQLite.

    Returns:
        sqlite3.Connection: Conexión a la base de datos con row_factory configurado.
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
    Cierra la conexión a la base de datos.

    Args:
        conn (sqlite3.Connection): Conexión a cerrar.
    """
    if conn:
        conn.close()