"""
app/modules/reportes/view.py

Interfaz gráfica del módulo de reportes.
Permite generar y visualizar reportes de retiros.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# Paleta de colores (la misma que usaste en dashboard y components)
C_BG = "#F0F2F5"
C_WHITE = "#FFFFFF"
C_TEXT = "#212121"
C_HEADER = "#1565C0"
C_BTN = "#1565C0"
C_ACCENT = "#1976D2"

class ReportesView(tk.Frame):
    """
    Vista del módulo de reportes.

    Proporciona interfaz para:
    - Seleccionar período (diario, semanal, mensual)
    - Visualizar datos del reporte
    - Exportar a PDF o Excel
    - Ver historial de reportes generados
    """

    def __init__(self, parent):
        """
        Inicializa la vista de reportes.

        Args:
            parent: Widget padre (ventana principal).
        """
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        
        # Ocupar todo el espacio disponible
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Construir la interfaz
        self._create_widgets()

    def _create_widgets(self):
        """
        Crea los componentes de la interfaz.

        Incluye:
        - Selector de tipo de reporte (diario, semanal, mensual)
        - Selector de fechas
        - Tabla con datos del reporte
        - Botones de exportación
        """
        # Encabezado
        lbl_title = tk.Label(self, text="Generador de Reportes", font=("Arial", 18, "bold"), bg=C_BG, fg=C_HEADER)
        lbl_title.pack(anchor="w", pady=(0, 20))

        # Contenedor principal dividido en dos (Izquierda: Controles, Derecha: Previsualización)
        main_frame = tk.Frame(self, bg=C_BG)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- PANEL IZQUIERDO (CONTROLES) ---
        ctrl_frame = tk.Frame(main_frame, bg=C_WHITE, width=280, highlightbackground="#E0E0E0", highlightthickness=1)
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        ctrl_frame.pack_propagate(False) # Mantener el ancho fijo

        tk.Label(ctrl_frame, text="Parámetros", font=("Arial", 12, "bold"), bg=C_WHITE, fg=C_HEADER).pack(pady=(15, 10), anchor="w", padx=15)

        # Selector de Tipo
        tk.Label(ctrl_frame, text="Tipo de Reporte:", font=("Arial", 10), bg=C_WHITE, fg=C_TEXT).pack(anchor="w", padx=15)
        self.combo_tipo = ttk.Combobox(ctrl_frame, values=["Diario", "Semanal", "Mensual"], state="readonly")
        self.combo_tipo.current(0)
        self.combo_tipo.pack(fill=tk.X, padx=15, pady=(0, 15))
        self.combo_tipo.bind("<<ComboboxSelected>>", self._on_tipo_reporte_changed)

        # Selector de Fecha (Periodo)
        self.lbl_fecha = tk.Label(ctrl_frame, text="Fecha (DD/MM/AAAA):", font=("Arial", 10), bg=C_WHITE, fg=C_TEXT)
        self.lbl_fecha.pack(anchor="w", padx=15)
        self.entry_fecha = ttk.Entry(ctrl_frame)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y")) # Fecha de hoy por defecto
        self.entry_fecha.pack(fill=tk.X, padx=15, pady=(0, 20))

        # Botón Generar
        btn_generar = tk.Button(ctrl_frame, text="Generar Previsualización", bg=C_BTN, fg=C_WHITE, font=("Arial", 10, "bold"), relief=tk.FLAT, cursor="hand2", command=self._on_generar_reporte)
        btn_generar.pack(fill=tk.X, padx=15, pady=(0, 30), ipady=5)

        # Botones de Exportación
        tk.Label(ctrl_frame, text="Exportar Resultados", font=("Arial", 10, "bold"), bg=C_WHITE, fg=C_HEADER).pack(anchor="w", padx=15, pady=(10, 5))
        
        btn_pdf = tk.Button(ctrl_frame, text="📄 Exportar a PDF", bg="#D32F2F", fg=C_WHITE, font=("Arial", 10), relief=tk.FLAT, cursor="hand2", command=self._on_exportar_pdf)
        btn_pdf.pack(fill=tk.X, padx=15, pady=(5, 5), ipady=3)
        
        btn_excel = tk.Button(ctrl_frame, text="📊 Exportar a Excel", bg="#2E7D32", fg=C_WHITE, font=("Arial", 10), relief=tk.FLAT, cursor="hand2", command=self._on_exportar_excel)
        btn_excel.pack(fill=tk.X, padx=15, pady=(0, 15), ipady=3)

        # --- PANEL DERECHO (PREVISUALIZACIÓN / TABLA) ---
        preview_frame = tk.Frame(main_frame, bg=C_WHITE, highlightbackground="#E0E0E0", highlightthickness=1)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(preview_frame, text="Vista Previa de Datos", font=("Arial", 12, "bold"), bg=C_WHITE, fg=C_HEADER).pack(anchor="w", padx=15, pady=(15, 10))

        # Tabla (Treeview)
        columnas = ("fecha", "caja", "transaccion", "importe", "usuario")
        self.tree = ttk.Treeview(preview_frame, columns=columnas, show="headings")
        
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("caja", text="Caja")
        self.tree.heading("transaccion", text="No. Transacción")
        self.tree.heading("importe", text="Importe")
        self.tree.heading("usuario", text="Usuario")
        
        # Ajustar anchos
        self.tree.column("fecha", width=90)
        self.tree.column("caja", width=80, anchor="center")
        self.tree.column("transaccion", width=120)
        self.tree.column("importe", width=100, anchor="e")
        self.tree.column("usuario", width=100)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=(0, 15))

    def _on_tipo_reporte_changed(self, event):
        """
        Actualiza las opciones de fecha según el tipo de reporte seleccionado.
        """
        tipo = self.combo_tipo.get()
        if tipo == "Diario":
            self.lbl_fecha.config(text="Fecha (DD/MM/AAAA):")
        elif tipo == "Semanal":
            self.lbl_fecha.config(text="Semana (Ej. Semana 10 - 2026):")
        elif tipo == "Mensual":
            self.lbl_fecha.config(text="Mes (MM/AAAA):")

    def _on_generar_reporte(self):
        """
        Genera el reporte según los parámetros seleccionados.
        Obtiene datos del modelo y los muestra en la tabla.
        """
        tipo = self.combo_tipo.get()
        fecha_texto = self.entry_fecha.get()
        
        # Por ahora limpiamos e insertamos datos de prueba visuales.
        # Más adelante, aquí el controlador/modelo traerá los datos reales de la BD[cite: 53, 57].
        self._refresh_reporte()
        
        self.tree.insert("", tk.END, values=(fecha_texto, "Caja 1", "TRX-001", "$1,500.00", "Admin"))
        self.tree.insert("", tk.END, values=(fecha_texto, "Caja 2", "TRX-002", "$3,200.00", "Operador1"))
        
        messagebox.showinfo("Reporte Generado", f"Previsualización del reporte {tipo.lower()} generada con éxito.")

    def _on_exportar_pdf(self):
        """
        Exporta el reporte actual a PDF.
        Abre un diálogo para seleccionar ubicación y nombre del archivo.
        """
        # Deja listo el cuadro de diálogo para la Persona 6
        archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar Reporte PDF"
        )
        if archivo:
            # Aquí se conectará la lógica de ReportLab / WeasyPrint
            messagebox.showinfo("Exportar PDF", f"El archivo se guardaría en:\n{archivo}\n\n(Lógica de exportación pendiente por P6)")

    def _on_exportar_excel(self):
        """
        Exporta el reporte actual a Excel.
        Abre un diálogo para seleccionar ubicación y nombre del archivo.
        """
        # Deja listo el cuadro de diálogo para la Persona 6
        archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar Reporte Excel"
        )
        if archivo:
            # Aquí se conectará la lógica de openpyxl
            messagebox.showinfo("Exportar Excel", f"El archivo se guardaría en:\n{archivo}\n\n(Lógica de exportación pendiente por P6)")

    def _refresh_reporte(self):
        """
        Refresca la tabla del reporte limpiando los datos actuales.
        """
        # Borra todos los elementos actuales del Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)