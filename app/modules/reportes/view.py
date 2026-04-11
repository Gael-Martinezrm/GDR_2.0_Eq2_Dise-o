"""
app/modules/reportes/view.py

Interfaz gráfica del módulo de reportes.
Permite generar y visualizar reportes de retiros.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import calendar

from app.modules.reportes.model import retiros_por_periodo

# ── Exportación ──────────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import inch
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# Paleta de colores
C_BG    = "#F0F2F5"
C_WHITE = "#FFFFFF"
C_TEXT  = "#212121"
C_HEADER= "#1565C0"
C_BTN   = "#1565C0"
C_ACCENT= "#1976D2"

# ── Nuevo orden de columnas ───────────────────────────────────────────────────
COLUMNAS_HEADER = ("No. Transacción", "Importe", "Caja", "Usuario", "Fecha")


# ── Selector de fecha (calendario popup) ─────────────────────────────────────

class _CalendarioPopup(tk.Toplevel):

    def __init__(self, parent, var_fecha: tk.StringVar, modo: str = "diario"):
        super().__init__(parent)
        self.var_fecha = var_fecha
        self.modo = modo
        self.overrideredirect(True)
        self.configure(bg=C_WHITE)
        self.grab_set()

        try:
            if modo == "mensual":
                fecha_ini = datetime.strptime(var_fecha.get(), "%m/%Y")
            else:
                fecha_ini = datetime.strptime(var_fecha.get(), "%d/%m/%Y")
        except ValueError:
            fecha_ini = datetime.now()

        self._año = fecha_ini.year
        self._mes = fecha_ini.month
        self._dia = fecha_ini.day

        self._build()
        self._posicionar(parent)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<FocusOut>", self._on_focus_out)

    def _build(self):
        frm = tk.Frame(self, bg=C_WHITE, relief="solid", bd=1, padx=8, pady=8)
        frm.pack(fill="both", expand=True)

        frm_nav = tk.Frame(frm, bg=C_WHITE)
        frm_nav.pack(fill="x", pady=(0, 6))

        tk.Button(frm_nav, text="◀", command=self._mes_anterior,
                  bg=C_WHITE, fg=C_ACCENT, relief="flat", cursor="hand2",
                  font=("Arial", 11, "bold")).pack(side="left")

        self.lbl_mes_año = tk.Label(frm_nav, bg=C_WHITE, fg=C_TEXT,
                                    font=("Arial", 10, "bold"), width=16)
        self.lbl_mes_año.pack(side="left", expand=True)

        tk.Button(frm_nav, text="▶", command=self._mes_siguiente,
                  bg=C_WHITE, fg=C_ACCENT, relief="flat", cursor="hand2",
                  font=("Arial", 11, "bold")).pack(side="right")

        if self.modo == "mensual":
            self.frm_grid = tk.Frame(frm, bg=C_WHITE)
            self.frm_grid.pack()
        else:
            DIAS_SEMANA = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
            frm_dias = tk.Frame(frm, bg=C_WHITE)
            frm_dias.pack()
            for col, d in enumerate(DIAS_SEMANA):
                tk.Label(frm_dias, text=d, bg=C_WHITE, fg=C_ACCENT,
                         font=("Arial", 8, "bold"), width=3).grid(row=0, column=col)
            self.frm_grid = tk.Frame(frm, bg=C_WHITE)
            self.frm_grid.pack()

        tk.Button(frm, text="Hoy", command=self._seleccionar_hoy,
                  bg=C_BG, fg=C_ACCENT, relief="flat", cursor="hand2",
                  font=("Arial", 9)).pack(pady=(6, 0))

        self._renderizar_mes()

    def _renderizar_mes(self):
        for w in self.frm_grid.winfo_children():
            w.destroy()

        MESES_ES = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.lbl_mes_año.config(text=f"{MESES_ES[self._mes]} {self._año}")

        if self.modo == "mensual":
            tk.Button(
                self.frm_grid,
                text=f"Seleccionar  {MESES_ES[self._mes]} {self._año}",
                bg=C_ACCENT, fg=C_WHITE,
                activebackground="#1565C0", activeforeground=C_WHITE,
                relief="flat", cursor="hand2", font=("Arial", 10),
                command=self._seleccionar_mes,
                padx=10, pady=6
            ).pack(pady=6)
        else:
            hoy = datetime.now().date()
            semanas = calendar.monthcalendar(self._año, self._mes)
            for fila, semana in enumerate(semanas):
                for col, dia in enumerate(semana):
                    if dia == 0:
                        tk.Label(self.frm_grid, text="", bg=C_WHITE, width=3).grid(
                            row=fila, column=col)
                        continue
                    es_hoy   = (dia == hoy.day and self._mes == hoy.month and self._año == hoy.year)
                    es_selec = (dia == self._dia)
                    bg = C_ACCENT if es_selec else ("#E3F2FD" if es_hoy else C_WHITE)
                    fg = C_WHITE  if es_selec else C_TEXT
                    btn = tk.Button(
                        self.frm_grid, text=str(dia), width=3,
                        bg=bg, fg=fg,
                        activebackground="#1565C0", activeforeground=C_WHITE,
                        relief="flat", cursor="hand2", font=("Arial", 9),
                        command=lambda d=dia: self._seleccionar_dia(d)
                    )
                    btn.grid(row=fila, column=col, padx=1, pady=1, ipady=2)

    def _mes_anterior(self):
        if self._mes == 1:
            self._mes = 12; self._año -= 1
        else:
            self._mes -= 1
        self._renderizar_mes()

    def _mes_siguiente(self):
        if self._mes == 12:
            self._mes = 1; self._año += 1
        else:
            self._mes += 1
        self._renderizar_mes()

    def _seleccionar_dia(self, dia):
        self._dia = dia
        self.var_fecha.set(datetime(self._año, self._mes, dia).strftime("%d/%m/%Y"))
        self.destroy()

    def _seleccionar_mes(self):
        self.var_fecha.set(f"{self._mes:02d}/{self._año}")
        self.destroy()

    def _seleccionar_hoy(self):
        hoy = datetime.now()
        self._año, self._mes, self._dia = hoy.year, hoy.month, hoy.day
        if self.modo == "mensual":
            self._seleccionar_mes()
        else:
            self._seleccionar_dia(hoy.day)

    def _posicionar(self, widget_referencia):
        self.update_idletasks()
        try:
            x = widget_referencia.winfo_rootx()
            y = widget_referencia.winfo_rooty() + widget_referencia.winfo_height() + 2
        except Exception:
            x, y = 100, 100
        self.geometry(f"+{x}+{y}")

    def _on_focus_out(self, event):
        self.after(100, self._verificar_foco)

    def _verificar_foco(self):
        try:
            if self.focus_get() is None:
                self.destroy()
        except Exception:
            self.destroy()


# ── Exportación: PDF ──────────────────────────────────────────────────────────

def exportar_pdf(ruta: str, tipo: str, periodo: str, filas: list[tuple]):
    """Genera un PDF profesional con la tabla de retiros usando reportlab."""

    # Colores corporativos
    AZUL_OSCURO  = colors.HexColor("#0D2B6B")   # encabezado principal
    AZUL_MEDIO   = colors.HexColor("#1565C0")   # subencabezado
    AZUL_CLARO   = colors.HexColor("#1976D2")   # acento
    GRIS_LINEA   = colors.HexColor("#B0BEC5")
    FILA_PAR     = colors.HexColor("#EEF4FF")
    FILA_IMPAR   = colors.white
    TEXTO_HEADER = colors.white
    TEXTO_DATA   = colors.HexColor("#212121")
    NARANJA_TOTAL= colors.HexColor("#E65100")

    doc = SimpleDocTemplate(
        ruta,
        pagesize=landscape(letter),
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    story  = []

    # ── Estilos de texto ──────────────────────────────────────────────────────
    titulo_style = ParagraphStyle(
        "titulo",
        parent=styles["Title"],
        fontSize=18,
        textColor=AZUL_OSCURO,
        spaceAfter=2,
        fontName="Helvetica-Bold",
        leading=22,
    )
    subtitulo_style = ParagraphStyle(
        "subtitulo",
        parent=styles["Normal"],
        fontSize=10,
        textColor=AZUL_MEDIO,
        spaceAfter=2,
        fontName="Helvetica-Bold",
    )
    meta_style = ParagraphStyle(
        "meta",
        parent=styles["Normal"],
        fontSize=8.5,
        textColor=colors.HexColor("#546E7A"),
        spaceAfter=14,
        fontName="Helvetica",
    )

    # ── Encabezado del documento ──────────────────────────────────────────────
    story.append(Paragraph("Reporte de Retiros", titulo_style))
    story.append(Paragraph(f"Tipo: {tipo}  ·  Período: {periodo}", subtitulo_style))
    story.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y')} a las {datetime.now().strftime('%H:%M')} hrs",
        meta_style
    ))

    # Línea divisoria bajo el encabezado
    story.append(HRFlowable(width="100%", thickness=1.5, color=AZUL_MEDIO, spaceAfter=12))

    # ── Tabla de datos ────────────────────────────────────────────────────────
    # Nuevo orden: No. Transacción | Importe | Caja | Usuario | Fecha
    encabezado = [list(COLUMNAS_HEADER)]
    data_rows  = [list(f) for f in filas]

    # Fila de totales (suma de importe si es numérico)
    total_importe = ""
    try:
        suma = sum(
            float(str(f[1]).replace("$", "").replace(",", ""))
            for f in filas
        )
        total_importe = f"${suma:,.2f}"
    except Exception:
        total_importe = "—"

    fila_total = ["TOTAL", total_importe, "", "", f"{len(filas)} registros"]
    data = encabezado + data_rows + [fila_total]

    # Anchos proporcionales: Transacción, Importe, Caja, Usuario, Fecha
    col_widths = [2.1*inch, 1.5*inch, 1.3*inch, 1.8*inch, 1.4*inch]
    num_filas  = len(data)
    num_datos  = num_filas - 2  # sin encabezado ni total

    tbl = Table(data, colWidths=col_widths, repeatRows=1)

    # Construir estilos por fila para el alternado
    style_cmds = [
        # ── Encabezado ──────────────────────────────────────────────────────
        ("BACKGROUND",    (0, 0), (-1, 0), AZUL_OSCURO),
        ("TEXTCOLOR",     (0, 0), (-1, 0), TEXTO_HEADER),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 10),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",        (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("LINEBELOW",     (0, 0), (-1, 0), 2, AZUL_CLARO),

        # ── Datos ───────────────────────────────────────────────────────────
        ("FONTNAME",      (0, 1), (-1, num_datos), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, num_datos), 9),
        ("ALIGN",         (0, 1), (-1, num_datos), "CENTER"),
        ("VALIGN",        (0, 1), (-1, num_datos), "MIDDLE"),
        ("TOPPADDING",    (0, 1), (-1, num_datos), 6),
        ("BOTTOMPADDING", (0, 1), (-1, num_datos), 6),

        # ── Fila de totales ─────────────────────────────────────────────────
        ("BACKGROUND",    (0, -1), (-1, -1), AZUL_OSCURO),
        ("TEXTCOLOR",     (0, -1), (-1, -1), TEXTO_HEADER),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, -1), (-1, -1), 9.5),
        ("ALIGN",         (0, -1), (-1, -1), "CENTER"),
        ("VALIGN",        (0, -1), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, -1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("LINEABOVE",     (0, -1), (-1, -1), 1.5, AZUL_CLARO),
        # El importe total en naranja destacado
        ("TEXTCOLOR",     (1, -1), (1, -1), colors.HexColor("#FFD54F")),

        # ── Bordes generales ────────────────────────────────────────────────
        ("GRID",          (0, 0), (-1, -1), 0.4, GRIS_LINEA),
        ("BOX",           (0, 0), (-1, -1), 1,   AZUL_MEDIO),
    ]

    # Filas alternadas
    for i in range(1, num_datos + 1):
        bg = FILA_PAR if i % 2 == 0 else FILA_IMPAR
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
        style_cmds.append(("TEXTCOLOR",  (0, i), (-1, i), TEXTO_DATA))

    tbl.setStyle(TableStyle(style_cmds))
    story.append(tbl)

    # ── Nota al pie ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.8, color=GRIS_LINEA, spaceAfter=6))
    nota_style = ParagraphStyle(
        "nota",
        parent=styles["Normal"],
        fontSize=7.5,
        textColor=colors.HexColor("#78909C"),
        fontName="Helvetica-Oblique",
    )
    story.append(Paragraph(
        f"Documento generado automáticamente · Sistema de Reportes de Retiros · {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        nota_style
    ))

    doc.build(story)


# ── Exportación: Excel ────────────────────────────────────────────────────────

def exportar_excel(ruta: str, tipo: str, periodo: str, filas: list[tuple]):
    """Genera un .xlsx profesional con la tabla de retiros usando openpyxl."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte de Retiros"

    # ── Colores ───────────────────────────────────────────────────────────────
    COLOR_AZUL_OSCURO = "0D2B6B"
    COLOR_AZUL_MEDIO  = "1565C0"
    COLOR_AZUL_CLARO  = "BBDEFB"
    COLOR_FILA_PAR    = "EEF4FF"
    COLOR_TOTAL_BG    = "0D2B6B"
    COLOR_TOTAL_MONTO = "FFD54F"
    COLOR_BLANCO      = "FFFFFF"

    # ── Bordes ────────────────────────────────────────────────────────────────
    thin   = Side(style="thin",   color="B0BEC5")
    medium = Side(style="medium", color=COLOR_AZUL_MEDIO)
    borde_datos  = Border(left=thin,   right=thin,   top=thin,   bottom=thin)
    borde_header = Border(left=medium, right=medium, top=medium, bottom=medium)

    # ── Fila 1: Banda de color superior (decorativa) ──────────────────────────
    ws.row_dimensions[1].height = 8
    for col in range(1, 6):
        c = ws.cell(row=1, column=col)
        c.fill = PatternFill("solid", fgColor=COLOR_AZUL_OSCURO)

    # ── Fila 2: Título principal ──────────────────────────────────────────────
    ws.merge_cells("A2:E2")
    ws["A2"] = "REPORTE DE RETIROS"
    ws["A2"].font      = Font(name="Calibri", bold=True, color=COLOR_BLANCO, size=16)
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws["A2"].fill      = PatternFill("solid", fgColor=COLOR_AZUL_OSCURO)
    ws.row_dimensions[2].height = 32

    # ── Fila 3: Subtítulo con metadatos ──────────────────────────────────────
    ws.merge_cells("A3:E3")
    ws["A3"] = f"Tipo: {tipo}   |   Período: {periodo}   |   Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} hrs"
    ws["A3"].font      = Font(name="Calibri", italic=True, color=COLOR_AZUL_CLARO, size=10)
    ws["A3"].alignment = Alignment(horizontal="center", vertical="center")
    ws["A3"].fill      = PatternFill("solid", fgColor=COLOR_AZUL_OSCURO)
    ws.row_dimensions[3].height = 20

    # ── Fila 4: Espacio ───────────────────────────────────────────────────────
    ws.row_dimensions[4].height = 6

    # ── Fila 5: Encabezados de columna ────────────────────────────────────────
    # Nuevo orden: No. Transacción | Importe | Caja | Usuario | Fecha
    for col_idx, header in enumerate(COLUMNAS_HEADER, start=1):
        cell = ws.cell(row=5, column=col_idx, value=header)
        cell.font      = Font(name="Calibri", bold=True, color=COLOR_BLANCO, size=11)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
        cell.fill      = PatternFill("solid", fgColor=COLOR_AZUL_MEDIO)
        cell.border    = borde_header
    ws.row_dimensions[5].height = 22

    # ── Filas de datos (desde fila 6) ─────────────────────────────────────────
    for row_idx, fila in enumerate(filas, start=6):
        es_par = (row_idx % 2 == 0)
        fill = PatternFill("solid", fgColor=COLOR_FILA_PAR) if es_par else None
        for col_idx, valor in enumerate(fila, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=valor)
            cell.font      = Font(name="Calibri", size=10, color="212121")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border    = borde_datos
            if fill:
                cell.fill = fill
        ws.row_dimensions[row_idx].height = 18

    # ── Fila de totales ───────────────────────────────────────────────────────
    fila_total = len(filas) + 6
    total_importe = ""
    try:
        suma = sum(
            float(str(f[1]).replace("$", "").replace(",", ""))
            for f in filas
        )
        total_importe = f"${suma:,.2f}"
    except Exception:
        total_importe = "—"

    totales = ["TOTAL", total_importe, "", "", f"{len(filas)} registros"]
    for col_idx, valor in enumerate(totales, start=1):
        cell = ws.cell(row=fila_total, column=col_idx, value=valor)
        cell.fill      = PatternFill("solid", fgColor=COLOR_TOTAL_BG)
        cell.font      = Font(name="Calibri", bold=True, color=COLOR_BLANCO, size=11)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = borde_header
    # Monto total en amarillo dorado
    ws.cell(row=fila_total, column=2).font = Font(
        name="Calibri", bold=True, color=COLOR_TOTAL_MONTO, size=11
    )
    ws.row_dimensions[fila_total].height = 22

    # ── Fila decorativa final ─────────────────────────────────────────────────
    fila_deco = fila_total + 1
    ws.row_dimensions[fila_deco].height = 6
    for col in range(1, 6):
        ws.cell(row=fila_deco, column=col).fill = PatternFill("solid", fgColor=COLOR_AZUL_OSCURO)

    # ── Anchos de columna ─────────────────────────────────────────────────────
    # Nuevo orden: No. Transacción, Importe, Caja, Usuario, Fecha
    anchos = [22, 16, 12, 18, 14]
    for col_idx, ancho in enumerate(anchos, start=1):
        ws.column_dimensions[ws.cell(row=5, column=col_idx).column_letter].width = ancho

    # ── Congelar encabezados ──────────────────────────────────────────────────
    ws.freeze_panes = "A6"

    # ── Zoom y vista ─────────────────────────────────────────────────────────
    ws.sheet_view.zoomScale = 110

    wb.save(ruta)


# ── Vista principal ───────────────────────────────────────────────────────────

class ReportesView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self._create_widgets()

    def _create_widgets(self):
        tk.Label(self, text="Generador de Reportes", font=("Arial", 18, "bold"),
                 bg=C_BG, fg=C_HEADER).pack(anchor="w", pady=(0, 20))

        main_frame = tk.Frame(self, bg=C_BG)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- PANEL IZQUIERDO (CONTROLES) ---
        ctrl_frame = tk.Frame(main_frame, bg=C_WHITE, width=280,
                              highlightbackground="#E0E0E0", highlightthickness=1)
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        ctrl_frame.pack_propagate(False)

        tk.Label(ctrl_frame, text="Parámetros", font=("Arial", 12, "bold"),
                 bg=C_WHITE, fg=C_HEADER).pack(pady=(15, 10), anchor="w", padx=15)

        tk.Label(ctrl_frame, text="Tipo de Reporte:", font=("Arial", 10),
                 bg=C_WHITE, fg=C_TEXT).pack(anchor="w", padx=15)
        self.combo_tipo = ttk.Combobox(ctrl_frame,
                                       values=["Diario", "Semanal", "Mensual"],
                                       state="readonly")
        self.combo_tipo.current(0)
        self.combo_tipo.pack(fill=tk.X, padx=15, pady=(0, 15))
        self.combo_tipo.bind("<<ComboboxSelected>>", self._on_tipo_reporte_changed)

        self.lbl_fecha = tk.Label(ctrl_frame, text="Fecha (DD/MM/AAAA):",
                                  font=("Arial", 10), bg=C_WHITE, fg=C_TEXT)
        self.lbl_fecha.pack(anchor="w", padx=15)

        frm_fecha = tk.Frame(ctrl_frame, bg=C_WHITE)
        frm_fecha.pack(fill=tk.X, padx=15, pady=(0, 20))

        self.var_fecha = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha = ttk.Entry(frm_fecha, textvariable=self.var_fecha)
        self.entry_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_cal = tk.Button(
            frm_fecha, text="📅",
            command=self._abrir_calendario,
            bg=C_WHITE, fg=C_ACCENT,
            relief="flat", cursor="hand2",
            font=("Arial", 12), padx=2
        )
        self.btn_cal.pack(side=tk.LEFT, padx=(3, 0))

        tk.Button(ctrl_frame, text="Generar Previsualización",
                  bg=C_BTN, fg=C_WHITE, font=("Arial", 10, "bold"),
                  relief=tk.FLAT, cursor="hand2",
                  command=self._on_generar_reporte).pack(
                      fill=tk.X, padx=15, pady=(0, 30), ipady=5)

        tk.Label(ctrl_frame, text="Exportar Resultados", font=("Arial", 10, "bold"),
                 bg=C_WHITE, fg=C_HEADER).pack(anchor="w", padx=15, pady=(10, 5))

        tk.Button(ctrl_frame, text="Exportar a PDF",
                  bg="#D32F2F", fg=C_WHITE, font=("Arial", 10),
                  relief=tk.FLAT, cursor="hand2",
                  command=self._on_exportar_pdf).pack(
                      fill=tk.X, padx=15, pady=(5, 5), ipady=3)

        tk.Button(ctrl_frame, text="Exportar a Excel",
                  bg="#2E7D32", fg=C_WHITE, font=("Arial", 10),
                  relief=tk.FLAT, cursor="hand2",
                  command=self._on_exportar_excel).pack(
                      fill=tk.X, padx=15, pady=(0, 15), ipady=3)

        # --- PANEL DERECHO (PREVISUALIZACIÓN) ---
        preview_frame = tk.Frame(main_frame, bg=C_WHITE,
                                 highlightbackground="#E0E0E0", highlightthickness=1)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(preview_frame, text="Vista Previa de Datos",
                 font=("Arial", 12, "bold"), bg=C_WHITE,
                 fg=C_HEADER).pack(anchor="w", padx=15, pady=(15, 10))

        # Nuevo orden de columnas en la vista previa
        columnas = ("transaccion", "importe", "caja", "usuario", "fecha")
        self.tree = ttk.Treeview(preview_frame, columns=columnas, show="headings")

        for col, header, width, anchor in [
            ("transaccion", "No. Transacción", 120, "center"),
            ("importe",     "Importe",         100, "center"),
            ("caja",        "Caja",             80, "center"),
            ("usuario",     "Usuario",          100, "center"),
            ("fecha",       "Fecha",             90, "center"),
        ]:
            self.tree.heading(col, text=header, anchor="center")
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                       padx=(15, 0), pady=(0, 15))

    # ── calendario ────────────────────────────────────────────────────────────

    def _abrir_calendario(self):
        tipo = self.combo_tipo.get()
        if tipo == "Semanal":
            messagebox.showinfo(
                "Modo Semanal",
                "Para el reporte semanal escribe la semana manualmente.\nEjemplo: Semana 10 - 2026",
                parent=self
            )
            return
        modo = "mensual" if tipo == "Mensual" else "diario"
        _CalendarioPopup(self.entry_fecha, self.var_fecha, modo=modo)

    # ── callbacks ────────────────────────────────────────────────────────────

    def _on_tipo_reporte_changed(self, event):
        tipo = self.combo_tipo.get()
        if tipo == "Diario":
            self.lbl_fecha.config(text="Fecha (DD/MM/AAAA):")
            self.var_fecha.set(datetime.now().strftime("%d/%m/%Y"))
            self.btn_cal.config(state="normal")
        elif tipo == "Semanal":
            self.lbl_fecha.config(text="Semana (Ej. Semana 10 - 2026):")
            self.var_fecha.set("")
            self.btn_cal.config(state="disabled")
        elif tipo == "Mensual":
            self.lbl_fecha.config(text="Mes (MM/AAAA):")
            self.var_fecha.set(datetime.now().strftime("%m/%Y"))
            self.btn_cal.config(state="normal")

    def _on_generar_reporte(self):
        tipo        = self.combo_tipo.get()
        fecha_texto = self.var_fecha.get().strip()
        self._refresh_reporte()

        try:
            fecha_inicio, fecha_fin = self._calcular_rango(tipo, fecha_texto)
        except ValueError as e:
            messagebox.showerror("Fecha inválida", str(e), parent=self)
            return

        try:
            retiros = retiros_por_periodo(fecha_inicio, fecha_fin)
        except Exception as e:
            messagebox.showerror("Error al consultar datos", str(e), parent=self)
            return

        if not retiros:
            messagebox.showinfo("Sin resultados",
                                "No se encontraron retiros para el período seleccionado.",
                                parent=self)
            return

        # Nuevo orden: No. Transacción, Importe, Caja, Usuario, Fecha
        for r in retiros:
            self.tree.insert("", tk.END, values=(
                r["numero_transaccion"],
                f"${r['importe']:,.2f}",
                r["nombre_caja"],
                r["usuario"],
                datetime.strptime(str(r["fecha"])[:10], "%Y-%m-%d").strftime("%d/%m/%Y"),
            ))

    def _calcular_rango(self, tipo: str, fecha_texto: str):
        """Devuelve (fecha_inicio, fecha_fin) como datetime.date según el tipo de reporte."""
        if tipo == "Diario":
            try:
                fecha = datetime.strptime(fecha_texto, "%d/%m/%Y").date()
            except ValueError:
                raise ValueError("Formato de fecha incorrecto. Usa DD/MM/AAAA.")
            return fecha, fecha

        elif tipo == "Semanal":
            # Espera "Semana N - AAAA"
            try:
                partes  = fecha_texto.replace("Semana", "").strip().split("-")
                semana  = int(partes[0].strip())
                año     = int(partes[1].strip())
                # Lunes de esa semana ISO
                lunes   = datetime.strptime(f"{año}-W{semana:02d}-1", "%Y-W%W-%w").date()
                domingo = lunes + timedelta(days=6)
                return lunes, domingo
            except Exception:
                raise ValueError(
                    "Formato de semana incorrecto.\nUsa el formato: Semana 10 - 2026"
                )

        elif tipo == "Mensual":
            try:
                fecha = datetime.strptime(fecha_texto, "%m/%Y").date()
            except ValueError:
                raise ValueError("Formato de mes incorrecto. Usa MM/AAAA.")
            # Primer y último día del mes
            import calendar as _cal
            ultimo_dia = _cal.monthrange(fecha.year, fecha.month)[1]
            return fecha.replace(day=1), fecha.replace(day=ultimo_dia)

        raise ValueError(f"Tipo de reporte desconocido: {tipo}")

    def _get_filas(self) -> list[tuple]:
        """Devuelve las filas visibles en el Treeview."""
        return [self.tree.item(iid, "values") for iid in self.tree.get_children()]

    def _on_exportar_pdf(self):
        filas = self._get_filas()
        if not filas:
            messagebox.showwarning("Sin datos",
                                   "Genera una previsualización antes de exportar.",
                                   parent=self)
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar Reporte PDF"
        )
        if not archivo:
            return
        try:
            exportar_pdf(archivo, self.combo_tipo.get(),
                         self.var_fecha.get(), filas)
            messagebox.showinfo("PDF exportado",
                                f"Reporte guardado correctamente en:\n{archivo}",
                                parent=self)
        except Exception as e:
            messagebox.showerror("Error al exportar PDF", str(e), parent=self)

    def _on_exportar_excel(self):
        filas = self._get_filas()
        if not filas:
            messagebox.showwarning("Sin datos",
                                   "Genera una previsualización antes de exportar.",
                                   parent=self)
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar Reporte Excel"
        )
        if not archivo:
            return
        try:
            exportar_excel(archivo, self.combo_tipo.get(),
                           self.var_fecha.get(), filas)
            messagebox.showinfo("Excel exportado",
                                f"Reporte guardado correctamente en:\n{archivo}",
                                parent=self)
        except Exception as e:
            messagebox.showerror("Error al exportar Excel", str(e), parent=self)

    def _refresh_reporte(self):
        for item in self.tree.get_children():
            self.tree.delete(item)