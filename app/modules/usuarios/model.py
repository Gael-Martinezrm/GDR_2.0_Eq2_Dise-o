from app.db.connection import get_conn
from app.utils.helpers import hash_password, verify_password

def obtener_usuarios(solo_activos=True):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        if solo_activos:
            cursor.execute("SELECT id, nombre, usuario, rol, activo, fecha_creacion FROM usuarios WHERE activo = 1 ORDER BY nombre ASC")
        else:
            cursor.execute("SELECT id, nombre, usuario, rol, activo, fecha_creacion FROM usuarios ORDER BY nombre ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def obtener_usuario_por_id(id_usuario):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre, usuario, password_hash, rol, activo FROM usuarios WHERE id = ? LIMIT 1", (id_usuario,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def obtener_usuario_por_username(usuario):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre, usuario, password_hash, rol, activo FROM usuarios WHERE usuario = ? LIMIT 1", (usuario,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def insertar_usuario(nombre, usuario, password, rol):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nombre, usuario, password_hash, rol, activo) VALUES (?, ?, ?, ?, 1)", (nombre.strip(), usuario.strip(), hash_password(password), rol))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def actualizar_usuario(id_usuario, nombre, usuario, rol):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET nombre = ?, usuario = ?, rol = ?, fecha_modificacion = CURRENT_TIMESTAMP WHERE id = ?", (nombre.strip(), usuario.strip(), rol, id_usuario))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def cambiar_password(id_usuario, password_nueva):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET password_hash = ?, fecha_modificacion = CURRENT_TIMESTAMP WHERE id = ?", (hash_password(password_nueva), id_usuario))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def toggle_activo(id_usuario):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT activo FROM usuarios WHERE id = ?", (id_usuario,))
        row = cursor.fetchone()
        if row is None:
            raise Exception(f"Usuario con id {id_usuario} no encontrado.")
        nuevo_estado = 0 if row["activo"] else 1
        cursor.execute("UPDATE usuarios SET activo = ?, fecha_modificacion = CURRENT_TIMESTAMP WHERE id = ?", (nuevo_estado, id_usuario))
        conn.commit()
        return bool(nuevo_estado)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def eliminar_usuario(id_usuario):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def verificar_password(id_usuario, password):
    usuario = obtener_usuario_por_id(id_usuario)
    if usuario is None:
        return False
    return verify_password(password, usuario["password_hash"])
