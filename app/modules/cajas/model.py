from app.db.connection import get_conn

def obtener_cajas(solo_activas=True):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        if solo_activas:
            cursor.execute("SELECT * FROM cajas WHERE activa = 1 ORDER BY numero_caja ASC")
        else:
            cursor.execute("SELECT * FROM cajas ORDER BY numero_caja ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def obtener_caja_por_id(id_caja):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM cajas WHERE id = ? LIMIT 1", (id_caja,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def insertar_caja(nombre, numero_caja, ubicacion=""):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cajas (nombre, numero_caja, ubicacion, activa) VALUES (?, ?, ?, 1)", (nombre.strip(), numero_caja.strip(), ubicacion.strip()))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def actualizar_caja(id_caja, nombre, numero_caja, ubicacion):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE cajas SET nombre = ?, numero_caja = ?, ubicacion = ?, fecha_modificacion = CURRENT_TIMESTAMP WHERE id = ?", (nombre.strip(), numero_caja.strip(), ubicacion.strip(), id_caja))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def toggle_activa(id_caja):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT activa FROM cajas WHERE id = ?", (id_caja,))
        row = cursor.fetchone()
        if row is None:
            raise Exception(f"Caja con id {id_caja} no encontrada.")
        nuevo_estado = 0 if row["activa"] else 1
        cursor.execute("UPDATE cajas SET activa = ?, fecha_modificacion = CURRENT_TIMESTAMP WHERE id = ?", (nuevo_estado, id_caja))
        conn.commit()
        return bool(nuevo_estado)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def eliminar_caja(id_caja):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cajas WHERE id = ?", (id_caja,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
