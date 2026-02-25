"""
app/modules/cajas/view.py

Interfaz gráfica del módulo de cajas.
Permite administrar las cajas físicas del sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class CajasView(tk.Frame):
    """
    Vista del módulo de cajas.

    Proporciona interfaz para:
    - Listar todas las cajas
    - Crear nueva caja
    - Editar cajas existentes
    - Activar/desactivar cajas
    """

    def __init__(self, parent):
        """
        Inicializa la vista de cajas.

        Args:
            parent: Widget padre (ventana principal).
        """
        super().__init__(parent)
        self.parent = parent

        # TODO: Implementar interfaz
        # 1. Crear tabla de cajas
        # 2. Crear botón "Nueva caja"
        # 3. Crear botones de edición/eliminación
        # 4. Conectar con métodos de model.py

    def _create_widgets(self):
        """
        Crea los componentes de la interfaz.

        Incluye:
        - Tabla de cajas
        - Botones de acciones (nueva, editar, eliminar, activar/desactivar)
        """
        pass

    def _on_nueva_caja(self):
        """
        Abre el diálogo para crear una nueva caja.

        Captura:
        - Nombre
        - Número de caja
        - Ubicación
        """
        pass

    def _on_editar_caja(self):
        """
        Abre el diálogo para editar la caja seleccionada.
        """
        pass

    def _on_toggle_caja(self):
        """
        Activa o desactiva la caja seleccionada.
        """
        pass

    def _on_eliminar_caja(self):
        """
        Elimina la caja seleccionada (previa confirmación).
        """
        pass

    def _refresh_cajas(self):
        """
        Refresca la tabla de cajas con los datos actualizados.
        """
        pass
