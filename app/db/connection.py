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
    return conn


def init_db():
    """
    Inicializa la base de datos creando las tablas si no existen.

    Lee el archivo schema.sql y ejecuta los comandos para crear las tablas.
    Luego ejecuta seed.py para cargar datos iniciales.
    """
    # TODO: Implementar inicialización de la BD
    # 1. Leer schema.sql
    # 2. Ejecutar CREATE TABLE IF NOT EXISTS
    # 3. Llamar a seed() para datos iniciales
    pass


def close_conn(conn):
    """
    Cierra la conexión a la base de datos.

    Args:
        conn (sqlite3.Connection): Conexión a cerrar.
    """
    if conn:
        conn.close()
