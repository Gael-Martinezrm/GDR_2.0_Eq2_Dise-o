"""
app/modules/retiros/model.py

Modelo de datos para el módulo de retiros.
Maneja todas las operaciones de BD relacionadas con retiros.
"""

from app.db.connection import get_conn
from datetime import datetime, date
from typing import List, Dict, Optional


def obtener_retiros(solo_activos=True, fecha=None):
    """Obtiene todos los retiros, opcionalmente filtrados por fecha."""
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
    """Obtiene todos los retiros de una fecha específica."""
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
    """Obtiene retiros de una caja específica en una fecha."""
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
    """Obtiene los detalles de un retiro específico."""
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
                c.id as caja_id,
                c.nombre as nombre_caja,
                c.numero_caja,
                u.id as usuario_id,
                u.nombre as nombre_usuario,
                u.usuario as username
            FROM retiros r
            LEFT JOIN cajas c ON r.id_caja = c.id
            LEFT JOIN usuarios u ON r.id_usuario = u.id
            WHERE r.id = ?
        """, (id_retiro,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def insertar_retiro(id_usuario, id_caja, monto, motivo="", observaciones=""):
    """Inserta un nuevo retiro en la base de datos."""
    # Validaciones de negocio
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Verificar que la caja existe y está activa
        cursor.execute("SELECT activa FROM cajas WHERE id = ?", (id_caja,))
        caja = cursor.fetchone()
        if not caja:
            raise ValueError(f"La caja con ID {id_caja} no existe")
        if not caja['activa']:
            raise ValueError("La caja está desactivada, no se pueden registrar retiros")
        
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
    except Exception as e:
        conn.rollback()
        if "FOREIGN KEY constraint failed" in str(e):
            raise Exception("El usuario o caja seleccionados no existen")
        raise e
    finally:
        conn.close()


def actualizar_retiro(id_retiro, monto, motivo, observaciones):
    """Actualiza los datos de un retiro existente."""
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE retiros 
            SET monto = ?, motivo = ?, observaciones = ? 
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
    """Elimina un retiro de la base de datos."""
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
    """Calcula el total de retiros en un día."""
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
    """Obtiene retiros dentro de un rango de fechas."""
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
    """Obtiene estadísticas completas del día."""
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