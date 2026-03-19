"""
app/modules/calculos/totales.py

Funciones de cálculo de totales y agregaciones.
Proporciona todas las funciones necesarias para el dashboard y reportes.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Tuple, Union
from app.db.connection import get_conn
from app.utils.helpers import (
    get_fecha_inicio_semana,
    get_fecha_fin_semana,
    get_fecha_inicio_mes,
    get_fecha_fin_mes
)


# ============================================================================
# FUNCIONES DE CÁLCULO DIARIO
# ============================================================================

def calcular_acumulado_dia(fecha: Optional[date] = None) -> float:
    """
    Calcula el acumulado total de retiros para un día.
    
    Args:
        fecha (datetime.date): Fecha a calcular. Si None, usa hoy.
    
    Returns:
        float: Monto total acumulado en el día
    
    Examples:
        >>> total_hoy = calcular_acumulado_dia()
        >>> print(f"Total hoy: ${total_hoy:,.2f}")
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


def calcular_acumulado_por_caja_dia(fecha: Optional[date] = None) -> List[Dict]:
    """
    Calcula el acumulado de retiros por caja para un día.
    
    Args:
        fecha (datetime.date): Fecha a calcular. Si None, usa hoy.
    
    Returns:
        list: Lista de diccionarios con:
            - id: ID de la caja
            - nombre: Nombre de la caja
            - numero_caja: Número de caja
            - total: Total acumulado en la caja
            - cantidad: Número de retiros en la caja
            - promedio: Promedio por retiro en la caja
    
    Examples:
        >>> distribucion = calcular_acumulado_por_caja_dia()
        >>> for caja in distribucion:
        ...     print(f"{caja['nombre']}: ${caja['total']:,.2f}")
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.id,
                c.nombre,
                c.numero_caja,
                COALESCE(SUM(r.monto), 0) as total,
                COUNT(r.id) as cantidad,
                COALESCE(AVG(r.monto), 0) as promedio
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


def calcular_promedio_por_retiro_dia(fecha: Optional[date] = None) -> float:
    """
    Calcula el promedio por retiro en un día.
    
    Args:
        fecha (datetime.date): Fecha a calcular. Si None, usa hoy.
    
    Returns:
        float: Promedio de monto por retiro (0 si no hay retiros)
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


def contar_retiros_dia(fecha: Optional[date] = None) -> int:
    """
    Cuenta la cantidad de retiros en un día.
    
    Args:
        fecha (datetime.date): Fecha a contar. Si None, usa hoy.
    
    Returns:
        int: Número de retiros
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


def obtener_monto_maximo_dia(fecha: Optional[date] = None) -> float:
    """
    Obtiene el retiro más grande del día.
    
    Args:
        fecha (datetime.date): Fecha a consultar. Si None, usa hoy.
    
    Returns:
        float: Monto del retiro más grande (0 si no hay retiros)
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(MAX(monto), 0) as maximo
            FROM retiros
            WHERE DATE(fecha_retiro) = DATE(?)
        """, (fecha.isoformat(),))
        
        row = cursor.fetchone()
        return float(row['maximo']) if row else 0.0
    finally:
        conn.close()


def obtener_monto_minimo_dia(fecha: Optional[date] = None) -> float:
    """
    Obtiene el retiro más pequeño del día.
    
    Args:
        fecha (datetime.date): Fecha a consultar. Si None, usa hoy.
    
    Returns:
        float: Monto del retiro más pequeño (0 si no hay retiros)
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(MIN(monto), 0) as minimo
            FROM retiros
            WHERE DATE(fecha_retiro) = DATE(?)
        """, (fecha.isoformat(),))
        
        row = cursor.fetchone()
        return float(row['minimo']) if row else 0.0
    finally:
        conn.close()


def obtener_estadisticas_completas_dia(fecha: Optional[date] = None) -> Dict:
    """
    Obtiene todas las estadísticas del día en un solo diccionario.
    
    Args:
        fecha (datetime.date): Fecha a calcular. Si None, usa hoy.
    
    Returns:
        dict: Diccionario con todas las estadísticas del día:
            - fecha: Fecha consultada
            - total: Suma de retiros
            - cantidad: Número de retiros
            - promedio: Promedio por retiro
            - maximo: Retiro más grande
            - minimo: Retiro más pequeño
            - por_caja: Lista de estadísticas por caja
    
    Examples:
        >>> stats = obtener_estadisticas_completas_dia()
        >>> print(f"Día: {stats['fecha']}")
        >>> print(f"Total: ${stats['total']:,.2f}")
        >>> print(f"Cantidad: {stats['cantidad']}")
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Estadísticas generales
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
        stats['fecha'] = fecha.isoformat()
        
        # Estadísticas por caja
        cursor.execute("""
            SELECT 
                c.nombre,
                c.numero_caja,
                COALESCE(SUM(r.monto), 0) as total,
                COUNT(r.id) as cantidad,
                COALESCE(AVG(r.monto), 0) as promedio
            FROM cajas c
            LEFT JOIN retiros r ON c.id = r.id_caja 
                AND DATE(r.fecha_retiro) = DATE(?)
            WHERE c.activa = 1
            GROUP BY c.id, c.nombre, c.numero_caja
            ORDER BY c.nombre
        """, (fecha.isoformat(),))
        
        stats['por_caja'] = [dict(row) for row in cursor.fetchall()]
        
        return stats
        
    finally:
        conn.close()


# ============================================================================
# FUNCIONES DE CÁLCULO SEMANAL
# ============================================================================

def calcular_total_semana(fecha_fin: Optional[date] = None) -> float:
    """
    Calcula el total de retiros de la semana.
    
    Args:
        fecha_fin (datetime.date): Última fecha de la semana. Si None, usa hoy.
    
    Returns:
        float: Monto total de la semana
    
    Examples:
        >>> total_semana = calcular_total_semana()
        >>> print(f"Total semana: ${total_semana:,.2f}")
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


def calcular_total_por_caja_semana(fecha_fin: Optional[date] = None) -> List[Dict]:
    """
    Calcula el total de retiros por caja para la semana.
    
    Args:
        fecha_fin (datetime.date): Última fecha de la semana. Si None, usa hoy.
    
    Returns:
        list: Lista de diccionarios con nombre_caja y total
    """
    if fecha_fin is None:
        fecha_fin = date.today()
    
    fecha_inicio = get_fecha_inicio_semana(fecha_fin)
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.nombre,
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


def contar_retiros_semana(fecha_fin: Optional[date] = None) -> int:
    """
    Cuenta la cantidad de retiros en la semana.
    
    Args:
        fecha_fin (datetime.date): Última fecha de la semana. Si None, usa hoy.
    
    Returns:
        int: Número de retiros
    """
    if fecha_fin is None:
        fecha_fin = date.today()
    
    fecha_inicio = get_fecha_inicio_semana(fecha_fin)
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) as cantidad
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        
        row = cursor.fetchone()
        return int(row['cantidad']) if row else 0
    finally:
        conn.close()


def calcular_promedio_semana(fecha_fin: Optional[date] = None) -> float:
    """
    Calcula el promedio de retiros por día en la semana.
    
    Args:
        fecha_fin (datetime.date): Última fecha de la semana. Si None, usa hoy.
    
    Returns:
        float: Promedio diario de la semana
    """
    if fecha_fin is None:
        fecha_fin = date.today()
    
    fecha_inicio = get_fecha_inicio_semana(fecha_fin)
    dias_semana = 7
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        
        row = cursor.fetchone()
        total = float(row['total']) if row else 0.0
        return total / dias_semana
    finally:
        conn.close()


def obtener_resumen_semanal(fecha_fin: Optional[date] = None) -> Dict:
    """
    Obtiene un resumen completo de la semana.
    
    Args:
        fecha_fin (datetime.date): Última fecha de la semana. Si None, usa hoy.
    
    Returns:
        dict: Resumen con:
            - fecha_inicio: Inicio de la semana
            - fecha_fin: Fin de la semana
            - total: Total de la semana
            - cantidad: Número de retiros
            - promedio_diario: Promedio por día
            - por_dia: Lista de totales por día
            - por_caja: Lista de totales por caja
    """
    if fecha_fin is None:
        fecha_fin = date.today()
    
    fecha_inicio = get_fecha_inicio_semana(fecha_fin)
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Resumen general
        cursor.execute("""
            SELECT 
                COUNT(*) as cantidad,
                COALESCE(SUM(monto), 0) as total
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        
        resumen = dict(cursor.fetchone())
        resumen['fecha_inicio'] = fecha_inicio.isoformat()
        resumen['fecha_fin'] = fecha_fin.isoformat()
        resumen['promedio_diario'] = resumen['total'] / 7
        
        # Desglose por día
        cursor.execute("""
            SELECT 
                DATE(fecha_retiro) as dia,
                COUNT(*) as cantidad,
                COALESCE(SUM(monto), 0) as total
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
            GROUP BY DATE(fecha_retiro)
            ORDER BY dia
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        
        resumen['por_dia'] = [dict(row) for row in cursor.fetchall()]
        
        # Por caja
        resumen['por_caja'] = calcular_total_por_caja_semana(fecha_fin)
        
        return resumen
        
    finally:
        conn.close()


# ============================================================================
# FUNCIONES DE CÁLCULO MENSUAL
# ============================================================================

def calcular_total_mes(fecha: Optional[date] = None) -> float:
    """
    Calcula el total de retiros del mes.
    
    Args:
        fecha (datetime.date): Fecha dentro del mes. Si None, usa hoy.
    
    Returns:
        float: Monto total del mes
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


def calcular_total_por_caja_mes(fecha: Optional[date] = None) -> List[Dict]:
    """
    Calcula el total de retiros por caja para el mes.
    
    Args:
        fecha (datetime.date): Fecha dentro del mes. Si None, usa hoy.
    
    Returns:
        list: Lista de diccionarios con nombre_caja y total
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
                c.nombre,
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


def contar_retiros_mes(fecha: Optional[date] = None) -> int:
    """
    Cuenta la cantidad de retiros en el mes.
    
    Args:
        fecha (datetime.date): Fecha dentro del mes. Si None, usa hoy.
    
    Returns:
        int: Número de retiros
    """
    if fecha is None:
        fecha = date.today()
    
    fecha_inicio = get_fecha_inicio_mes(fecha)
    fecha_fin = get_fecha_fin_mes(fecha)
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) as cantidad
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        
        row = cursor.fetchone()
        return int(row['cantidad']) if row else 0
    finally:
        conn.close()


def calcular_promedio_mes(fecha: Optional[date] = None) -> float:
    """
    Calcula el promedio de retiros por día en el mes.
    
    Args:
        fecha (datetime.date): Fecha dentro del mes. Si None, usa hoy.
    
    Returns:
        float: Promedio diario del mes
    """
    if fecha is None:
        fecha = date.today()
    
    fecha_inicio = get_fecha_inicio_mes(fecha)
    fecha_fin = get_fecha_fin_mes(fecha)
    dias_mes = (fecha_fin - fecha_inicio).days + 1
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        
        row = cursor.fetchone()
        total = float(row['total']) if row else 0.0
        return total / dias_mes
    finally:
        conn.close()


def obtener_resumen_mensual(fecha: Optional[date] = None) -> Dict:
    """
    Obtiene un resumen completo del mes.
    
    Args:
        fecha (datetime.date): Fecha dentro del mes. Si None, usa hoy.
    
    Returns:
        dict: Resumen con:
            - mes: Nombre del mes
            - año: Año
            - fecha_inicio: Inicio del mes
            - fecha_fin: Fin del mes
            - total: Total del mes
            - cantidad: Número de retiros
            - promedio_diario: Promedio por día
            - por_semana: Lista de totales por semana
            - por_caja: Lista de totales por caja
    """
    if fecha is None:
        fecha = date.today()
    
    fecha_inicio = get_fecha_inicio_mes(fecha)
    fecha_fin = get_fecha_fin_mes(fecha)
    dias_mes = (fecha_fin - fecha_inicio).days + 1
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Resumen general
        cursor.execute("""
            SELECT 
                COUNT(*) as cantidad,
                COALESCE(SUM(monto), 0) as total
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        
        resumen = dict(cursor.fetchone())
        resumen['mes'] = fecha.strftime("%B")
        resumen['año'] = fecha.year
        resumen['fecha_inicio'] = fecha_inicio.isoformat()
        resumen['fecha_fin'] = fecha_fin.isoformat()
        resumen['promedio_diario'] = resumen['total'] / dias_mes
        
        # Por semana (aproximado por semana natural)
        resumen['por_semana'] = []
        semana_actual = fecha_inicio
        semana_num = 1
        
        while semana_actual <= fecha_fin:
            semana_fin = min(semana_actual + timedelta(days=6), fecha_fin)
            
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0) as total,
                       COUNT(*) as cantidad
                FROM retiros
                WHERE DATE(fecha_retiro) BETWEEN ? AND ?
            """, (semana_actual.isoformat(), semana_fin.isoformat()))
            
            semana_data = cursor.fetchone()
            
            resumen['por_semana'].append({
                'semana': semana_num,
                'inicio': semana_actual.isoformat(),
                'fin': semana_fin.isoformat(),
                'total': semana_data['total'],
                'cantidad': semana_data['cantidad']
            })
            
            semana_actual = semana_fin + timedelta(days=1)
            semana_num += 1
        
        # Por caja
        resumen['por_caja'] = calcular_total_por_caja_mes(fecha)
        
        return resumen
        
    finally:
        conn.close()


# ============================================================================
# FUNCIONES DE ACUMULADO HISTÓRICO
# ============================================================================

def calcular_acumulado_hasta_fecha(fecha: Optional[date] = None) -> float:
    """
    Calcula el acumulado total histórico hasta una fecha.
    
    Args:
        fecha (datetime.date): Fecha límite. Si None, usa hoy.
    
    Returns:
        float: Acumulado total desde el inicio hasta la fecha
    
    Examples:
        >>> acumulado = calcular_acumulado_hasta_fecha()
        >>> print(f"Total histórico: ${acumulado:,.2f}")
    """
    if fecha is None:
        fecha = date.today()
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as acumulado
            FROM retiros
            WHERE DATE(fecha_retiro) <= ?
        """, (fecha.isoformat(),))
        
        row = cursor.fetchone()
        return float(row['acumulado']) if row else 0.0
    finally:
        conn.close()


def calcular_serie_temporal(fecha_inicio: date, fecha_fin: date, 
                           intervalo: str = 'dia') -> List[Dict]:
    """
    Calcula una serie temporal de totales para un período.
    
    Args:
        fecha_inicio (date): Fecha inicial
        fecha_fin (date): Fecha final
        intervalo (str): 'dia', 'semana', 'mes'
    
    Returns:
        list: Lista de puntos con fecha y total
    
    Examples:
        >>> serie = calcular_serie_temporal(
        ...     date(2026, 3, 1),
        ...     date(2026, 3, 31),
        ...     'semana'
        ... )
        >>> for punto in serie:
        ...     print(f"{punto['fecha']}: ${punto['total']:,.2f}")
    """
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        if intervalo == 'dia':
            cursor.execute("""
                SELECT 
                    DATE(fecha_retiro) as fecha,
                    COALESCE(SUM(monto), 0) as total,
                    COUNT(*) as cantidad
                FROM retiros
                WHERE DATE(fecha_retiro) BETWEEN ? AND ?
                GROUP BY DATE(fecha_retiro)
                ORDER BY fecha
            """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
            
        elif intervalo == 'semana':
            # Agrupar por semana (lunes a domingo)
            cursor.execute("""
                SELECT 
                    DATE(fecha_retiro, 'weekday 0', '-6 days') as semana_inicio,
                    DATE(fecha_retiro, 'weekday 0', '0 days') as semana_fin,
                    COALESCE(SUM(monto), 0) as total,
                    COUNT(*) as cantidad
                FROM retiros
                WHERE DATE(fecha_retiro) BETWEEN ? AND ?
                GROUP BY semana_inicio
                ORDER BY semana_inicio
            """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
            
        elif intervalo == 'mes':
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', fecha_retiro) as mes,
                    COALESCE(SUM(monto), 0) as total,
                    COUNT(*) as cantidad
                FROM retiros
                WHERE DATE(fecha_retiro) BETWEEN ? AND ?
                GROUP BY strftime('%Y-%m', fecha_retiro)
                ORDER BY mes
            """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
            
        else:
            raise ValueError(f"Intervalo no válido: {intervalo}")
        
        return [dict(row) for row in cursor.fetchall()]
        
    finally:
        conn.close()


def obtener_top_cajas(periodo: str = 'dia', fecha: Optional[date] = None, limite: int = 3) -> List[Dict]:
    """
    Obtiene las cajas con mayores montos de retiro en un período.
    
    Args:
        periodo (str): 'dia', 'semana', 'mes'
        fecha (date): Fecha de referencia
        limite (int): Número de cajas a retornar
    
    Returns:
        list: Lista de cajas ordenadas por monto descendente
    """
    if fecha is None:
        fecha = date.today()
    
    if periodo == 'dia':
        fecha_inicio = fecha
        fecha_fin = fecha
    elif periodo == 'semana':
        fecha_inicio = get_fecha_inicio_semana(fecha)
        fecha_fin = get_fecha_fin_semana(fecha)
    elif periodo == 'mes':
        fecha_inicio = get_fecha_inicio_mes(fecha)
        fecha_fin = get_fecha_fin_mes(fecha)
    else:
        raise ValueError(f"Período no válido: {periodo}")
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.nombre,
                c.numero_caja,
                COALESCE(SUM(r.monto), 0) as total,
                COUNT(r.id) as cantidad
            FROM cajas c
            LEFT JOIN retiros r ON c.id = r.id_caja 
                AND DATE(r.fecha_retiro) BETWEEN ? AND ?
            WHERE c.activa = 1
            GROUP BY c.id, c.nombre, c.numero_caja
            HAVING total > 0
            ORDER BY total DESC
            LIMIT ?
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat(), limite))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def obtener_evolucion_diaria_mes(fecha: Optional[date] = None) -> List[Dict]:
    """
    Obtiene la evolución diaria de retiros para el mes actual.
    
    Args:
        fecha (date): Fecha dentro del mes
    
    Returns:
        list: Lista con total por día del mes
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
                DATE(fecha_retiro) as dia,
                COALESCE(SUM(monto), 0) as total,
                COUNT(*) as cantidad
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
            GROUP BY DATE(fecha_retiro)
            ORDER BY dia
        """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
        
        resultados = {row['dia']: dict(row) for row in cursor.fetchall()}
        
        # Completar días sin retiros
        evolucion = []
        dia_actual = fecha_inicio
        while dia_actual <= fecha_fin:
            dia_str = dia_actual.isoformat()
            if dia_str in resultados:
                evolucion.append(resultados[dia_str])
            else:
                evolucion.append({
                    'dia': dia_str,
                    'total': 0.0,
                    'cantidad': 0
                })
            dia_actual += timedelta(days=1)
        
        return evolucion
        
    finally:
        conn.close()