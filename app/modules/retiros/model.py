"""
app/modules/retiros/model.py
"""

from app.db.connection import get_conn
from datetime import datetime, date

def obtener_retiros_por_fecha(fecha):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                r.id,
                r.id as num_retiro,
                'TRX-' || r.id as num_transaccion,
                STRFTIME('%d/%m/%Y', r.fecha_retiro) as fecha_solo,
                STRFTIME('%H:%M:%S', r.fecha_retiro) as hora_deposito,
                r.monto,
                SUM(r.monto) OVER (
                    ORDER BY r.fecha_retiro ASC 
                ) as acumulado,
                r.motivo,
                r.observaciones,
                c.nombre as nombre_caja,
                u.nombre as nombre_usuario
            FROM retiros r
            JOIN cajas c ON r.id_caja = c.id
            JOIN usuarios u ON r.id_usuario = u.id
            WHERE DATE(r.fecha_retiro) = DATE(?)
            ORDER BY r.fecha_retiro DESC
        """, (fecha.isoformat() if hasattr(fecha, 'isoformat') else fecha,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def obtener_retiros_por_caja_y_fecha(id_caja, fecha):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                r.id,
                r.id as num_retiro,
                'TRX-' || r.id as num_transaccion,
                STRFTIME('%H:%M:%S', r.fecha_retiro) as hora_deposito,
                r.monto,
                SUM(r.monto) OVER (ORDER BY r.fecha_retiro ASC) as acumulado,
                r.motivo,
                r.observaciones,
                r.fecha_retiro,
                u.nombre as nombre_usuario
            FROM retiros r
            JOIN usuarios u ON r.id_usuario = u.id
            WHERE r.id_caja = ? AND DATE(r.fecha_retiro) = DATE(?)
            ORDER BY r.fecha_retiro DESC
        """, (id_caja, fecha.isoformat() if hasattr(fecha, 'isoformat') else fecha))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def obtener_retiro_por_id(id_retiro):
    """ Obtiene detalle de un retiro con su formato formal de transacción. """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                r.*,
                'TRX-' || r.id as num_transaccion,
                STRFTIME('%H:%M:%S', r.fecha_retiro) as hora_deposito,
                STRFTIME('%d/%m/%Y', r.fecha_retiro) as fecha_solo,
                c.nombre as nombre_caja,
                u.nombre as nombre_usuario
            FROM retiros r
            JOIN cajas c ON r.id_caja = c.id
            JOIN usuarios u ON r.id_usuario = u.id
            WHERE r.id = ?
        """, (id_retiro,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insertar_retiro(id_usuario, id_caja, monto, motivo="", observaciones=""):
    """ Inserta un retiro y retorna el ID autoincrementable. """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO retiros 
            (id_usuario, id_caja, monto, motivo, fecha_retiro, observaciones) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            id_usuario,
            id_caja,
            monto,
            motivo.strip() if motivo else "Retiro de efectivo",
            datetime.now(),
            observaciones.strip() if observaciones else ""
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def actualizar_retiro(id_retiro, id_caja, monto, motivo="", observaciones=""):
    """ Actualiza los datos editables de un retiro existente. """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE retiros
            SET id_caja       = ?,
                monto         = ?,
                motivo        = ?,
                observaciones = ?
            WHERE id = ?
        """, (
            id_caja,
            monto,
            motivo.strip() if motivo else "Retiro de efectivo",
            observaciones.strip() if observaciones else "",
            id_retiro
        ))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def eliminar_retiro(id_retiro):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM retiros WHERE id = ?", (id_retiro,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def obtener_estadisticas_diarias(fecha=None):
    if fecha is None: fecha = date.today()
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as cantidad,
                COALESCE(SUM(monto), 0) as total,
                COALESCE(AVG(monto), 0) as promedio
            FROM retiros
            WHERE DATE(fecha_retiro) = DATE(?)
        """, (fecha.isoformat(),))
        return dict(cursor.fetchone())
    finally:
        conn.close()