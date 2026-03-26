"""
app/modules/comparaciones/model.py

Módulo de comparaciones de montos por períodos.
"""

from datetime import date, timedelta
from typing import Optional, Dict, List
from app.db.connection import get_conn
from app.utils.helpers import (
    get_fecha_inicio_semana,
    get_fecha_fin_semana,
    get_fecha_inicio_mes,
    get_fecha_fin_mes
)


def comparar_semanas(semana1_inicio: date, semana1_fin: date, 
                     semana2_inicio: date, semana2_fin: date,
                     incluir_detalle: bool = True) -> Dict:
    """
    Compara totales entre dos semanas.
    """
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # Semana 1
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total, COUNT(*) as cantidad
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (semana1_inicio.isoformat(), semana1_fin.isoformat()))
        semana1 = dict(cursor.fetchone())
        semana1['inicio'] = semana1_inicio.isoformat()
        semana1['fin'] = semana1_fin.isoformat()
        
        # Semana 2
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total, COUNT(*) as cantidad
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (semana2_inicio.isoformat(), semana2_fin.isoformat()))
        semana2 = dict(cursor.fetchone())
        semana2['inicio'] = semana2_inicio.isoformat()
        semana2['fin'] = semana2_fin.isoformat()
        
        # Cálculos
        diferencia = semana2['total'] - semana1['total']
        
        if semana1['total'] > 0:
            porcentaje = (diferencia / semana1['total']) * 100
        else:
            porcentaje = 100 if semana2['total'] > 0 else 0
        
        tendencia = 'aumento' if diferencia > 0 else 'disminucion' if diferencia < 0 else 'sin_cambio'
        
        resultado = {
            'semana1': semana1,
            'semana2': semana2,
            'diferencia': diferencia,
            'porcentaje': porcentaje,
            'tendencia': tendencia
        }
        
        # Detalle por caja
        if incluir_detalle:
            cursor.execute("""
                SELECT 
                    c.nombre,
                    COALESCE(SUM(CASE WHEN DATE(r.fecha_retiro) BETWEEN ? AND ? THEN r.monto ELSE 0 END), 0) as total_semana1,
                    COALESCE(SUM(CASE WHEN DATE(r.fecha_retiro) BETWEEN ? AND ? THEN r.monto ELSE 0 END), 0) as total_semana2,
                    COUNT(CASE WHEN DATE(r.fecha_retiro) BETWEEN ? AND ? THEN 1 END) as cantidad_semana1,
                    COUNT(CASE WHEN DATE(r.fecha_retiro) BETWEEN ? AND ? THEN 1 END) as cantidad_semana2
                FROM cajas c
                LEFT JOIN retiros r ON c.id = r.id_caja
                WHERE c.activa = 1
                GROUP BY c.id, c.nombre
                ORDER BY c.nombre
            """, (semana1_inicio.isoformat(), semana1_fin.isoformat(),
                  semana2_inicio.isoformat(), semana2_fin.isoformat(),
                  semana1_inicio.isoformat(), semana1_fin.isoformat(),
                  semana2_inicio.isoformat(), semana2_fin.isoformat()))
            
            resultado['detalle_cajas'] = [dict(row) for row in cursor.fetchall()]
        
        return resultado
        
    finally:
        conn.close()


def comparar_semana_actual_con_anterior(fecha_ref: Optional[date] = None) -> Dict:
    """
    Compara la semana actual con la semana anterior.
    """
    if fecha_ref is None:
        fecha_ref = date.today()
    
    semana_actual_inicio = get_fecha_inicio_semana(fecha_ref)
    semana_actual_fin = get_fecha_fin_semana(fecha_ref)
    semana_anterior_inicio = semana_actual_inicio - timedelta(days=7)
    semana_anterior_fin = semana_actual_inicio - timedelta(days=1)
    
    return comparar_semanas(
        semana_anterior_inicio, semana_anterior_fin,
        semana_actual_inicio, semana_actual_fin
    )


def comparar_meses(mes1_año: int, mes1_mes: int, 
                   mes2_año: int, mes2_mes: int,
                   incluir_detalle: bool = True) -> Dict:
    """
    Compara totales entre dos meses.
    """
    from calendar import monthrange
    
    inicio1 = date(mes1_año, mes1_mes, 1)
    fin1 = date(mes1_año, mes1_mes, monthrange(mes1_año, mes1_mes)[1])
    inicio2 = date(mes2_año, mes2_mes, 1)
    fin2 = date(mes2_año, mes2_mes, monthrange(mes2_año, mes2_mes)[1])
    
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # Mes 1
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total, COUNT(*) as cantidad
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (inicio1.isoformat(), fin1.isoformat()))
        mes1 = dict(cursor.fetchone())
        mes1['año'] = mes1_año
        mes1['mes'] = mes1_mes
        mes1['inicio'] = inicio1.isoformat()
        mes1['fin'] = fin1.isoformat()
        
        # Mes 2
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total, COUNT(*) as cantidad
            FROM retiros
            WHERE DATE(fecha_retiro) BETWEEN ? AND ?
        """, (inicio2.isoformat(), fin2.isoformat()))
        mes2 = dict(cursor.fetchone())
        mes2['año'] = mes2_año
        mes2['mes'] = mes2_mes
        mes2['inicio'] = inicio2.isoformat()
        mes2['fin'] = fin2.isoformat()
        
        # Cálculos
        diferencia = mes2['total'] - mes1['total']
        
        if mes1['total'] > 0:
            porcentaje = (diferencia / mes1['total']) * 100
        else:
            porcentaje = 100 if mes2['total'] > 0 else 0
        
        tendencia = 'aumento' if diferencia > 0 else 'disminucion' if diferencia < 0 else 'sin_cambio'
        
        resultado = {
            'mes1': mes1,
            'mes2': mes2,
            'diferencia': diferencia,
            'porcentaje': porcentaje,
            'tendencia': tendencia
        }
        
        # Detalle por caja
        if incluir_detalle:
            cursor.execute("""
                SELECT 
                    c.nombre,
                    COALESCE(SUM(CASE WHEN DATE(r.fecha_retiro) BETWEEN ? AND ? THEN r.monto ELSE 0 END), 0) as total_mes1,
                    COALESCE(SUM(CASE WHEN DATE(r.fecha_retiro) BETWEEN ? AND ? THEN r.monto ELSE 0 END), 0) as total_mes2,
                    COUNT(CASE WHEN DATE(r.fecha_retiro) BETWEEN ? AND ? THEN 1 END) as cantidad_mes1,
                    COUNT(CASE WHEN DATE(r.fecha_retiro) BETWEEN ? AND ? THEN 1 END) as cantidad_mes2
                FROM cajas c
                LEFT JOIN retiros r ON c.id = r.id_caja
                WHERE c.activa = 1
                GROUP BY c.id, c.nombre
                ORDER BY c.nombre
            """, (inicio1.isoformat(), fin1.isoformat(),
                  inicio2.isoformat(), fin2.isoformat(),
                  inicio1.isoformat(), fin1.isoformat(),
                  inicio2.isoformat(), fin2.isoformat()))
            
            resultado['detalle_cajas'] = [dict(row) for row in cursor.fetchall()]
        
        return resultado
        
    finally:
        conn.close()


def comparar_mes_actual_con_anterior(fecha_ref: Optional[date] = None) -> Dict:
    """
    Compara el mes actual con el mes anterior.
    """
    if fecha_ref is None:
        fecha_ref = date.today()
    
    mes_actual = fecha_ref.month
    año_actual = fecha_ref.year
    
    if mes_actual == 1:
        mes_anterior = 12
        año_anterior = año_actual - 1
    else:
        mes_anterior = mes_actual - 1
        año_anterior = año_actual
    
    return comparar_meses(año_anterior, mes_anterior, año_actual, mes_actual)