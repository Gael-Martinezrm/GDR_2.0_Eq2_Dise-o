"""
app/ui/dashboard.py

Vista del dashboard principal.
Muestra resumen de retiros del día, semana y mes.
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


class DashboardView(tk.Frame):
    """
    Vista del dashboard principal.

    Muestra tarjetas de resumen con:
    - Total de retiros hoy
    - Total de retiros semana
    - Total de retiros mes
    - Número de retiros registrados en el día
    - Distribución por cajas
    """

    def __init__(self, parent):
        """
        Inicializa el dashboard.

        Args:
            parent: Widget padre (ventana principal).
        """
        super().__init__(parent, bg=C_BG)
        self.parent = parent

        # TODO: Implementar dashboard
        # 1. Crear tarjetas de resumen (total hoy, semana, mes)
        # 2. Crear gráfico/tabla de respistribución por cajas
        # 3. Crear lista de últimos retiros registrados
        # 4. Conectar con funciones de cálculo

    def _create_widgets(self):
        """
        Crea los componentes del dashboard.

        Incluye:
        - Tarjetas de resumen
        - Gráfico de distribución por cajas
        - Tabla de últimos retiros
        """
        pass

    def _create_summary_cards(self):
        """
        Crea las tarjetas de resumen (total hoy, semana, mes).
        """
        pass

    def _create_distribution_chart(self):
        """
        Crea gráfico/tabla de distribución de retiros por cajas.
        """
        pass

    def _create_recent_retiros_table(self):
        """
        Crea tabla con los últimos retiros registrados.
        """
        pass

    def _refresh_dashboard(self):
        """
        Refresca todos los datos del dashboard.
        """
        pass

    def _update_summary_card(self, card_frame, valor):
        """
        Actualiza el valor mostrado en una tarjeta de resumen.

        Args:
            card_frame (tk.Frame): Frame de la tarjeta.
            valor (str): Nuevo valor a mostrar.
        """
        pass
