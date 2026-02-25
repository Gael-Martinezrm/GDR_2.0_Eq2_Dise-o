"""
app/ui/main_window.py

Ventana principal de la aplicación.
Contiene sidebar de navegación y área de contenido intercambiable.
"""

import tkinter as tk
from tkinter import ttk

# Paleta de colores
C_BG = "#F0F2F5"
C_SIDEBAR = "#1565C0"
C_ACCENT = "#1976D2"
C_WHITE = "#FFFFFF"
C_TEXT = "#212121"
C_HEADER = "#1565C0"
C_BTN = "#1565C0"
C_DANGER = "#C62828"


class MainWindow(tk.Tk):
    """
    Ventana principal de la aplicación.

    Estructura:
    - Sidebar izquierdo azul (#1565C0) con navegación
    - Área de contenido derecha intercambiable según opción seleccionada
    - Logout y usuario activo en el header

    Módulos disponibles:
    - Dashboard
    - Retiros
    - Cajas (solo admin/gerente)
    - Usuarios (solo admin)
    - Reportes
    """

    def __init__(self, usuario):
        """
        Inicializa la ventana principal.

        Args:
            usuario (dict): Datos del usuario autenticado.
        """
        super().__init__()
        self.usuario = usuario
        self.title("Sistema de Retiros")
        self.geometry("1200x800")

        # TODO: Implementar ventana principal
        # 1. Crear sidebar con botones de navegación
        # 2. Crear area de contenido central
        # 3. Crear header con información del usuario y logout
        # 4. Implementar cambio dinámico de vistas

    def _create_widgets(self):
        """
        Crea los componentes principales de la ventana.

        Incluye:
        - Sidebar
        - Header
        - Área de contenido intercambiable
        """
        pass

    def _show_dashboard(self):
        """
        Muestra la vista del dashboard.
        """
        pass

    def _show_retiros(self):
        """
        Muestra la vista de retiros.
        """
        pass

    def _show_cajas(self):
        """
        Muestra la vista de cajas (solo admin/gerente).
        """
        pass

    def _show_usuarios(self):
        """
        Muestra la vista de usuarios (solo admin).
        """
        pass

    def _show_reportes(self):
        """
        Muestra la vista de reportes.
        """
        pass

    def _change_view(self, new_frame):
        """
        Cambia la vista actual por una nueva.

        Args:
            new_frame (tk.Frame): Frame a mostrar.
        """
        pass

    def _on_logout(self):
        """
        Cierra la sesión y vuelve a la ventana de login.
        """
        pass
