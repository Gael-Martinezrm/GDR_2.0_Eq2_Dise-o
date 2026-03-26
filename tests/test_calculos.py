"""
tests/test_calculos.py

Pruebas unitarias para el módulo de cálculos.
"""

import unittest
import sqlite3
import tempfile
import os
from datetime import date, timedelta
from unittest.mock import patch

from app.modules.calculos import totales
from app.utils.helpers import (
    get_fecha_inicio_semana,
    get_fecha_fin_semana,
    get_fecha_inicio_mes,
    get_fecha_fin_mes
)


# Esquema de base de datos para pruebas
SCHEMA_COMPLETO = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL,
    activo INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cajas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    numero_caja TEXT NOT NULL,
    ubicacion TEXT,
    activa INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS retiros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_caja INTEGER NOT NULL,
    monto REAL NOT NULL,
    motivo TEXT,
    fecha_retiro DATETIME NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_caja) REFERENCES cajas(id)
);
"""


def _nueva_conn(db_path):
    """Abre una nueva conexión SQLite al archivo de prueba."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class TestCalculosTotales(unittest.TestCase):
    """
    Suite de pruebas para el módulo de cálculos de totales.
    """

    def setUp(self):
        """Configuración inicial para cada prueba."""
        # Archivo temporal para BD de prueba
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)

        # Crear esquema
        conn = _nueva_conn(self.db_path)
        conn.executescript(SCHEMA_COMPLETO)
        conn.commit()
        
        # Insertar datos de prueba
        self._insertar_datos_prueba(conn)
        conn.close()

        # Parchear get_conn para usar BD de prueba
        self.patcher = patch(
            "app.modules.calculos.totales.get_conn",
            side_effect=lambda: _nueva_conn(self.db_path)
        )
        self.patcher.start()

    def tearDown(self):
        """Limpieza después de cada prueba."""
        self.patcher.stop()
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def _insertar_datos_prueba(self, conn):
        """Inserta datos de prueba en la BD."""
        cursor = conn.cursor()
        
        # Insertar usuario
        cursor.execute("""
            INSERT INTO usuarios (nombre, usuario, password_hash, rol, activo) 
            VALUES (?, ?, ?, ?, ?)
        """, ("Usuario Test", "test", "hash123", "operador", 1))
        
        # Insertar cajas
        cursor.execute("""
            INSERT INTO cajas (nombre, numero_caja, ubicacion, activa) 
            VALUES (?, ?, ?, ?)
        """, ("Caja Principal", "001", "Mostrador", 1))
        
        cursor.execute("""
            INSERT INTO cajas (nombre, numero_caja, ubicacion, activa) 
            VALUES (?, ?, ?, ?)
        """, ("Caja Secundaria", "002", "Oficina", 1))
        
        # Insertar retiros en diferentes fechas
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        hace_2_dias = hoy - timedelta(days=2)
        hace_7_dias = hoy - timedelta(days=7)
        hace_30_dias = hoy - timedelta(days=30)
        
        # Retiros de hoy
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 1000.00, ?)
        """, (hoy.isoformat(),))
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 2, 500.00, ?)
        """, (hoy.isoformat(),))
        
        # Retiro de ayer
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 300.00, ?)
        """, (ayer.isoformat(),))
        
        # Retiro de hace 2 días
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 2, 200.00, ?)
        """, (hace_2_dias.isoformat(),))
        
        # Retiro de hace 7 días (semana pasada)
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 700.00, ?)
        """, (hace_7_dias.isoformat(),))
        
        # Retiro de hace 30 días (mes pasado)
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 2, 1500.00, ?)
        """, (hace_30_dias.isoformat(),))
        
        conn.commit()

    def test_calcular_acumulado_dia(self):
        """Prueba cálculo del acumulado diario."""
        hoy = date.today()
        total = totales.calcular_acumulado_dia(hoy)
        self.assertEqual(total, 1500.00)  # 1000 + 500

    def test_calcular_acumulado_dia_vacio(self):
        """Prueba cálculo cuando no hay retiros en el día."""
        fecha_sin_retiros = date(2025, 1, 1)
        total = totales.calcular_acumulado_dia(fecha_sin_retiros)
        self.assertEqual(total, 0.0)

    def test_calcular_acumulado_por_caja_dia(self):
        """Prueba cálculo del acumulado por caja en un día."""
        hoy = date.today()
        distribucion = totales.calcular_acumulado_por_caja_dia(hoy)
        
        # Buscar cada caja
        caja_principal = next((c for c in distribucion if c["nombre"] == "Caja Principal"), None)
        caja_secundaria = next((c for c in distribucion if c["nombre"] == "Caja Secundaria"), None)
        
        self.assertIsNotNone(caja_principal)
        self.assertIsNotNone(caja_secundaria)
        self.assertEqual(caja_principal["total"], 1000.00)
        self.assertEqual(caja_secundaria["total"], 500.00)

    def test_calcular_total_semana(self):
        """Prueba cálculo del total semanal."""
        hoy = date.today()
        total_semana = totales.calcular_total_semana(hoy)
        # Debe incluir hoy, ayer y hace 2 días (3 días dentro de la semana)
        self.assertEqual(total_semana, 2000.00)  # 1000 + 500 + 300 + 200 = 2000

    def test_calcular_total_mes(self):
        """Prueba cálculo del total mensual."""
        hoy = date.today()
        total_mes = totales.calcular_total_mes(hoy)
        # Debe incluir hoy, ayer, hace 2 días, hace 7 días (si está en el mismo mes)
        # hace 30 días no debe incluirse
        self.assertGreaterEqual(total_mes, 2000.00)

    def test_promedio_por_retiro_dia(self):
        """Prueba cálculo del promedio de retiro por día."""
        hoy = date.today()
        promedio = totales.calcular_promedio_por_retiro_dia(hoy)
        # (1000 + 500) / 2 = 750
        self.assertEqual(promedio, 750.00)

    def test_contar_retiros_dia(self):
        """Prueba conteo de retiros en un día."""
        hoy = date.today()
        cantidad = totales.contar_retiros_dia(hoy)
        self.assertEqual(cantidad, 2)

    def test_contar_retiros_semana(self):
        """Prueba conteo de retiros en una semana."""
        hoy = date.today()
        cantidad = totales.contar_retiros_semana(hoy)
        # Debe contar 4 retiros (hoy:2, ayer:1, hace 2 días:1)
        self.assertEqual(cantidad, 4)

    def test_obtener_monto_maximo_dia(self):
        """Prueba obtener el retiro más grande del día."""
        hoy = date.today()
        maximo = totales.obtener_monto_maximo_dia(hoy)
        self.assertEqual(maximo, 1000.00)

    def test_obtener_monto_minimo_dia(self):
        """Prueba obtener el retiro más pequeño del día."""
        hoy = date.today()
        minimo = totales.obtener_monto_minimo_dia(hoy)
        self.assertEqual(minimo, 500.00)

    def test_obtener_estadisticas_completas_dia(self):
        """Prueba obtener todas las estadísticas del día."""
        hoy = date.today()
        stats = totales.obtener_estadisticas_completas_dia(hoy)
        
        self.assertEqual(stats["total"], 1500.00)
        self.assertEqual(stats["cantidad"], 2)
        self.assertEqual(stats["promedio"], 750.00)
        self.assertEqual(stats["maximo"], 1000.00)
        self.assertEqual(stats["minimo"], 500.00)
        self.assertEqual(len(stats["por_caja"]), 2)

    def test_calcular_acumulado_hasta_fecha(self):
        """Prueba cálculo del acumulado histórico."""
        hoy = date.today()
        acumulado = totales.calcular_acumulado_hasta_fecha(hoy)
        # Debe sumar todos los retiros hasta hoy
        self.assertGreaterEqual(acumulado, 4200.00)  # 1000+500+300+200+700+1500=4200


if __name__ == "__main__":
    unittest.main(verbosity=2)