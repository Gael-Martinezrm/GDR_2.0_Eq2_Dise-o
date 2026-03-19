"""
app/ui/dashboard.py

Vista del dashboard principal.
Muestra resumen de retiros del día, semana y mes.
CONECTADO CON CÁLCULOS REALES
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

    Muestra tarjetas de resumen con:
    - Total de retiros hoy
    - Total de retiros semana
    - Total de retiros mes
    - Número de retiros registrados en el día
    - Distribución por cajas
    - Últimos retiros registrados
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

        # Frame para distribución por cajas (placeholder)
        self.frame_distribucion_contenido = None
        
        # Treeview para últimos retiros
        self.tree_ultimos = None

        # Construir la interfaz (manteniendo el diseño original)
        self._create_widgets()
        
        # Cargar datos automáticamente después de crear la interfaz
        self.after(100, self._refresh_dashboard)

    def _create_widgets(self):
        """
        Crea los componentes del dashboard (DISEÑO ORIGINAL).
        """
        # Título de la vista
        lbl_title = tk.Label(
            self, text="Resumen General", font=("Arial", 18, "bold"), 
            bg=C_BG, fg=C_HEADER
        )
        lbl_title.pack(anchor="w", padx=20, pady=(20, 10))

        # 1. Crear tarjetas de resumen (diseño original)
        self._create_summary_cards()
        
        # 2. Crear frame para distribución por cajas
        self._create_distribution_chart()
        
        # 3. Crear lista de últimos retiros registrados
        self._create_recent_retiros_table()

    def _create_summary_cards(self):
        """
        Crea las tarjetas de resumen (total hoy, semana, mes) - DISEÑO ORIGINAL.
        """
        # Contenedor principal para las tarjetas
        cards_container = tk.Frame(self, bg=C_BG)
        cards_container.pack(fill=tk.X, padx=20, pady=10)

        # Función auxiliar para crear tarjetas
        def build_card(title, initial_val):
            card = tk.Frame(cards_container, bg=C_WHITE, relief=tk.FLAT, bd=0)
            # Para simular un pequeño borde/sombra
            card.config(highlightbackground="#E0E0E0", highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

            lbl_title = tk.Label(card, text=title, font=("Arial", 12), 
                                bg=C_WHITE, fg=C_TEXT)
            lbl_title.pack(anchor=tk.W, padx=15, pady=(15, 5))

            lbl_val = tk.Label(card, text=initial_val, font=("Arial", 22, "bold"), 
                              bg=C_WHITE, fg=C_ACCENT)
            lbl_val.pack(anchor=tk.W, padx=15, pady=(0, 15))
            
            # Guardamos la referencia del label dentro del frame para actualizarlo después
            card.lbl_valor = lbl_val 
            return card

        # Instanciamos las 3 tarjetas y las guardamos
        self.card_hoy = build_card("Total Retiros (Hoy)", "Cargando...")
        self.card_semana = build_card("Total Retiros (Semana)", "Cargando...")
        
        # Como el último no necesita padding a la derecha, lo reconfiguramos un poco
        self.card_mes = build_card("Total Retiros (Mes)", "Cargando...")
        self.card_mes.pack(padx=(0, 0))  # Quitamos el margen derecho al último

    def _create_distribution_chart(self):
        """
        Crea el frame para distribución de retiros por cajas (DISEÑO ORIGINAL).
        """
        frame_dist = tk.Frame(self, bg=C_WHITE, highlightbackground="#E0E0E0", 
                              highlightthickness=1)
        frame_dist.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            frame_dist, text="Distribución por Cajas", 
            font=("Arial", 14, "bold"), bg=C_WHITE, fg=C_HEADER
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Frame contenedor para el contenido dinámico (se actualizará con datos reales)
        self.frame_distribucion_contenido = tk.Frame(frame_dist, bg=C_WHITE)
        self.frame_distribucion_contenido.pack(fill=tk.X, padx=15, pady=(0, 15))

    def _create_recent_retiros_table(self):
        """
        Crea tabla con los últimos retiros registrados (DISEÑO ORIGINAL).
        """
        frame_table = tk.Frame(self, bg=C_WHITE, highlightbackground="#E0E0E0", 
                               highlightthickness=1)
        frame_table.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        tk.Label(
            frame_table, text="Últimos Retiros Registrados", 
            font=("Arial", 14, "bold"), bg=C_WHITE, fg=C_HEADER
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Frame para el Treeview
        frm_tree = tk.Frame(frame_table, bg=C_WHITE)
        frm_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Crear Treeview (tabla)
        columns = ("hora", "caja", "monto", "usuario")
        self.tree_ultimos = ttk.Treeview(frm_tree, columns=columns, show="headings", height=8)
        
        # Configurar columnas
        self.tree_ultimos.heading("hora", text="Hora")
        self.tree_ultimos.heading("caja", text="Caja")
        self.tree_ultimos.heading("monto", text="Monto")
        self.tree_ultimos.heading("usuario", text="Usuario")
        
        self.tree_ultimos.column("hora", width=100)
        self.tree_ultimos.column("caja", width=150)
        self.tree_ultimos.column("monto", width=120, anchor="e")
        self.tree_ultimos.column("usuario", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frm_tree, orient="vertical", command=self.tree_ultimos.yview)
        self.tree_ultimos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_ultimos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
        Refresca todos los datos del dashboard con información REAL de la BD.
        """
        try:
            # Obtener fecha actual
            hoy = date.today()
            
            # ===== 1. OBTENER DATOS DE LOS MÓDULOS DE CÁLCULO =====
            total_hoy = totales.calcular_acumulado_dia(hoy)
            total_semana = totales.calcular_total_semana(hoy)
            total_mes = totales.calcular_total_mes(hoy)
            
            # ===== 2. ACTUALIZAR TARJETAS =====
            self._update_summary_card(self.card_hoy, total_hoy)
            self._update_summary_card(self.card_semana, total_semana)
            self._update_summary_card(self.card_mes, total_mes)
            
            # ===== 3. ACTUALIZAR DISTRIBUCIÓN POR CAJAS =====
            self._actualizar_distribucion_cajas(hoy)
            
            # ===== 4. ACTUALIZAR ÚLTIMOS RETIROS =====
            self._actualizar_ultimos_retiros(hoy)
            
        except Exception as e:
            print(f"Error actualizando dashboard: {e}")
            # Mostrar error en las tarjetas
            self._update_summary_card(self.card_hoy, "Error")
            self._update_summary_card(self.card_semana, "Error")
            self._update_summary_card(self.card_mes, "Error")

    def _actualizar_distribucion_cajas(self, fecha):
        """
        Actualiza la sección de distribución por cajas con datos reales.
        
        Args:
            fecha (date): Fecha a consultar
        """
        # Limpiar contenido anterior
        for widget in self.frame_distribucion_contenido.winfo_children():
            widget.destroy()

        try:
            # Obtener distribución por cajas
            distribucion = totales.calcular_acumulado_por_caja_dia(fecha)
            
            if not distribucion:
                # Mostrar mensaje si no hay datos
                tk.Label(
                    self.frame_distribucion_contenido, 
                    text="No hay retiros registrados hoy",
                    font=("Arial", 10, "italic"),
                    bg=C_WHITE, fg=C_TEXT
                ).pack(pady=20)
                return

            # Crear una tabla simple con los datos
            for caja in distribucion:
                # Frame para cada caja
                frm_caja = tk.Frame(self.frame_distribucion_contenido, bg=C_WHITE)
                frm_caja.pack(fill=tk.X, pady=2)
                
                # Nombre de la caja
                tk.Label(
                    frm_caja, 
                    text=f"{caja['nombre']} (N° {caja['numero_caja']}):",
                    font=("Arial", 10),
                    bg=C_WHITE, fg=C_TEXT
                ).pack(side="left", padx=(0, 10))
                
                # Total de la caja
                tk.Label(
                    frm_caja,
                    text=f"${caja['total']:,.2f}",
                    font=("Arial", 10, "bold"),
                    bg=C_WHITE, fg=C_ACCENT
                ).pack(side="left")
                
                # Cantidad de retiros
                tk.Label(
                    frm_caja,
                    text=f"({caja['cantidad']} retiros)",
                    font=("Arial", 9),
                    bg=C_WHITE, fg=C_TEXT
                ).pack(side="left", padx=(5, 0))

        except Exception as e:
            # Mostrar error
            tk.Label(
                self.frame_distribucion_contenido,
                text=f"Error al cargar datos: {e}",
                font=("Arial", 10),
                bg=C_WHITE, fg=C_DANGER
            ).pack(pady=20)

    def _actualizar_ultimos_retiros(self, fecha):
        """
        Actualiza la tabla de últimos retiros con datos reales.
        
        Args:
            fecha (date): Fecha a consultar
        """
        # Limpiar tabla
        for item in self.tree_ultimos.get_children():
            self.tree_ultimos.delete(item)

        try:
            # Obtener últimos retiros
            retiros = retiros_model.obtener_retiros_por_fecha(fecha)
            
            if not retiros:
                # Mostrar mensaje si no hay retiros
                self.tree_ultimos.insert("", "end", values=(
                    "--:--", "---", "$0.00", "---"
                ))
                return

            # Insertar retiros (mostrar solo los primeros 10)
            for r in retiros[:10]:
                # Formatear hora
                if isinstance(r['fecha_retiro'], str):
                    hora_str = r['fecha_retiro'][11:16]  # HH:MM
                else:
                    hora_str = str(r['fecha_retiro'])

                self.tree_ultimos.insert("", "end", values=(
                    hora_str,
                    r.get('nombre_caja', 'N/A'),
                    f"${r['monto']:,.2f}",
                    r.get('nombre_usuario', r.get('username', 'N/A'))
                ))

        except Exception as e:
            # Mostrar error
            self.tree_ultimos.insert("", "end", values=(
                "Error", "Error", "Error", str(e)
            ))

    # Métodos públicos para compatibilidad (los usa main_window.py)
    def set_totales(self, total_hoy, total_semana, total_mes):
        """
        Método público para inyectar los datos desde el controlador.
        Mantenido para compatibilidad con código existente.
        """
        self._update_summary_card(self.card_hoy, total_hoy)
        self._update_summary_card(self.card_semana, total_semana)
        self._update_summary_card(self.card_mes, total_mes)