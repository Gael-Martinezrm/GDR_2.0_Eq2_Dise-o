"""
tests/test_cajas.py

Pruebas unitarias para el módulo de cajas.
"""

import unittest
import sqlite3
import tempfile
import os
from unittest.mock import patch

# ──────────────────────────────────────────────────────────────────────────────
# BD de prueba: archivo temporal compartido entre llamadas
# Cada test obtiene su propio archivo .db que se borra al terminar.
# Se usa side_effect (no return_value) para que get_conn() abra y cierre
# conexiones independientes sobre el mismo archivo, igual que en producción.
# ──────────────────────────────────────────────────────────────────────────────

SCHEMA_CAJAS = """
    CREATE TABLE IF NOT EXISTS cajas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        numero_caja TEXT NOT NULL,
        ubicacion TEXT DEFAULT '',
        activa INTEGER DEFAULT 1,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""


def _nueva_conn(db_path):
    """Abre una nueva conexión SQLite al archivo de prueba."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class TestCajasModel(unittest.TestCase):
    """
    Suite de pruebas para el modelo de cajas.
    """

    def setUp(self):
        """
        Configuración inicial para cada prueba.
        Crea un archivo .db temporal con el esquema de cajas
        y parchea get_conn para que cada llamada abra una conexión nueva.
        """
        from app.modules.cajas import model as cajas_model
        self.model = cajas_model

        # Archivo temporal — se borra en tearDown
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)

        # Crear esquema en el archivo temporal
        conn = _nueva_conn(self.db_path)
        conn.executescript(SCHEMA_CAJAS)
        conn.commit()
        conn.close()

        # Cada llamada a get_conn() abre una conexión nueva al mismo archivo
        self.patcher = patch(
            "app.modules.cajas.model.get_conn",
            side_effect=lambda: _nueva_conn(self.db_path)
        )
        self.patcher.start()

    def tearDown(self):
        """
        Limpieza después de cada prueba.
        """
        self.patcher.stop()
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    # ── Helper interno ────────────────────────────────────────────────────────

    def _insertar(self, nombre="Caja 1", numero="001", ubicacion="", activa=1):
        """Inserta una caja directamente sin pasar por el model."""
        conn = _nueva_conn(self.db_path)
        conn.execute(
            "INSERT INTO cajas (nombre, numero_caja, ubicacion, activa) VALUES (?, ?, ?, ?)",
            (nombre, numero, ubicacion, activa)
        )
        conn.commit()
        row = conn.execute("SELECT id FROM cajas WHERE nombre = ?", (nombre,)).fetchone()
        caja_id = row["id"]
        conn.close()
        return caja_id

    # ── obtener_cajas ─────────────────────────────────────────────────────────

    def test_obtener_cajas(self):
        """Prueba obtención de todas las cajas."""
        self._insertar("Caja A", "001")
        self._insertar("Caja B", "002")
        cajas = self.model.obtener_cajas(solo_activas=False)
        self.assertIsInstance(cajas, list)
        self.assertEqual(len(cajas), 2)
        self.assertIn("nombre", cajas[0])
        self.assertIn("numero_caja", cajas[0])

    def test_obtener_cajas_solo_activas(self):
        """Prueba obtención de solo cajas activas."""
        self._insertar("Caja Activa",   "001", activa=1)
        self._insertar("Caja Inactiva", "002", activa=0)
        activas = self.model.obtener_cajas(solo_activas=True)
        self.assertEqual(len(activas), 1)
        self.assertEqual(activas[0]["nombre"], "Caja Activa")

    # ── insertar_caja ─────────────────────────────────────────────────────────

    def test_insertar_caja(self):
        """Prueba inserción de una nueva caja."""
        nuevo_id = self.model.insertar_caja("Caja Norte", "005", "Planta baja")
        self.assertIsNotNone(nuevo_id)
        self.assertGreater(nuevo_id, 0)
        caja = self.model.obtener_caja_por_id(nuevo_id)
        self.assertEqual(caja["nombre"], "Caja Norte")
        self.assertEqual(caja["numero_caja"], "005")

    def test_insertar_caja_nombre_duplicado(self):
        """Prueba que no se puede insertar caja con nombre duplicado."""
        self.model.insertar_caja("Caja Única", "010")
        with self.assertRaises(Exception):
            self.model.insertar_caja("Caja Única", "011")

    def test_insertar_caja_activa_por_defecto(self):
        """Prueba que la caja se inserta activa por defecto."""
        caja_id = self.model.insertar_caja("Nueva", "020")
        caja = self.model.obtener_caja_por_id(caja_id)
        self.assertTrue(caja["activa"])

    # ── actualizar_caja ───────────────────────────────────────────────────────

    def test_actualizar_caja(self):
        """Prueba actualización de datos de una caja."""
        caja_id = self._insertar("Original", "030")
        resultado = self.model.actualizar_caja(caja_id, "Modificada", "031", "Piso 2")
        self.assertTrue(resultado)
        caja = self.model.obtener_caja_por_id(caja_id)
        self.assertEqual(caja["nombre"], "Modificada")
        self.assertEqual(caja["numero_caja"], "031")
        self.assertEqual(caja["ubicacion"], "Piso 2")

    # ── toggle_activa ─────────────────────────────────────────────────────────

    def test_toggle_activa_desactiva(self):
        """Prueba que toggle desactiva una caja activa."""
        caja_id = self._insertar("Caja Toggle", "040", activa=1)
        nuevo_estado = self.model.toggle_activa(caja_id)
        self.assertFalse(nuevo_estado)
        caja = self.model.obtener_caja_por_id(caja_id)
        self.assertFalse(caja["activa"])

    def test_toggle_activa_reactiva(self):
        """Prueba que toggle activa una caja inactiva."""
        caja_id = self._insertar("Caja Inactiva", "041", activa=0)
        nuevo_estado = self.model.toggle_activa(caja_id)
        self.assertTrue(nuevo_estado)

    def test_toggle_no_borra_datos(self):
        """Prueba que toggle no elimina la fila, solo cambia el campo activa."""
        caja_id = self._insertar("Caja Persist", "042", activa=1)
        self.model.toggle_activa(caja_id)
        todas = self.model.obtener_cajas(solo_activas=False)
        ids = [c["id"] for c in todas]
        self.assertIn(caja_id, ids)

    # ── eliminar_caja ─────────────────────────────────────────────────────────

    def test_eliminar_caja(self):
        """Prueba eliminación de una caja."""
        caja_id = self._insertar("Caja Borrar", "099")
        resultado = self.model.eliminar_caja(caja_id)
        self.assertTrue(resultado)
        caja = self.model.obtener_caja_por_id(caja_id)
        self.assertIsNone(caja)

    def test_eliminar_caja_inexistente(self):
        """Prueba que eliminar una caja inexistente retorna False."""
        resultado = self.model.eliminar_caja(99999)
        self.assertFalse(resultado)


if __name__ == "__main__":
    unittest.main(verbosity=2)