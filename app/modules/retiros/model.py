"""
app/modules/retiros/model.py

Modelo de datos para el módulo de retiros.
Maneja todas las operaciones de BD relacionadas con retiros.
"""

from app.db.connection import get_conn
from datetime import datetime, date
from typing import List, Dict, Optional


def obtener_retiros(solo_activos=True, fecha=None):
    """
    Obtiene todos los retiros, opcionalmente filtrados por fecha.
    
    Args:
        solo_activos (bool): Si True, solo retiros activos (no implementado aún)
        fecha (date): Fecha para filtrar retiros
    
    Returns:
        list: Lista de retiros con información de caja y usuario
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        query = """
            SELECT 
                r.id,
                r.monto,
                r.motivo,
                r.observaciones,
                r.fecha_retiro,
                r.fecha_registro,
                c.id as caja_id,
                c.nombre as nombre_caja,
                c.numero_caja,
                u.id as usuario_id,
                u.nombre as nombre_usuario,
                u.usuario as username
            FROM retiros r
            JOIN cajas c ON r.id_caja = c.id
            JOIN usuarios u ON r.id_usuario = u.id
        """
        
        params = []
        if fecha:
            query += " WHERE DATE(r.fecha_retiro) = DATE(?)"
            params.append(fecha.isoformat() if hasattr(fecha, 'isoformat') else fecha)
        
        query += " ORDER BY r.fecha_retiro DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def obtener_retiros_por_fecha(fecha):
    """
    Obtiene todos los retiros de una fecha específica.
    
    Args:
        fecha (datetime.date): Fecha a consultar.
    
    Returns:
        list: Lista de retiros en esa fecha.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                r.id,
                r.monto,
                r.motivo,
                r.observaciones,
                r.fecha_retiro,
                r.fecha_registro,
                c.nombre as nombre_caja,
                c.numero_caja,
                u.nombre as nombre_usuario,
                u.usuario as username
            FROM retiros r
            JOIN cajas c ON r.id_caja = c.id
            JOIN usuarios u ON r.id_usuario = u.id
            WHERE DATE(r.fecha_retiro) = DATE(?)
            ORDER BY r.fecha_retiro DESC
        """, (fecha.isoformat(),))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def obtener_retiros_por_caja_y_fecha(id_caja, fecha):
    """
    Obtiene retiros de una caja específica en una fecha.
    
    Args:
        id_caja (int): ID de la caja.
        fecha (datetime.date): Fecha a consultar.
    
    Returns:
        list: Lista de retiros filtrados.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                r.id,
                r.monto,
                r.motivo,
                r.observaciones,
                r.fecha_retiro,
                u.nombre as nombre_usuario,
                u.usuario as username
            FROM retiros r
            JOIN usuarios u ON r.id_usuario = u.id
            WHERE r.id_caja = ? AND DATE(r.fecha_retiro) = DATE(?)
            ORDER BY r.fecha_retiro DESC
        """, (id_caja, fecha.isoformat()))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def obtener_retiro_por_id(id_retiro):
    """
    Obtiene los detalles de un retiro específico.
    
    Args:
        id_retiro (int): ID del retiro.
    
    Returns:
        dict: Datos del retiro o None si no existe.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                r.*,
                c.nombre as nombre_caja,
                c.numero_caja,
                u.nombre as nombre_usuario,
                u.usuario as username
            FROM retiros r
            JOIN cajas c ON r.id_caja = c.id
            JOIN usuarios u ON r.id_usuario = u.id
            WHERE r.id = ? LIMIT 1
        """, (id_retiro,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insertar_retiro(id_usuario, id_caja, monto, motivo="", observaciones=""):
    """
    Inserta un nuevo retiro en la base de datos.
    
    Args:
        id_usuario (int): ID del usuario que registra el retiro.
        id_caja (int): ID de la caja donde se realiza el retiro.
        monto (float): Cantidad de dinero retirado.
        motivo (str): Razón o motivo del retiro.
        observaciones (str): Notas u observaciones adicionales.
    
    Returns:
        int: ID del retiro insertado.
    
    Raises:
        Exception: Si hay error en la BD.
    """
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
            motivo.strip() if motivo else "", 
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


def actualizar_retiro(id_retiro, monto, motivo, observaciones):
    """
    Actualiza los datos de un retiro existente.
    
    Args:
        id_retiro (int): ID del retiro a actualizar.
        monto (float): Nuevo monto.
        motivo (str): Nuevo motivo.
        observaciones (str): Nuevas observaciones.
    
    Returns:
        bool: True si se actualizó correctamente.
    
    Raises:
        Exception: Si hay error en la BD.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE retiros 
            SET monto = ?, motivo = ?, observaciones = ?, 
                fecha_modificacion = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (monto, motivo.strip(), observaciones.strip(), id_retiro))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def eliminar_retiro(id_retiro):
    """
    Elimina un retiro de la base de datos.
    
    Args:
        id_retiro (int): ID del retiro a eliminar.
    
    Returns:
        bool: True si se eliminó exitosamente.
    
    Raises:
        Exception: Si hay error en la BD.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM retiros WHERE id = ?", (id_retiro,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def obtener_total_diario(fecha=None):
    """
    Calcula el total de retiros en un día.
    
    Args:
        fecha (datetime.date): Fecha a consultar. Si None, usa hoy.
    
    Returns:
        float: Monto total de retiros en el día.
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total
            FROM retiros
            WHERE DATE(fecha_retiro) = DATE(?)
        """, (fecha.isoformat(),))
        row = cursor.fetchone()
        return float(row["total"]) if row else 0.0
    finally:
        conn.close()


def obtener_retiros_por_periodo(fecha_inicio, fecha_fin):
    """
    Obtiene retiros dentro de un rango de fechas.
    
    Args:
        fecha_inicio (datetime.date): Fecha inicial.
        fecha_fin (datetime.date): Fecha final (inclusive).
    
    Returns:
        list: Lista de retiros en el período.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                r.id,
                r.monto,
                r.motivo,
                r.observaciones,
                r.fecha_retiro,
                c.nombre as nombre_caja,
                u.nombre as nombre_usuario
            FROM retiros r
            JOIN cajas c ON r.id_caja = c.id
            JOIN usuarios u ON r.id_usuario = u.id
            WHERE DATE(r.fecha_retiro) BETWEEN DATE(?) AND DATE(?)
            ORDER BY r.fecha_retiro DESC
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def obtener_estadisticas_diarias(fecha=None):
    """
    Obtiene estadísticas completas del día.
    
    Args:
        fecha (datetime.date): Fecha a consultar.
    
    Returns:
        dict: Diccionario con total, cantidad, promedio, max, min.
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as cantidad,
                COALESCE(SUM(monto), 0) as total,
                COALESCE(AVG(monto), 0) as promedio,
                COALESCE(MAX(monto), 0) as maximo,
                COALESCE(MIN(monto), 0) as minimo
            FROM retiros
            WHERE DATE(fecha_retiro) = DATE(?)
        """, (fecha.isoformat(),))
        
        stats = dict(cursor.fetchone())
        stats["fecha"] = fecha.isoformat()
        
        # Estadísticas por caja
        cursor.execute("""
            SELECT 
                c.nombre,
                c.numero_caja,
                COALESCE(SUM(r.monto), 0) as total,
                COUNT(r.id) as cantidad
            FROM cajas c
            LEFT JOIN retiros r ON c.id = r.id_caja 
                AND DATE(r.fecha_retiro) = DATE(?)
            WHERE c.activa = 1
            GROUP BY c.id, c.nombre, c.numero_caja
            ORDER BY c.nombre
        """, (fecha.isoformat(),))
        
        stats["por_caja"] = [dict(row) for row in cursor.fetchall()]
        
        return stats
    finally:
        conn.close()