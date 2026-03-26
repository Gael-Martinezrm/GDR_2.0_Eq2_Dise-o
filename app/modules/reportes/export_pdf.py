"""
app/modules/reportes/export_pdf.py

Exportación de reportes a formato PDF usando ReportLab.
INCLUYE COMPARATIVAS SEGÚN TIPO DE REPORTE
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime, date, timedelta
import os

from app.modules.comparaciones import model as comparaciones_model
from app.utils.helpers import (
    get_fecha_inicio_semana,
    get_fecha_fin_semana,
    get_fecha_inicio_mes,
    get_fecha_fin_mes
)


def exportar_pdf(datos: dict, titulo: str, ruta_archivo: str) -> bool:
    """
    Exporta los datos del reporte a un archivo PDF.
    Incluye comparativas según el tipo de reporte.
    """
    try:
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        
        doc = SimpleDocTemplate(ruta_archivo, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontSize = 16
        title_style.alignment = 1
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            alignment=1,
            textColor=colors.grey
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Normal'],
            fontSize=12,
            alignment=0,
            textColor=colors.HexColor('#1565C0'),
            spaceAfter=10
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 9
        
        elements = []
        
        # ===== TÍTULO PRINCIPAL =====
        elements.append(Paragraph(titulo, title_style))
        elements.append(Spacer(1, 0.1 * inch))
        
        # ===== PERÍODO DEL REPORTE =====
        periodo_text = f"Período: {datos['fecha_inicio']} al {datos['fecha_fin']}"
        elements.append(Paragraph(periodo_text, subtitle_style))
        elements.append(Spacer(1, 0.1 * inch))
        
        # ===== FECHA DE GENERACIÓN =====
        fecha_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        elements.append(Paragraph(fecha_text, subtitle_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # ===== TABLA DE RETIROS =====
        elements.append(Paragraph("Detalle de Retiros", heading_style))
        
        table_data = [['ID', 'Fecha', 'Caja', 'Usuario', 'Monto']]
        
        for retiro in datos['retiros']:
            fecha_str = str(retiro['fecha_retiro'])[:16]
            table_data.append([
                str(retiro['id']),
                fecha_str,
                retiro.get('nombre_caja', 'N/A'),
                retiro.get('nombre_usuario', retiro.get('username', 'N/A')),
                f"${retiro['monto']:,.2f}"
            ])
        
        table = Table(table_data, colWidths=[0.8*inch, 1.5*inch, 1.2*inch, 1.5*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # ===== TOTALES =====
        total_text = f"<b>TOTAL GENERAL:</b> ${datos['total']:,.2f}"
        elements.append(Paragraph(total_text, normal_style))
        
        cantidad_text = f"Cantidad de retiros: {datos['cantidad']}"
        elements.append(Paragraph(cantidad_text, normal_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        # ===== COMPARATIVAS SEGÚN TIPO DE REPORTE =====
        # Extraer el tipo de reporte del título
        tipo_reporte = ""
        if "Diario" in titulo:
            tipo_reporte = "Diario"
        elif "Semanal" in titulo:
            tipo_reporte = "Semanal"
        elif "Mensual" in titulo:
            tipo_reporte = "Mensual"
        
        # Solo mostrar comparativas si es Semanal o Mensual
        if tipo_reporte == "Semanal":
            elements.append(Paragraph("Comparativa Semanal", heading_style))
            elements.append(Spacer(1, 0.1 * inch))
            
            try:
                comparacion = comparaciones_model.comparar_semana_actual_con_anterior()
                
                semana_actual_total = comparacion['semana2']['total']
                semana_anterior_total = comparacion['semana1']['total']
                diferencia = comparacion['diferencia']
                porcentaje = comparacion['porcentaje']
                tendencia = comparacion['tendencia']
                
                datos_tabla = [
                    ['', 'Semana Anterior', 'Semana Actual', 'Variación'],
                    ['Total', f"${semana_anterior_total:,.2f}", f"${semana_actual_total:,.2f}", 
                     f"{'▲' if tendencia == 'aumento' else '▼' if tendencia == 'disminucion' else '='} ${abs(diferencia):,.2f} ({porcentaje:.1f}%)"]
                ]
                
                tabla = Table(datos_tabla, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (3, 1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (3, 1), (3, 1), 
                     colors.HexColor('#2E7D32') if tendencia == 'aumento' 
                     else colors.HexColor('#C62828') if tendencia == 'disminucion' 
                     else colors.HexColor('#ED6C02')),
                    ('TEXTCOLOR', (3, 1), (3, 1), colors.white),
                ]))
                
                elements.append(tabla)
                
                # Detalle por caja
                if 'detalle_cajas' in comparacion and comparacion['detalle_cajas']:
                    elements.append(Spacer(1, 0.1 * inch))
                    elements.append(Paragraph("Detalle por Caja", heading_style))
                    
                    datos_detalle = [['Caja', 'Semana Anterior', 'Semana Actual', 'Variación']]
                    for caja in comparacion['detalle_cajas']:
                        variacion_caja = caja['total_semana2'] - caja['total_semana1']
                        signo = "▲" if variacion_caja > 0 else "▼" if variacion_caja < 0 else "="
                        datos_detalle.append([
                            caja['nombre'],
                            f"${caja['total_semana1']:,.2f}",
                            f"${caja['total_semana2']:,.2f}",
                            f"{signo} ${abs(variacion_caja):,.2f}"
                        ])
                    
                    tabla_detalle = Table(datos_detalle, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                    tabla_detalle.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (3, -1), 'RIGHT'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                    ]))
                    
                    elements.append(tabla_detalle)
                
            except Exception as e:
                elements.append(Paragraph("No hay datos suficientes para comparativa semanal", normal_style))
        
        elif tipo_reporte == "Mensual":
            elements.append(Paragraph("Comparativa Mensual", heading_style))
            elements.append(Spacer(1, 0.1 * inch))
            
            try:
                comparacion = comparaciones_model.comparar_mes_actual_con_anterior()
                
                mes_actual_total = comparacion['mes2']['total']
                mes_anterior_total = comparacion['mes1']['total']
                diferencia = comparacion['diferencia']
                porcentaje = comparacion['porcentaje']
                tendencia = comparacion['tendencia']
                
                datos_tabla = [
                    ['', 'Mes Anterior', 'Mes Actual', 'Variación'],
                    ['Total', f"${mes_anterior_total:,.2f}", f"${mes_actual_total:,.2f}", 
                     f"{'▲' if tendencia == 'aumento' else '▼' if tendencia == 'disminucion' else '='} ${abs(diferencia):,.2f} ({porcentaje:.1f}%)"]
                ]
                
                tabla = Table(datos_tabla, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (3, 1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (3, 1), (3, 1), 
                     colors.HexColor('#2E7D32') if tendencia == 'aumento' 
                     else colors.HexColor('#C62828') if tendencia == 'disminucion' 
                     else colors.HexColor('#ED6C02')),
                    ('TEXTCOLOR', (3, 1), (3, 1), colors.white),
                ]))
                
                elements.append(tabla)
                
                # Detalle por caja
                if 'detalle_cajas' in comparacion and comparacion['detalle_cajas']:
                    elements.append(Spacer(1, 0.1 * inch))
                    elements.append(Paragraph("Detalle por Caja", heading_style))
                    
                    datos_detalle = [['Caja', 'Mes Anterior', 'Mes Actual', 'Variación']]
                    for caja in comparacion['detalle_cajas']:
                        variacion_caja = caja['total_mes2'] - caja['total_mes1']
                        signo = "▲" if variacion_caja > 0 else "▼" if variacion_caja < 0 else "="
                        datos_detalle.append([
                            caja['nombre'],
                            f"${caja['total_mes1']:,.2f}",
                            f"${caja['total_mes2']:,.2f}",
                            f"{signo} ${abs(variacion_caja):,.2f}"
                        ])
                    
                    tabla_detalle = Table(datos_detalle, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                    tabla_detalle.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (3, -1), 'RIGHT'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                    ]))
                    
                    elements.append(tabla_detalle)
                
            except Exception as e:
                elements.append(Paragraph("No hay datos suficientes para comparativa mensual", normal_style))
        
        # Si es Diario, no se añaden comparativas
        
        doc.build(elements)
        return True
        
    except Exception as e:
        raise Exception(f"Error exportando PDF: {e}")