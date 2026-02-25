"""
app/db/seed.py

Carga de datos iniciales en la base de datos.
Inserta usuario admin y cajas iniciales si no existen.
"""

from app.db.connection import get_conn
from app.utils.helpers import hash_password


def seed():
    """
    Carga datos iniciales en la base de datos.

    Crea:
    - Usuario administrador por defecto (admin/admin123)
    - 3 cajas iniciales (Caja 1, Caja 2, Caja 3)

    Solo inserta si los registros no existen.
    """
    conn = get_conn()
    cursor = conn.cursor()

    try:
        # Verificar e insertar usuario admin si no existe
        cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", ("admin",))
        if cursor.fetchone() is None:
            password_hash = hash_password("admin123")
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, usuario, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("Administrador", "admin", password_hash, "administrador", 1)
            )

        # Verificar e insertar cajas iniciales
        cajas_iniciales = [
            ("Caja 1", "001", "Mostrador Principal"),
            ("Caja 2", "002", "Mostrador Secundario"),
            ("Caja 3", "003", "Oficina Administrativa")
        ]

        for nombre, numero, ubicacion in cajas_iniciales:
            cursor.execute("SELECT id FROM cajas WHERE nombre = ?", (nombre,))
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    INSERT INTO cajas (nombre, numero_caja, ubicacion, activa)
                    VALUES (?, ?, ?, ?)
                    """,
                    (nombre, numero, ubicacion, 1)
                )

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Error en seed: {e}")
        raise

    finally:
        conn.close()
