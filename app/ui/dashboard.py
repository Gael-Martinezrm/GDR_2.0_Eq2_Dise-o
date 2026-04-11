"""
app/ui/dashboard.py

Vista del dashboard principal.
Actualizado con el nuevo orden de columnas para los últimos registros.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from app.modules.calculos import totales
from app.modules.retiros import model as retiros_model

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
    Muestra tarjetas de resumen y la tabla de últimos retiros con el orden solicitado.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        
        self.card_hoy = None
        self.card_semana = None
        self.card_mes = None
        self.frame_distribucion_contenido = None
        self.tree_ultimos = None

        self._create_widgets()
        
        # Cargar datos automáticamente
        self.after(100, self._refresh_dashboard)

    def _create_widgets(self):
        lbl_title = tk.Label(
            self, text="Resumen General", font=("Arial", 18, "bold"), 
            bg=C_BG, fg=C_HEADER
        )
        lbl_title.pack(anchor="w", padx=20, pady=(20, 10))

        self._create_summary_cards()
        self._create_distribution_chart()
        self._create_recent_retiros_table()

    def _create_summary_cards(self):
        cards_container = tk.Frame(self, bg=C_BG)
        cards_container.pack(fill=tk.X, padx=20, pady=10)

        def build_card(title, initial_val):
            card = tk.Frame(cards_container, bg=C_WHITE, relief=tk.FLAT, bd=0)
            card.config(highlightbackground="#E0E0E0", highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

            tk.Label(card, text=title, font=("Arial", 12), bg=C_WHITE, fg=C_TEXT).pack(anchor=tk.W, padx=15, pady=(15, 5))
            lbl_val = tk.Label(card, text=initial_val, font=("Arial", 22, "bold"), bg=C_WHITE, fg=C_ACCENT)
            lbl_val.pack(anchor=tk.W, padx=15, pady=(0, 15))
            
            card.lbl_valor = lbl_val 
            return card

        self.card_hoy = build_card("Total Retiros (Hoy)", "Cargando...")
        self.card_semana = build_card("Total Retiros (Semana)", "Cargando...")
        self.card_mes = build_card("Total Retiros (Mes)", "Cargando...")
        self.card_mes.pack(padx=(0, 0))

    def _create_distribution_chart(self):
        frame_dist = tk.Frame(self, bg=C_WHITE, highlightbackground="#E0E0E0", highlightthickness=1)
        frame_dist.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_dist, text="Distribución por Cajas", font=("Arial", 14, "bold"), bg=C_WHITE, fg=C_HEADER).pack(anchor="w", padx=15, pady=(15, 5))
        self.frame_distribucion_contenido = tk.Frame(frame_dist, bg=C_WHITE)
        self.frame_distribucion_contenido.pack(fill=tk.X, padx=15, pady=(0, 15))

    def _create_recent_retiros_table(self):
        """
        Crea tabla con toda la información centrada.
        """
        frame_table = tk.Frame(self, bg=C_WHITE, highlightbackground="#E0E0E0", 
                               highlightthickness=1)
        frame_table.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        tk.Label(
            frame_table, text="Últimos Retiros Registrados", 
            font=("Arial", 14, "bold"), bg=C_WHITE, fg=C_HEADER
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        frm_tree = tk.Frame(frame_table, bg=C_WHITE)
        frm_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        columns = ("retiro_n", "transaccion_n", "fecha", "hora", "caja", "monto", "acumulado", "usuario")
        self.tree_ultimos = ttk.Treeview(frm_tree, columns=columns, show="headings", height=8)
        
        # Configurar encabezados (Centrados por defecto en la mayoría de temas)
        self.tree_ultimos.heading("retiro_n", text="Retiro #", anchor="center")
        self.tree_ultimos.heading("transaccion_n", text="Transacción #", anchor="center")
        self.tree_ultimos.heading("fecha", text="Fecha", anchor="center")
        self.tree_ultimos.heading("hora", text="Hora Depósito", anchor="center")
        self.tree_ultimos.heading("caja", text="Caja", anchor="center")
        self.tree_ultimos.heading("monto", text="Monto", anchor="center")
        self.tree_ultimos.heading("acumulado", text="Acumulado", anchor="center")
        self.tree_ultimos.heading("usuario", text="Usuario", anchor="center")
        
        # --- CONFIGURACIÓN DE CENTRADO ---
        # Usamos anchor="center" para centrar el contenido de la celda
        self.tree_ultimos.column("retiro_n", width=70, anchor="center")
        self.tree_ultimos.column("transaccion_n", width=110, anchor="center")
        self.tree_ultimos.column("fecha", width=95, anchor="center")
        self.tree_ultimos.column("hora", width=100, anchor="center")
        self.tree_ultimos.column("caja", width=100, anchor="center")
        self.tree_ultimos.column("monto", width=90, anchor="center")  # Centrado
        self.tree_ultimos.column("acumulado", width=100, anchor="center") # Centrado
        self.tree_ultimos.column("usuario", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(frm_tree, orient="vertical", command=self.tree_ultimos.yview)
        self.tree_ultimos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_ultimos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _refresh_dashboard(self):
        try:
            hoy = date.today()
            
            # Obtener datos reales
            total_hoy = totales.calcular_acumulado_dia(hoy)
            total_semana = totales.calcular_total_semana(hoy)
            total_mes = totales.calcular_total_mes(hoy)
            
            self._update_summary_card(self.card_hoy, total_hoy)
            self._update_summary_card(self.card_semana, total_semana)
            self._update_summary_card(self.card_mes, total_mes)
            
            self._actualizar_distribucion_cajas(hoy)
            self._actualizar_ultimos_retiros(hoy)
            
        except Exception as e:
            print(f"Error actualizando dashboard: {e}")

    def _actualizar_ultimos_retiros(self, fecha):
        for item in self.tree_ultimos.get_children():
            self.tree_ultimos.delete(item)

        try:
            # Obtener registros desde el modelo (el cual ya tiene TRX-ID y Acumulado)
            retiros = retiros_model.obtener_retiros_por_fecha(fecha)
            
            if not retiros:
                return

            # Insertar con el nuevo mapeo de columnas
            for r in retiros[:10]: # Top 10
                self.tree_ultimos.insert("", "end", values=(
                    r.get('num_retiro', r.get('id')),      # Retiro #
                    r.get('num_transaccion', 'N/A'),       # Transacción #
                    r.get('fecha_solo', 'N/A'),            # Fecha
                    r.get('hora_deposito', 'N/A'),         # Hora Depósito
                    r.get('nombre_caja', 'N/A'),           # Caja
                    f"${r['monto']:,.2f}",                 # Monto
                    f"${r.get('acumulado', 0):,.2f}",      # Acumulado
                    r.get('nombre_usuario', 'N/A')         # Usuario
                ))

        except Exception as e:
            print(f"Error en tabla dashboard: {e}")

    def _update_summary_card(self, card_frame, valor):
        if card_frame and hasattr(card_frame, 'lbl_valor'):
            texto = f"${valor:,.2f}" if isinstance(valor, (int, float)) else str(valor)
            card_frame.lbl_valor.config(text=texto)

    def _actualizar_distribucion_cajas(self, fecha):
        for widget in self.frame_distribucion_contenido.winfo_children():
            widget.destroy()
        try:
            distribucion = totales.calcular_acumulado_por_caja_dia(fecha)
            if not distribucion:
                tk.Label(self.frame_distribucion_contenido, text="Sin movimientos hoy", font=("Arial", 10, "italic"), bg=C_WHITE).pack(pady=10)
                return
            for caja in distribucion:
                frm = tk.Frame(self.frame_distribucion_contenido, bg=C_WHITE)
                frm.pack(fill=tk.X, pady=2)
                tk.Label(frm, text=f"{caja['nombre']}:", font=("Arial", 10), bg=C_WHITE).pack(side="left")
                tk.Label(frm, text=f"${caja['total']:,.2f}", font=("Arial", 10, "bold"), bg=C_WHITE, fg=C_ACCENT).pack(side="left", padx=5)
        except: pass