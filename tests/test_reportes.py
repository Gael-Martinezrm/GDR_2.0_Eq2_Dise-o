"""
tests/test_reportes.py

Pruebas unitarias para el módulo de reportes.
"""

import unittest
import sqlite3
import tempfile
import os
from datetime import date, datetime, timedelta
from unittest.mock import patch

from app.modules.reportes import model as reportes_model
from app.modules.comparaciones import model as comparaciones_model


SCHEMA_COMPLETO = """
-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('administrador', 'gerente', 'operador')),
    activo INTEGER DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Cajas
CREATE TABLE IF NOT EXISTS cajas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    numero_caja TEXT NOT NULL,
    ubicacion TEXT,
    activa INTEGER DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Retiros
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

-- Tabla de Reportes Generados
CREATE TABLE IF NOT EXISTS reportes_generados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_reporte TEXT NOT NULL,
    periodo TEXT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    total_retiros REAL NOT NULL,
    cantidad_retiros INTEGER NOT NULL,
    ruta_archivo TEXT,
    formato TEXT,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def _nueva_conn(db_path):
    """Abre una nueva conexión SQLite al archivo de prueba."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class TestReportesModel(unittest.TestCase):
    """
    Suite de pruebas para el modelo de reportes.
    """

    def setUp(self):
        """Configuración inicial para cada prueba."""
        from app.modules.reportes import model as reportes_model
        self.model = reportes_model

        # Archivo temporal
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)

        # Crear esquema completo
        conn = _nueva_conn(self.db_path)
        conn.executescript(SCHEMA_COMPLETO)
        conn.commit()
        
        # Insertar datos de prueba
        self._insertar_datos_prueba(conn)
        conn.close()

        # Parchear get_conn
        self.patcher = patch(
            "app.modules.reportes.model.get_conn",
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
            INSERT INTO usuarios (nombre, usuario, password_hash, rol) 
            VALUES (?, ?, ?, ?)
        """, ("Usuario Test", "test", "hash123", "operador"))
        
        # Insertar cajas
        cursor.execute("""
            INSERT INTO cajas (nombre, numero_caja, ubicacion, activa) 
            VALUES (?, ?, ?, ?)
        """, ("Caja 1", "001", "Mostrador", 1))
        
        cursor.execute("""
            INSERT INTO cajas (nombre, numero_caja, ubicacion, activa) 
            VALUES (?, ?, ?, ?)
        """, ("Caja 2", "002", "Oficina", 1))
        
        # Insertar retiros en diferentes fechas
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        semana_pasada = hoy - timedelta(days=7)
        
        # Hoy: 2 retiros
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 1000.00, ?)
        """, (hoy.isoformat(),))
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 2, 500.00, ?)
        """, (hoy.isoformat(),))
        
        # Ayer: 1 retiro
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 300.00, ?)
        """, (ayer.isoformat(),))
        
        # Semana pasada: 1 retiro
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 2, 700.00, ?)
        """, (semana_pasada.isoformat(),))
        
        conn.commit()

    def test_total_diario(self):
        """Prueba cálculo del total diario de retiros."""
        hoy = date.today()
        total = self.model.total_diario(hoy)
        self.assertEqual(total, 1500.00)  # 1000 + 500

    def test_total_diario_sin_datos(self):
        """Prueba total diario para fecha sin retiros."""
        fecha_sin_retiros = date(2025, 1, 1)
        total = self.model.total_diario(fecha_sin_retiros)
        self.assertEqual(total, 0.0)

    def test_total_semanal(self):
        """Prueba cálculo del total semanal de retiros."""
        hoy = date.today()
        total = self.model.total_semanal(hoy)
        # Debe incluir hoy y ayer
        self.assertEqual(total, 1800.00)  # 1000 + 500 + 300

    def test_total_mensual(self):
        """Prueba cálculo del total mensual de retiros."""
        hoy = date.today()
        total = self.model.total_mensual(hoy)
        # Debe incluir hoy, ayer y semana pasada (si está en el mismo mes)
        self.assertGreaterEqual(total, 1800.00)

    def test_total_por_caja_diario(self):
        """Prueba cálculo del total por caja en un día."""
        hoy = date.today()
        por_caja = self.model.total_por_caja_diario(hoy)
        
        caja1 = next((c for c in por_caja if c['nombre_caja'] == 'Caja 1'), None)
        caja2 = next((c for c in por_caja if c['nombre_caja'] == 'Caja 2'), None)
        
        self.assertIsNotNone(caja1)
        self.assertIsNotNone(caja2)
        self.assertEqual(caja1['total'], 1000.00)
        self.assertEqual(caja2['total'], 500.00)

    def test_retiros_por_periodo(self):
        """Prueba obtención de retiros en un período."""
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        
        retiros = self.model.retiros_por_periodo(ayer, hoy)
        self.assertEqual(len(retiros), 3)  # Ayer (1) + Hoy (2)

    def test_cantidad_retiros_diarios(self):
        """Prueba conteo de retiros en un día."""
        hoy = date.today()
        cantidad = self.model.cantidad_retiros_diarios(hoy)
        self.assertEqual(cantidad, 2)

    def test_promedio_retiros_diarios(self):
        """Prueba cálculo del promedio de retiros en un día."""
        hoy = date.today()
        promedio = self.model.promedio_retiros_diarios(hoy)
        self.assertEqual(promedio, 750.00)  # (1000 + 500) / 2

    def test_registrar_reporte_generado(self):
        """Prueba registro de un reporte generado."""
        reporte_id = self.model.registrar_reporte_generado(
            tipo_reporte="diario",
            periodo="01/03/2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 3, 1),
            total_retiros=1500.00,
            cantidad_retiros=2,
            ruta_archivo="/exports/reporte.pdf",
            formato="PDF"
        )
        
        self.assertIsNotNone(reporte_id)
        self.assertGreater(reporte_id, 0)


class TestComparacionesModel(unittest.TestCase):
    """
    Suite de pruebas para el modelo de comparaciones.
    """

    def setUp(self):
        """Configuración inicial para cada prueba."""
        from app.modules.comparaciones import model as comparaciones_model
        self.model = comparaciones_model

        # Archivo temporal
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)

        # Crear esquema completo
        conn = _nueva_conn(self.db_path)
        conn.executescript(SCHEMA_COMPLETO)
        conn.commit()
        
        # Insertar datos de prueba
        self._insertar_datos_prueba(conn)
        conn.close()

        # Parchear get_conn
        self.patcher = patch(
            "app.modules.comparaciones.model.get_conn",
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
        """Inserta datos de prueba para comparaciones."""
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO usuarios (nombre, usuario, password_hash, rol) 
            VALUES (?, ?, ?, ?)
        """, ("Test", "test", "hash", "operador"))
        
        cursor.execute("""
            INSERT INTO cajas (nombre, numero_caja, activa) 
            VALUES (?, ?, ?)
        """, ("Caja Test", "001", 1))
        
        # Semana 1: 1000
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 1000.00, '2026-03-01')
        """)
        
        # Semana 2: 1500
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 1500.00, '2026-03-08')
        """)
        
        conn.commit()

    def test_comparar_semanas(self):
        """Prueba comparación entre semanas."""
        semana1_inicio = date(2026, 3, 1)
        semana1_fin = date(2026, 3, 7)
        semana2_inicio = date(2026, 3, 8)
        semana2_fin = date(2026, 3, 14)
        
        resultado = self.model.comparar_semanas(
            semana1_inicio, semana1_fin,
            semana2_inicio, semana2_fin
        )
        
        self.assertEqual(resultado['semana1']['total'], 1000.00)
        self.assertEqual(resultado['semana2']['total'], 1500.00)
        self.assertEqual(resultado['diferencia'], 500.00)
        self.assertEqual(resultado['porcentaje'], 50.00)
        self.assertEqual(resultado['tendencia'], 'aumento')


if __name__ == "__main__":
    unittest.main(verbosity=2)