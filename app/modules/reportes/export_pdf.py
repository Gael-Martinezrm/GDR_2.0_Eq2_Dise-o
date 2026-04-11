"""
app/modules/reportes/export_pdf.py

Exportación de reportes a formato PDF usando ReportLab.
Diseño Profesional: Sistema de Gestión de Asilo - CREAN.
"""

from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable

# ── PALETA DE COLORES PROFESIONAL ─────────────────────────────────────────────
# Una paleta más sobria basada en azules corporativos y grises cálidos
PRIMARY_DARK = colors.HexColor("#0D47A1")  # Azul Profundo
PRIMARY      = colors.HexColor("#1976D2")  # Azul Principal
ACCENT       = colors.HexColor("#42A5F5")  # Azul de acento (bordes)
BG_LIGHT     = colors.HexColor("#F8FAFC")  # Fondo casi blanco para filas
SURFACE      = colors.HexColor("#E3F2FD")  # Superficie de tarjetas
TEXT_MAIN    = colors.HexColor("#1E293B")  # Gris muy oscuro para lectura
TEXT_MUTE    = colors.HexColor("#64748B")  # Gris para metadatos
WHITE        = colors.white

class _CajaCriterios(Flowable):
    """Caja de información con diseño de 'Card' moderna."""
    def __init__(self, residente, periodo, total, ancho):
        super().__init__()
        self.residente = residente
        self.periodo = periodo
        self.total = total
        self.ancho = ancho
        self.alto = 65

    def draw(self):
        c = self.canv
        # Sombra suave (simulada)
        c.setFillColor(colors.HexColor("#000000", alpha=0.05))
        c.roundRect(2, -2, self.ancho, self.alto, 8, fill=1, stroke=0)
        
        # Fondo Principal
        c.setFillColor(SURFACE)
        c.roundRect(0, 0, self.ancho, self.alto, 8, fill=1, stroke=0)
        
        # Acento lateral
        c.setFillColor(PRIMARY)
        c.roundRect(0, 0, 6, self.alto, 2, fill=1, stroke=0)

        # Textos
        c.setFillColor(PRIMARY_DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(15, self.alto - 18, "FILTROS APLICADOS")
        
        c.setStrokeColor(ACCENT)
        c.setLineWidth(0.5)
        c.line(15, self.alto - 22, 120, self.alto - 22)

        # Grid de datos
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(TEXT_MUTE)
        c.drawString(15, 25, "RESIDENTE:")
        c.drawString(180, 25, "PERÍODO:")
        
        c.setFillColor(TEXT_MAIN)
        c.setFont("Helvetica", 9)
        c.drawString(80, 25, str(self.residente).upper())
        c.drawString(235, 25, str(self.periodo))

        # Badge de Total (Derecha)
        c.setFillColor(PRIMARY_DARK)
        c.roundRect(self.ancho - 100, 10, 90, 45, 6, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(self.ancho - 55, 38, "TOTAL REGISTROS")
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(self.ancho - 55, 18, str(self.total))

class _CajaResumen(Flowable):
    """Footer de estadísticas con diseño de KPI cards."""
    def __init__(self, stats, ancho):
        super().__init__()
        self.stats = stats
        self.ancho = ancho
        self.alto = 60

    def draw(self):
        c = self.canv
        n = len(self.stats)
        col_w = self.ancho / n
        
        # Fondo contenedor
        c.setFillColor(BG_LIGHT)
        c.roundRect(0, 0, self.ancho, self.alto, 10, fill=1, stroke=1)
        c.setStrokeColor(ACCENT)

        for i, (valor, etiqueta) in enumerate(self.stats):
            x = i * col_w
            # Valor central
            c.setFillColor(PRIMARY)
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(x + col_w/2, 30, str(valor))
            # Etiqueta
            c.setFillColor(TEXT_MUTE)
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(x + col_w/2, 15, etiqueta.upper())
            
            if i < n - 1: # Divisor
                c.setStrokeColor(colors.lightgrey)
                c.line(x + col_w, 15, x + col_w, 45)

def exportar_pdf(datos: dict, titulo: str, ruta_archivo: str) -> bool:
    PAGE_W, PAGE_H = letter
    MARGIN = 0.6 * inch
    CONTENT_W = PAGE_W - (2 * MARGIN)

    doc = SimpleDocTemplate(
        ruta_archivo,
        pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.2 * inch, bottomMargin=0.8 * inch
    )

    # Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'MainTitle', parent=styles['Heading1'], fontSize=24,
        textColor=PRIMARY_DARK, spaceAfter=2, fontName="Helvetica-Bold"
    )
    style_subtitle = ParagraphStyle(
        'SubTitle', fontSize=11, textColor=TEXT_MUTE,
        spaceAfter=15, fontName="Helvetica-Oblique"
    )

    def header_footer(canvas, doc):
        canvas.saveState()
        # Header Blue Bar
        canvas.setFillColor(PRIMARY_DARK)
        canvas.rect(0, PAGE_H - 45, PAGE_W, 45, fill=1, stroke=0)
        
        # Logo Text / System Name
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(MARGIN, PAGE_H - 28, datos.get("sistema", "CREAN - GESTIÓN").upper())
        
        # Metadata
        canvas.setFont("Helvetica", 8)
        fecha = datetime.now().strftime("%d/%m/%Y | %H:%M")
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 28, f"Reporte Oficial | {fecha}")
        
        # Footer
        canvas.setStrokeColor(ACCENT)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, 0.6*inch, PAGE_W - MARGIN, 0.6*inch)
        canvas.setFillColor(TEXT_MUTE)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(MARGIN, 0.45*inch, datos.get("pie", "Confidencial"))
        canvas.drawRightString(PAGE_W - MARGIN, 0.45*inch, f"Hoja {doc.page}")
        canvas.restoreState()

    story = []

    # 1. Título y Subtítulo
    story.append(Paragraph(titulo.upper(), style_title))
    story.append(Paragraph(datos.get("subtitulo", ""), style_subtitle))
    
    # 2. Caja de Criterios
    story.append(_CajaCriterios(
        datos.get("residente", "N/A"),
        datos.get("periodo", "N/A"),
        datos.get("stats", [("0", "")])[0][0],
        CONTENT_W
    ))
    story.append(Spacer(1, 20))

    # 3. Tabla de Datos
    columnas = datos.get("columnas", [])
    filas = datos.get("filas", [])

    if columnas:
        # Estilo de celdas
        h_style = ParagraphStyle('h', fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, alignment=TA_CENTER)
        b_style = ParagraphStyle('b', fontName="Helvetica", fontSize=8.5, textColor=TEXT_MAIN, alignment=TA_CENTER)
        
        data = [[Paragraph(c.upper(), h_style) for c in ["#"] + columnas]]
        for i, fila in enumerate(filas, 1):
            data.append([Paragraph(str(i), b_style)] + [Paragraph(str(v), b_style) for v in fila])

        # Cálculo de anchos (Columna ID fija, resto proporcional)
        col_widths = [0.3*inch] + [(CONTENT_W - 0.3*inch) / len(columnas)] * len(columnas)
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,0), (-1,0), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, BG_LIGHT]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('LINEBELOW', (0,0), (-1,0), 2, PRIMARY_DARK),
        ]))
        story.append(t)

    # 4. Resumen Final
    story.append(Spacer(1, 25))
    if datos.get("stats"):
        story.append(KeepTogether([
            Paragraph("RESUMEN DE MÉTRICAS", ParagraphStyle('res', fontName="Helvetica-Bold", fontSize=10, textColor=TEXT_MUTE, spaceAfter=8)),
            _CajaResumen(datos["stats"], CONTENT_W)
        ]))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return True