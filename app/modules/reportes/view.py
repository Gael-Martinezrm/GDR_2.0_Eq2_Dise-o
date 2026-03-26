"""
app/modules/reportes/view.py

Interfaz gráfica del módulo de reportes.
Permite generar y visualizar reportes de retiros.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta

from app.modules.reportes import model as reportes_model
from app.modules.reportes import export_excel, export_pdf
from app.auth.session import Session
from app.utils.helpers import (
    get_fecha_inicio_semana,
    get_fecha_fin_semana,
    get_fecha_inicio_mes,
    get_fecha_fin_mes
)

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
        self.sesion = Session()
        self.datos_actuales = None
        
        # Ocupar todo el espacio disponible
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Construir la interfaz
        self._create_widgets()

    def _nombre_mes_espanol(self, fecha):
        """
        Convierte la fecha a nombre de mes en español.
        
        Args:
            fecha (date): Fecha a convertir
        
        Returns:
            str: Nombre del mes en español
        """
        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        return meses[fecha.month]

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
        ctrl_frame.pack_propagate(False)  # Mantener el ancho fijo

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
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))  # Fecha de hoy por defecto
        self.entry_fecha.pack(fill=tk.X, padx=15, pady=(0, 20))

        # Botón Generar
        btn_generar = tk.Button(ctrl_frame, text="Generar Previsualización", bg=C_BTN, fg=C_WHITE, 
                                font=("Arial", 10, "bold"), relief=tk.FLAT, cursor="hand2", 
                                command=self._on_generar_reporte)
        btn_generar.pack(fill=tk.X, padx=15, pady=(0, 30), ipady=5)

        # Botones de Exportación
        tk.Label(ctrl_frame, text="Exportar Resultados", font=("Arial", 10, "bold"), bg=C_WHITE, fg=C_HEADER).pack(anchor="w", padx=15, pady=(10, 5))
        
        btn_pdf = tk.Button(ctrl_frame, text="📄 Exportar a PDF", bg="#D32F2F", fg=C_WHITE, 
                           font=("Arial", 10), relief=tk.FLAT, cursor="hand2", 
                           command=self._on_exportar_pdf)
        btn_pdf.pack(fill=tk.X, padx=15, pady=(5, 5), ipady=3)
        
        btn_excel = tk.Button(ctrl_frame, text="📊 Exportar a Excel", bg="#2E7D32", fg=C_WHITE, 
                             font=("Arial", 10), relief=tk.FLAT, cursor="hand2", 
                             command=self._on_exportar_excel)
        btn_excel.pack(fill=tk.X, padx=15, pady=(0, 15), ipady=3)

        # --- PANEL DERECHO (PREVISUALIZACIÓN / TABLA) ---
        preview_frame = tk.Frame(main_frame, bg=C_WHITE, highlightbackground="#E0E0E0", highlightthickness=1)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(preview_frame, text="Vista Previa de Datos", font=("Arial", 12, "bold"), bg=C_WHITE, fg=C_HEADER).pack(anchor="w", padx=15, pady=(15, 10))

        # Tabla (Treeview) - CON TODAS LAS COLUMNAS CENTRADAS
        columnas = ("fecha", "caja", "id", "importe", "usuario")
        self.tree = ttk.Treeview(preview_frame, columns=columnas, show="headings")
        
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("caja", text="Caja")
        self.tree.heading("id", text="ID")
        self.tree.heading("importe", text="Importe")
        self.tree.heading("usuario", text="Usuario")
        
        # Ajustar anchos y alineación - TODAS CENTRADAS
        self.tree.column("fecha", width=120, anchor="center")
        self.tree.column("caja", width=100, anchor="center")
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("importe", width=100, anchor="center")
        self.tree.column("usuario", width=120, anchor="center")

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
            # Actualizar valor por defecto
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        elif tipo == "Semanal":
            self.lbl_fecha.config(text="Semana (DD/MM/AAAA):")
            # Actualizar valor por defecto
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        elif tipo == "Mensual":
            self.lbl_fecha.config(text="Mes (MM/AAAA):")
            # Actualizar valor por defecto al mes actual
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, datetime.now().strftime("%m/%Y"))

    def _obtener_rango_fechas(self):
        """
        Obtiene el rango de fechas según el tipo de reporte y fecha ingresada.
        
        Returns:
            tuple: (fecha_inicio, fecha_fin, periodo_descripcion)
        """
        tipo = self.combo_tipo.get()
        fecha_texto = self.entry_fecha.get().strip()
        
        try:
            if tipo == "Diario":
                fecha_obj = datetime.strptime(fecha_texto, "%d/%m/%Y").date()
                fecha_inicio = fecha_obj
                fecha_fin = fecha_obj
                periodo = fecha_obj.strftime("%d/%m/%Y")
                
            elif tipo == "Semanal":
                fecha_ref = datetime.strptime(fecha_texto, "%d/%m/%Y").date()
                # Obtener lunes de la semana
                fecha_inicio = get_fecha_inicio_semana(fecha_ref)  # Lunes
                # Obtener domingo de la semana
                fecha_fin = get_fecha_fin_semana(fecha_ref)  # Domingo
                # Mostrar rango de fechas: Lunes a Domingo
                periodo = f"{fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
                
            elif tipo == "Mensual":
                # Formato MM/AAAA
                fecha_obj = datetime.strptime(fecha_texto, "%m/%Y").date()
                fecha_inicio = get_fecha_inicio_mes(fecha_obj)
                fecha_fin = get_fecha_fin_mes(fecha_obj)
                # MODIFICADO: Nombre del mes en español
                periodo = f"{self._nombre_mes_espanol(fecha_obj)} {fecha_obj.year}"
                
            else:
                raise ValueError("Tipo de reporte no válido")
            
            return fecha_inicio, fecha_fin, periodo
            
        except ValueError as e:
            if tipo == "Mensual":
                raise ValueError(f"Formato de fecha inválido. Use: Mes (MM/AAAA) - Ejemplo: 03/2026")
            else:
                raise ValueError(f"Formato de fecha inválido. Use: {self.lbl_fecha.cget('text')}")

    def _on_generar_reporte(self):
        """
        Genera el reporte según los parámetros seleccionados.
        Obtiene datos del modelo y los muestra en la tabla.
        """
        try:
            # Obtener rango de fechas
            fecha_inicio, fecha_fin, periodo = self._obtener_rango_fechas()
            
            # Obtener retiros del período
            retiros = reportes_model.retiros_por_periodo(fecha_inicio, fecha_fin)
            
            # Calcular totales
            total = sum(r['monto'] for r in retiros)
            cantidad = len(retiros)
            
            # Guardar datos actuales para exportación
            self.datos_actuales = {
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime("%d/%m/%Y"),
                'fecha_fin': fecha_fin.strftime("%d/%m/%Y"),
                'retiros': retiros,
                'total': total,
                'cantidad': cantidad
            }
            
            # Limpiar tabla
            self._refresh_reporte()
            
            # Llenar tabla con datos reales
            for r in retiros:
                # Formatear fecha
                if isinstance(r['fecha_retiro'], str):
                    fecha_str = r['fecha_retiro'][:16].replace('T', ' ')
                else:
                    fecha_str = str(r['fecha_retiro'])[:16]
                
                self.tree.insert("", tk.END, values=(
                    fecha_str,
                    r.get('nombre_caja', 'N/A'),
                    r['id'],
                    f"${r['monto']:,.2f}",
                    r.get('nombre_usuario', r.get('username', 'N/A'))
                ))
            
            tipo = self.combo_tipo.get()
            messagebox.showinfo("Reporte Generado", 
                               f"Previsualización del reporte {tipo.lower()} generada con éxito.\n"
                               f"Período: {periodo}\n"
                               f"Total: ${total:,.2f}\n"
                               f"Cantidad: {cantidad} retiros", 
                               parent=self)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}", parent=self)

    def _on_exportar_pdf(self):
        """
        Exporta el reporte actual a PDF.
        Abre un diálogo para seleccionar ubicación y nombre del archivo.
        """
        if not self.datos_actuales or not self.datos_actuales['retiros']:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Genera un reporte primero.", parent=self)
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar Reporte PDF",
            initialdir="exports/"
        )
        
        if archivo:
            try:
                tipo = self.combo_tipo.get()
                titulo = f"Reporte {tipo} - {self.datos_actuales['periodo']}"
                
                export_pdf.exportar_pdf(self.datos_actuales, titulo, archivo)
                
                # Registrar en base de datos
                fecha_inicio = datetime.strptime(self.datos_actuales['fecha_inicio'], "%d/%m/%Y").date()
                fecha_fin = datetime.strptime(self.datos_actuales['fecha_fin'], "%d/%m/%Y").date()
                
                reportes_model.registrar_reporte_generado(
                    tipo_reporte=tipo.lower(),
                    periodo=self.datos_actuales['periodo'],
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    total_retiros=self.datos_actuales['total'],
                    cantidad_retiros=self.datos_actuales['cantidad'],
                    ruta_archivo=archivo,
                    formato="PDF"
                )
                
                messagebox.showinfo("Exportar PDF", f"Reporte PDF guardado en:\n{archivo}", parent=self)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar PDF: {e}", parent=self)

    def _on_exportar_excel(self):
        """
        Exporta el reporte actual a Excel.
        Abre un diálogo para seleccionar ubicación y nombre del archivo.
        """
        if not self.datos_actuales or not self.datos_actuales['retiros']:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Genera un reporte primero.", parent=self)
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar Reporte Excel",
            initialdir="exports/"
        )
        
        if archivo:
            try:
                tipo = self.combo_tipo.get()
                titulo = f"Reporte {tipo} - {self.datos_actuales['periodo']}"
                
                export_excel.exportar_excel(self.datos_actuales, titulo, archivo)
                
                # Registrar en base de datos
                fecha_inicio = datetime.strptime(self.datos_actuales['fecha_inicio'], "%d/%m/%Y").date()
                fecha_fin = datetime.strptime(self.datos_actuales['fecha_fin'], "%d/%m/%Y").date()
                
                reportes_model.registrar_reporte_generado(
                    tipo_reporte=tipo.lower(),
                    periodo=self.datos_actuales['periodo'],
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    total_retiros=self.datos_actuales['total'],
                    cantidad_retiros=self.datos_actuales['cantidad'],
                    ruta_archivo=archivo,
                    formato="Excel"
                )
                
                messagebox.showinfo("Exportar Excel", f"Reporte Excel guardado en:\n{archivo}", parent=self)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar Excel: {e}", parent=self)

    def _refresh_reporte(self):
        """
        Refresca la tabla del reporte limpiando los datos actuales.
        """
        # Borra todos los elementos actuales del Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
