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
        
        # Variables para guardar referencias a las tarjetas
        self.card_hoy = None
        self.card_semana = None
        self.card_mes = None

        # Construir la interfaz
        self._create_widgets()

    def _create_widgets(self):
        """
        Crea los componentes del dashboard.
        """
        # Título de la vista
        lbl_title = tk.Label(
            self, text="Resumen General", font=("Arial", 18, "bold"), bg=C_BG, fg=C_HEADER
        )
        lbl_title.pack(anchor="w", padx=20, pady=(20, 10))

        # 1. Crear tarjetas de resumen (tu tarea principal)
        self._create_summary_cards()
        
        # 2. Crear gráfico/tabla de distribución por cajas
        self._create_distribution_chart()
        
        # 3. Crear lista de últimos retiros registrados
        self._create_recent_retiros_table()

    def _create_summary_cards(self):
        """
        Crea las tarjetas de resumen (total hoy, semana, mes).
        """
        # Contenedor principal para las tarjetas
        cards_container = tk.Frame(self, bg=C_BG)
        cards_container.pack(fill=tk.X, padx=20, pady=10)

        # Función auxiliar para no repetir código al crear tarjetas
        def build_card(title, initial_val):
            card = tk.Frame(cards_container, bg=C_WHITE, relief=tk.FLAT, bd=0)
            # Para simular un pequeño borde/sombra
            card.config(highlightbackground="#E0E0E0", highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

            lbl_title = tk.Label(card, text=title, font=("Arial", 12), bg=C_WHITE, fg=C_TEXT)
            lbl_title.pack(anchor=tk.W, padx=15, pady=(15, 5))

            lbl_val = tk.Label(card, text=initial_val, font=("Arial", 22, "bold"), bg=C_WHITE, fg=C_ACCENT)
            lbl_val.pack(anchor=tk.W, padx=15, pady=(0, 15))
            
            # Guardamos la referencia del label dentro del frame para actualizarlo después
            card.lbl_valor = lbl_val 
            return card

        # Instanciamos las 3 tarjetas y las guardamos
        self.card_hoy = build_card("Total Retiros (Hoy)", "$0.00")
        self.card_semana = build_card("Total Retiros (Semana)", "$0.00")
        
        # Como el último no necesita padding a la derecha, lo reconfiguramos un poco
        self.card_mes = build_card("Total Retiros (Mes)", "$0.00")
        self.card_mes.pack(padx=(0, 0)) # Quitamos el margen derecho al último

    def _create_distribution_chart(self):
        """
        Crea gráfico/tabla de distribución de retiros por cajas.
        (Placeholder visual por ahora)
        """
        frame_dist = tk.Frame(self, bg=C_WHITE, highlightbackground="#E0E0E0", highlightthickness=1)
        frame_dist.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            frame_dist, text="Distribución por Cajas", font=("Arial", 14, "bold"), bg=C_WHITE, fg=C_HEADER
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        tk.Label(
            frame_dist, text="[ Aquí irá el gráfico o tabla de cajas ]", font=("Arial", 10, "italic"), bg=C_WHITE, fg=C_TEXT
        ).pack(pady=30)

    def _create_recent_retiros_table(self):
        """
        Crea tabla con los últimos retiros registrados.
        (Placeholder visual por ahora)
        """
        frame_table = tk.Frame(self, bg=C_WHITE, highlightbackground="#E0E0E0", highlightthickness=1)
        frame_table.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        tk.Label(
            frame_table, text="Últimos Retiros Registrados", font=("Arial", 14, "bold"), bg=C_WHITE, fg=C_HEADER
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        tk.Label(
            frame_table, text="[ Aquí irá el Treeview/Tabla de retiros recientes ]", font=("Arial", 10, "italic"), bg=C_WHITE, fg=C_TEXT
        ).pack(pady=50)

    def _update_summary_card(self, card_frame, valor):
        """
        Actualiza el valor mostrado en una tarjeta de resumen.

        Args:
            card_frame (tk.Frame): Frame de la tarjeta.
            valor (float o str): Nuevo valor a mostrar.
        """
        if card_frame and hasattr(card_frame, 'lbl_valor'):
            # Si el valor es un número, le damos formato de moneda
            if isinstance(valor, (int, float)):
                texto_formateado = f"${valor:,.2f}"
            else:
                texto_formateado = str(valor)
                
            card_frame.lbl_valor.config(text=texto_formateado)

    def _refresh_dashboard(self):
        """
        Refresca todos los datos del dashboard.
        (Este método será llenado más adelante conectándolo con la BD)
        """
        # EJEMPLO de cómo se usaría (esto lo conectará la Persona 3 con la base de datos)
        # self._update_summary_card(self.card_hoy, 12500.50)
        # self._update_summary_card(self.card_semana, 45800.00)
        # self._update_summary_card(self.card_mes, 120000.00)
        pass

    # Método de conveniencia para que el Backend actualice todo fácilmente
    def set_totales(self, total_hoy, total_semana, total_mes):
        """Método público para inyectar los datos desde el controlador"""
        self._update_summary_card(self.card_hoy, total_hoy)
        self._update_summary_card(self.card_semana, total_semana)
        self._update_summary_card(self.card_mes, total_mes)