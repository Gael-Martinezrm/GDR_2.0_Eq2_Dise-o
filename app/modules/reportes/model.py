"""
app/modules/reportes/model.py

Modelo de datos para el módulo de reportes.
Maneja cálculos y agregaciones de datos para reportes.
"""

from app.db.connection import get_conn
from datetime import datetime, timedelta


def total_diario(fecha=None):
    if fecha is None:
        fecha = datetime.now().date()
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto), 0) AS total FROM retiros WHERE DATE(fecha_retiro) = ?",
            (fecha.strftime("%Y-%m-%d"),)
        ).fetchone()
        return float(row["total"])
    finally:
        conn.close()


def total_semanal(fecha_fin=None):
    if fecha_fin is None:
        fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=6)
    conn = get_conn()
    try:
        row = conn.execute(
            """SELECT COALESCE(SUM(monto), 0) AS total
               FROM retiros WHERE DATE(fecha_retiro) BETWEEN ? AND ?""",
            (fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"))
        ).fetchone()
        return float(row["total"])
    finally:
        conn.close()


def total_mensual(fecha=None):
    if fecha is None:
        fecha = datetime.now().date()
    conn = get_conn()
    try:
        row = conn.execute(
            """SELECT COALESCE(SUM(monto), 0) AS total
               FROM retiros WHERE strftime('%Y-%m', fecha_retiro) = ?""",
            (fecha.strftime("%Y-%m"),)
        ).fetchone()
        return float(row["total"])
    finally:
        conn.close()


def total_por_caja_diario(fecha=None):
    if fecha is None:
        fecha = datetime.now().date()
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT c.nombre AS nombre_caja,
                      COALESCE(SUM(r.monto), 0) AS total
               FROM cajas c
               LEFT JOIN retiros r ON r.id_caja = c.id
                     AND DATE(r.fecha_retiro) = ?
               GROUP BY c.id, c.nombre ORDER BY c.numero_caja""",
            (fecha.strftime("%Y-%m-%d"),)
        ).fetchall()
        return [{"nombre_caja": row["nombre_caja"], "total": float(row["total"])} for row in rows]
    finally:
        conn.close()


def total_por_caja_semanal(fecha_fin=None):
    if fecha_fin is None:
        fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=6)
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT c.nombre AS nombre_caja,
                      COALESCE(SUM(r.monto), 0) AS total
               FROM cajas c
               LEFT JOIN retiros r ON r.id_caja = c.id
                     AND DATE(r.fecha_retiro) BETWEEN ? AND ?
               GROUP BY c.id, c.nombre ORDER BY c.numero_caja""",
            (fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"))
        ).fetchall()
        return [{"nombre_caja": row["nombre_caja"], "total": float(row["total"])} for row in rows]
    finally:
        conn.close()


def total_por_caja_mensual(fecha=None):
    if fecha is None:
        fecha = datetime.now().date()
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT c.nombre AS nombre_caja,
                      COALESCE(SUM(r.monto), 0) AS total
               FROM cajas c
               LEFT JOIN retiros r ON r.id_caja = c.id
                     AND strftime('%Y-%m', r.fecha_retiro) = ?
               GROUP BY c.id, c.nombre ORDER BY c.numero_caja""",
            (fecha.strftime("%Y-%m"),)
        ).fetchall()
        return [{"nombre_caja": row["nombre_caja"], "total": float(row["total"])} for row in rows]
    finally:
        conn.close()


def retiros_por_periodo(fecha_inicio, fecha_fin):
    """
    Obtiene detalle de todos los retiros en un período.

    Returns:
        list[dict]: claves → numero_transaccion, importe, nombre_caja, usuario, fecha
    """
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT r.id           AS numero_transaccion,
                      r.monto        AS importe,
                      c.nombre       AS nombre_caja,
                      u.usuario      AS usuario,
                      strftime('%Y-%m-%d', r.fecha_retiro) AS fecha
               FROM retiros  r
               JOIN cajas    c ON c.id = r.id_caja
               JOIN usuarios u ON u.id = r.id_usuario
               WHERE DATE(r.fecha_retiro) BETWEEN ? AND ?
               ORDER BY r.fecha_retiro""",
            (fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"))
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def cantidad_retiros_diarios(fecha=None):
    if fecha is None:
        fecha = datetime.now().date()
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM retiros WHERE DATE(fecha_retiro) = ?",
            (fecha.strftime("%Y-%m-%d"),)
        ).fetchone()
        return int(row["cnt"])
    finally:
        conn.close()


def promedio_retiros_diarios(fecha=None):
    if fecha is None:
        fecha = datetime.now().date()
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT COALESCE(AVG(monto), 0) AS promedio FROM retiros WHERE DATE(fecha_retiro) = ?",
            (fecha.strftime("%Y-%m-%d"),)
        ).fetchone()
        return float(row["promedio"])
    finally:
        conn.close()


def registrar_reporte_generado(tipo_reporte, periodo, fecha_inicio, fecha_fin,
                               total_retiros, cantidad_retiros, ruta_archivo, formato):
    """
    Registra un reporte generado en la BD.

    Returns:
        int: ID del reporte registrado.
    """
    conn = get_conn()
    try:
        cursor = conn.execute(
            """INSERT INTO reportes_generados
                   (tipo_reporte, periodo, fecha_inicio, fecha_fin,
                    total_retiros, cantidad_retiros, ruta_archivo, formato)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                tipo_reporte,
                periodo,
                fecha_inicio.strftime("%Y-%m-%d"),
                fecha_fin.strftime("%Y-%m-%d"),
                total_retiros,
                cantidad_retiros,
                ruta_archivo,
                formato,
            )
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()