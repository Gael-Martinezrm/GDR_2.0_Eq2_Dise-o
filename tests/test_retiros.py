"""
tests/test_retiros.py

Pruebas unitarias para el módulo de retiros.
"""

import unittest
import sqlite3
import tempfile
import os
from datetime import datetime, date, timedelta
from unittest.mock import patch

from app.modules.retiros import model as retiros_model


# Esquema de base de datos para pruebas
SCHEMA_COMPLETO = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL,
    activo INTEGER DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cajas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    numero_caja TEXT NOT NULL,
    ubicacion TEXT,
    activa INTEGER DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
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


class TestRetirosModel(unittest.TestCase):
    """
    Suite de pruebas para el modelo de retiros.
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
        
        # Insertar datos base (usuario y cajas)
        self._insertar_datos_base(conn)
        conn.close()

        # Parchear get_conn para usar BD de prueba
        self.patcher = patch(
            "app.modules.retiros.model.get_conn",
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

    def _insertar_datos_base(self, conn):
        """Inserta datos base (usuario y cajas) en la BD."""
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
        
        conn.commit()

    def test_insertar_retiro(self):
        """Prueba inserción de un retiro en la base de datos."""
        id_retiro = retiros_model.insertar_retiro(
            id_usuario=1,
            id_caja=1,
            monto=1500.50,
            motivo="Pago proveedor",
            observaciones="Factura #123"
        )
        
        self.assertIsNotNone(id_retiro)
        self.assertGreater(id_retiro, 0)
        
        # Verificar que se insertó correctamente
        retiro = retiros_model.obtener_retiro_por_id(id_retiro)
        self.assertEqual(retiro["monto"], 1500.50)
        self.assertEqual(retiro["motivo"], "Pago proveedor")
        self.assertEqual(retiro["observaciones"], "Factura #123")

    def test_insertar_retiro_sin_monto(self):
        """Prueba que no se puede insertar retiro sin monto."""
        # Intentar insertar con monto negativo o cero
        with self.assertRaises(Exception):
            retiros_model.insertar_retiro(
                id_usuario=1,
                id_caja=1,
                monto=0,
                motivo="Prueba",
                observaciones=""
            )

    def test_insertar_retiro_monto_negativo(self):
        """Prueba que no se puede insertar retiro con monto negativo."""
        with self.assertRaises(Exception):
            retiros_model.insertar_retiro(
                id_usuario=1,
                id_caja=1,
                monto=-100,
                motivo="Prueba",
                observaciones=""
            )

    def test_insertar_retiro_caja_inexistente(self):
        """Prueba que no se puede insertar retiro con caja inexistente."""
        with self.assertRaises(Exception):
            retiros_model.insertar_retiro(
                id_usuario=1,
                id_caja=999,  # ID de caja inexistente
                monto=1000,
                motivo="Prueba",
                observaciones=""
            )

    def test_obtener_retiros_por_fecha(self):
        """Prueba obtención de retiros por fecha específica."""
        hoy = date.today()
        
        # Insertar retiros
        retiros_model.insertar_retiro(1, 1, 1000, "Pago 1", "")
        retiros_model.insertar_retiro(1, 2, 500, "Pago 2", "")
        
        # Obtener retiros de hoy
        retiros = retiros_model.obtener_retiros_por_fecha(hoy)
        
        self.assertEqual(len(retiros), 2)
        self.assertEqual(retiros[0]["monto"], 1000)
        self.assertEqual(retiros[1]["monto"], 500)

    def test_obtener_retiros_fecha_sin_datos(self):
        """Prueba obtención de retiros en fecha sin transacciones."""
        fecha_sin = date(2025, 1, 1)
        retiros = retiros_model.obtener_retiros_por_fecha(fecha_sin)
        self.assertEqual(len(retiros), 0)

    def test_obtener_retiros_por_caja_y_fecha(self):
        """Prueba obtención de retiros por caja y fecha."""
        hoy = date.today()
        
        # Insertar retiros
        retiros_model.insertar_retiro(1, 1, 1000, "Caja 1 - Pago", "")
        retiros_model.insertar_retiro(1, 2, 500, "Caja 2 - Pago", "")
        retiros_model.insertar_retiro(1, 1, 300, "Caja 1 - Otro", "")
        
        # Obtener retiros de caja 1
        retiros_caja1 = retiros_model.obtener_retiros_por_caja_y_fecha(1, hoy)
        
        self.assertEqual(len(retiros_caja1), 2)
        self.assertEqual(retiros_caja1[0]["monto"], 1000)
        self.assertEqual(retiros_caja1[1]["monto"], 300)

    def test_obtener_total_diario(self):
        """Prueba cálculo del total diario de retiros."""
        hoy = date.today()
        
        # Insertar retiros
        retiros_model.insertar_retiro(1, 1, 1000, "", "")
        retiros_model.insertar_retiro(1, 2, 500, "", "")
        
        total = retiros_model.obtener_total_diario(hoy)
        self.assertEqual(total, 1500.00)

    def test_obtener_retiros_por_periodo(self):
        """Prueba obtención de retiros en un rango de fechas."""
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        hace_3_dias = hoy - timedelta(days=3)
        
        # Insertar retiros en diferentes fechas
        conn = _nueva_conn(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 1000, ?)
        """, (hoy.isoformat(),))
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 2, 500, ?)
        """, (ayer.isoformat(),))
        cursor.execute("""
            INSERT INTO retiros (id_usuario, id_caja, monto, fecha_retiro) 
            VALUES (1, 1, 300, ?)
        """, (hace_3_dias.isoformat(),))
        conn.commit()
        conn.close()
        
        # Obtener retiros en período (ayer a hoy)
        retiros = retiros_model.obtener_retiros_por_periodo(ayer, hoy)
        self.assertEqual(len(retiros), 2)  # solo ayer y hoy

    def test_obtener_retiro_por_id(self):
        """Prueba obtención de un retiro específico por ID."""
        id_retiro = retiros_model.insertar_retiro(
            id_usuario=1,
            id_caja=1,
            monto=2500.75,
            motivo="Prueba específica",
            observaciones="Observación de prueba"
        )
        
        retiro = retiros_model.obtener_retiro_por_id(id_retiro)
        
        self.assertIsNotNone(retiro)
        self.assertEqual(retiro["id"], id_retiro)
        self.assertEqual(retiro["monto"], 2500.75)
        self.assertEqual(retiro["motivo"], "Prueba específica")
        self.assertEqual(retiro["observaciones"], "Observación de prueba")

    def test_eliminar_retiro(self):
        """Prueba eliminación de un retiro."""
        # Insertar retiro
        id_retiro = retiros_model.insertar_retiro(1, 1, 1000, "Para eliminar", "")
        
        # Verificar que existe
        retiro = retiros_model.obtener_retiro_por_id(id_retiro)
        self.assertIsNotNone(retiro)
        
        # Eliminar
        resultado = retiros_model.eliminar_retiro(id_retiro)
        self.assertTrue(resultado)
        
        # Verificar que ya no existe
        retiro = retiros_model.obtener_retiro_por_id(id_retiro)
        self.assertIsNone(retiro)

    def test_eliminar_retiro_inexistente(self):
        """Prueba eliminación de un retiro que no existe."""
        resultado = retiros_model.eliminar_retiro(99999)
        self.assertFalse(resultado)

    def test_actualizar_retiro(self):
        """Prueba actualización de un retiro existente."""
        # Insertar retiro
        id_retiro = retiros_model.insertar_retiro(
            id_usuario=1,
            id_caja=1,
            monto=1000,
            motivo="Original",
            observaciones="Original"
        )
        
        # Actualizar
        resultado = retiros_model.actualizar_retiro(
            id_retiro=id_retiro,
            monto=2000,
            motivo="Actualizado",
            observaciones="Nuevas observaciones"
        )
        
        self.assertTrue(resultado)
        
        # Verificar cambios
        retiro = retiros_model.obtener_retiro_por_id(id_retiro)
        self.assertEqual(retiro["monto"], 2000)
        self.assertEqual(retiro["motivo"], "Actualizado")
        self.assertEqual(retiro["observaciones"], "Nuevas observaciones")

    def test_obtener_estadisticas_diarias(self):
        """Prueba obtención de estadísticas diarias."""
        hoy = date.today()
        
        # Insertar retiros
        retiros_model.insertar_retiro(1, 1, 1000, "Primero", "")
        retiros_model.insertar_retiro(1, 2, 500, "Segundo", "")
        
        stats = retiros_model.obtener_estadisticas_diarias(hoy)
        
        self.assertEqual(stats["total"], 1500.00)
        self.assertEqual(stats["cantidad"], 2)
        self.assertEqual(stats["promedio"], 750.00)
        self.assertEqual(stats["maximo"], 1000.00)
        self.assertEqual(stats["minimo"], 500.00)
        self.assertEqual(len(stats["por_caja"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)