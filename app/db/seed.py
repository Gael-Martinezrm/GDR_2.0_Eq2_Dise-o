"""
app/db/seed.py

Carga de datos iniciales en la base de datos.
Inserta usuarios iniciales (admin, operador, gerente) y cajas si no existen.
"""

from app.db.connection import get_conn
from app.utils.helpers import hash_password


def seed():
    """
    Carga datos iniciales en la base de datos.

    Crea:
    - Usuario administrador por defecto (admin/admin123)
    - Usuario operador por defecto (operador/operador123)
    - Usuario gerente por defecto (gerente/gerente123)
    - 3 cajas iniciales (Caja 1, Caja 2, Caja 3)

    Solo inserta si los registros no existen. Pueden eliminarse después.
    """
    conn = get_conn()
    cursor = conn.cursor()

    try:
        # Usuarios iniciales: (nombre_completo, usuario, password, rol)
        usuarios_iniciales = [
            ("Administrador", "admin",    "admin123",    "administrador"),
            ("Operador",      "operador", "operador123", "operador"),
            ("Gerente",       "gerente",  "gerente123",  "gerente"),
        ]

        for nombre, usuario, password, rol in usuarios_iniciales:
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))
            if cursor.fetchone() is None:
                password_hash = hash_password(password)
                cursor.execute(
                    """
                    INSERT INTO usuarios (nombre, usuario, password_hash, rol, activo)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (nombre, usuario, password_hash, rol, 1)
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
