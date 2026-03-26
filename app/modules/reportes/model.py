"""
app/modules/reportes/model.py

Modelo de datos para el módulo de reportes.
Maneja cálculos y agregaciones de datos para reportes.
"""

from app.db.connection import get_conn
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from app.utils.helpers import (
    get_fecha_inicio_semana,
    get_fecha_fin_semana,
    get_fecha_inicio_mes,
    get_fecha_fin_mes
)


def total_diario(fecha: Optional[date] = None) -> float:
    """
    Calcula el total de retiros para un día específico.
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
        return float(row['total']) if row else 0.0
    finally:
        conn.close()


def total_semanal(fecha_fin: Optional[date] = None) -> float:
    """
    Calcula el total de retiros de la semana.
    """
    if fecha_fin is None:
        fecha_fin = date.today()
    
    fecha_inicio = get_fecha_inicio_semana(fecha_fin)
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        row = cursor.fetchone()
        return float(row['total']) if row else 0.0
    finally:
        conn.close()


def total_mensual(fecha: Optional[date] = None) -> float:
    """
    Calcula el total de retiros del mes.
    """
    if fecha is None:
        fecha = date.today()
    
    fecha_inicio = get_fecha_inicio_mes(fecha)
    fecha_fin = get_fecha_fin_mes(fecha)
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        row = cursor.fetchone()
        return float(row['total']) if row else 0.0
    finally:
        conn.close()


def total_por_caja_diario(fecha: Optional[date] = None) -> List[Dict]:
    """
    Calcula el total de retiros por caja para un día.
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.nombre as nombre_caja,
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
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def total_por_caja_semanal(fecha_fin: Optional[date] = None) -> List[Dict]:
    """
    Calcula el total de retiros por caja para la semana.
    """
    if fecha_fin is None:
        fecha_fin = date.today()
    
    fecha_inicio = get_fecha_inicio_semana(fecha_fin)
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.nombre as nombre_caja,
                c.numero_caja,
                COALESCE(SUM(r.monto), 0) as total,
                COUNT(r.id) as cantidad
            FROM cajas c
            LEFT JOIN retiros r ON c.id = r.id_caja 
                AND DATE(r.fecha_retiro) BETWEEN ? AND ?
            WHERE c.activa = 1
            GROUP BY c.id, c.nombre, c.numero_caja
            ORDER BY c.nombre
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def total_por_caja_mensual(fecha: Optional[date] = None) -> List[Dict]:
    """
    Calcula el total de retiros por caja para el mes.
    """
    if fecha is None:
        fecha = date.today()
    
    fecha_inicio = get_fecha_inicio_mes(fecha)
    fecha_fin = get_fecha_fin_mes(fecha)
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.nombre as nombre_caja,
                c.numero_caja,
                COALESCE(SUM(r.monto), 0) as total,
                COUNT(r.id) as cantidad
            FROM cajas c
            LEFT JOIN retiros r ON c.id = r.id_caja 
                AND DATE(r.fecha_retiro) BETWEEN ? AND ?
            WHERE c.activa = 1
            GROUP BY c.id, c.nombre, c.numero_caja
            ORDER BY c.nombre
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def retiros_por_periodo(fecha_inicio: date, fecha_fin: date) -> List[Dict]:
    """
    Obtiene detalle de todos los retiros en un período.
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
            WHERE DATE(r.fecha_retiro) BETWEEN DATE(?) AND DATE(?)
            ORDER BY r.fecha_retiro ASC
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def cantidad_retiros_diarios(fecha: Optional[date] = None) -> int:
    """
    Cuenta la cantidad de retiros en un día.
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) as cantidad
            FROM retiros
            WHERE DATE(fecha_retiro) = DATE(?)
        """, (fecha.isoformat(),))
        row = cursor.fetchone()
        return int(row['cantidad']) if row else 0
    finally:
        conn.close()


def promedio_retiros_diarios(fecha: Optional[date] = None) -> float:
    """
    Calcula el monto promedio de retiros en un día.
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(AVG(monto), 0) as promedio
            FROM retiros
            WHERE DATE(fecha_retiro) = DATE(?)
        """, (fecha.isoformat(),))
        row = cursor.fetchone()
        return float(row['promedio']) if row else 0.0
    finally:
        conn.close()


def registrar_reporte_generado(tipo_reporte: str, periodo: str, 
                               fecha_inicio: date, fecha_fin: date,
                               total_retiros: float, cantidad_retiros: int, 
                               ruta_archivo: str, formato: str) -> int:
    """
    Registra un reporte generado en la BD.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO reportes_generados 
            (tipo_reporte, periodo, fecha_inicio, fecha_fin, total_retiros, 
             cantidad_retiros, ruta_archivo, formato)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tipo_reporte, periodo, fecha_inicio.isoformat(), fecha_fin.isoformat(),
              total_retiros, cantidad_retiros, ruta_archivo, formato))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()