import qrcode
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 # Cambiado a A4 normal
from reportlab.lib.utils import ImageReader
import os
import pandas as pd

def draw_single_format(c, datos, qr_img, logo_path, y_offset):
    """
    Dibuja un único formato de boleta en el canvas en una posición vertical (y_offset) específica.
    """
    width, page_height = A4
    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    # Área de la boleta: se ajusta para caber en la mitad de la página con mejores márgenes
    total_block_height = page_height / 2
    
    # Reducimos la altura del recuadro principal y dejamos espacio abajo para la tarja
    boleta_height = 350
    boleta_width = width - 50  # Margen horizontal de 25 en cada lado
    boleta_left = 25
    
    # Centramos el recuadro en el bloque vertical que le corresponde
    padding_top = 40
    boleta_bottom = y_offset + total_block_height - boleta_height - padding_top
    
    # Cuadro exterior de la boleta (en negro)
    c.setStrokeColorRGB(0, 0, 0) # Color negro para el borde
    c.setLineWidth(2)
    c.rect(boleta_left, boleta_bottom, boleta_width, boleta_height)

    # --- Líneas de división ---
    c.setLineWidth(1)
    # Línea vertical para separar QR del resto
    line_v_x = boleta_left + 165 
    c.line(line_v_x, boleta_bottom, line_v_x, boleta_bottom + boleta_height)
    # Línea horizontal para separar cabecera de datos
    line_h_y = boleta_bottom + boleta_height - 70
    c.line(line_v_x, line_h_y, boleta_left + boleta_width, line_h_y)

    #c.setStrokeColorRGB(0, 0, 0) # Restaurar color negro para otras líneas

    # --- Logo ---
    logo_w, logo_h = 50, 50
    # Posición del recuadro del logo
    logo_box_x = line_v_x + 10
    logo_box_y = line_h_y + 10
    # Dibujar el recuadro para el logo
    c.setLineWidth(1)
    c.rect(logo_box_x, logo_box_y, logo_w, logo_h)
    
    if os.path.exists(logo_path):
        # Centrar el logo dentro de su recuadro
        c.drawImage(logo_path, logo_box_x, logo_box_y, width=logo_w, height=logo_h, mask='auto')
    else:
        # Si no hay logo, escribir "LOGO" como placeholder
        c.setFont("Helvetica", 12)
        c.drawCentredString(logo_box_x + logo_w / 2, logo_box_y + (logo_h - 12) / 2, "LOGO")

    # --- QR ---
    qr_size = 162 # Tamaño ajustado
    qr_x = boleta_left + 1
    qr_y = boleta_bottom + boleta_height - qr_size - 95
    qr_buffer = io.BytesIO()
    if hasattr(qr_img, 'get_image'):
        qr_img = qr_img.get_image()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)

    c.setFont("Helvetica",11)
    text_qr = datos['key_qr']
    text_width = c.stringWidth(text_qr, "Helvetica", 11)
    c.drawString(qr_x + (qr_size - text_width) / 2, qr_y - 10, text_qr)

    # --- Cabecera ---
    header_x_center = boleta_left + boleta_width / 2 + 60
    header_y_top = boleta_bottom + boleta_height - 15
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(header_x_center, header_y_top- 10, "FORMATO")
    c.setFont("Helvetica", 9)
    c.drawCentredString(header_x_center, header_y_top - 30, "BOLETA DE RECEPCION DE MATERIA PRIMA")
    
    # Código, versión, fecha
    info_x = boleta_left + boleta_width - 95
    info_y = header_y_top +5
    c.setFont("Helvetica", 7)
    c.drawString(info_x, info_y, "Código: APP - CC-FPP 002")
    c.drawString(info_x, info_y - 9, "Versión : 01-2")
    c.drawString(info_x, info_y - 18, f"Fecha : {fecha_actual}")

    # --- Tabla de datos ---
    table_left = boleta_left + 170 # Más espacio para el QR
    table_top = boleta_bottom + boleta_height -100
    col1_x = table_left
    col2_x = table_left + 230
    row_height = 23
    font_size = 8
    font_size_big=11
    bold = "Helvetica-Bold"
    normal = "Helvetica"
    
    # Línea vertical entre columnas de datos
    line_v2_x = col2_x - 10
    c.line(line_v2_x, boleta_bottom, line_v2_x, line_h_y)
    
    # --- Columna 1 ---
    y = table_top + 20 ### mopdifica el alto 
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "CULTIVO:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['cultivo']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "TIPO DE PRODUCTO:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['tipo_producto']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "EMPRESA:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['empresa']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "FUNDO:")
    c.setFont(normal, 9)
    c.drawString(col1_x + 90, y, f"{datos['fundo']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "VARIEDAD:")
    c.setFont(normal, 9)
    c.drawString(col1_x + 90, y, f"{datos['variedad']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "Nº PALLET:")
    c.setFont(bold, 9)
    c.drawString(col1_x + 90, y, f"{datos['num_pallet']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "GUIA:")
    c.setFont(normal, 9)
    c.drawString(col1_x + 90, y, f"{datos['guia']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "VIAJE:")
    c.setFont(normal, 17)
    c.drawString(col1_x + 90, y, f"{datos['viaje']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "OBSERVACIONES:")
    c.setFont(bold, 9)
    c.drawString(col1_x + 90, y, f"{datos['observaciones']}")

    # --- Columna 2 ---
    y = table_top
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "FECHA:")
    c.setFont(bold, 14)
    c.drawString(col2_x + 50, y, f"{datos['fecha']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. BRUTO:")
    c.setFont(normal, 12)
    c.drawString(col2_x + 70, y, f"{datos['peso_bruto']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "Nº JABAS:")
    c.setFont(normal, 12)
    c.drawString(col2_x + 70, y, f"{datos['num_jabas']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "Nº JARRAS:")
    c.setFont(normal, 12)
    c.drawString(col2_x + 70, y, f"{datos['num_jarras']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. CAMPO:")
    c.setFont(normal, 12)
    c.drawString(col2_x + 70, y, f"{datos['peso_campo']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. NETO:")
    c.setFont(bold, 13) # Resaltado
    c.drawString(col2_x + 70, y, f"{datos['peso_neto']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "T° ESTADO:")
    c.setFont(bold, 9) # Resaltado
    c.drawString(col2_x + 70, y, f"{datos['temperatura_estado']}")#
    # --- Línea horizontal sobre TUNEL DE ENFRIAMIENTO ---
    line_h2_y = y - 20
    c.line(line_v2_x, line_h2_y, boleta_left + boleta_width, line_h2_y)

    y -= (row_height + 15) # Espacio extra para la nueva sección
    
    c.setFont(bold, 10)
    # Centrar el texto "TUNEL DE ENFRIAMIENTO" en el espacio disponible
    text_tunel = "TUNEL DE ENFRIAMIENTO:"
    text_tunel_width = c.stringWidth(text_tunel, bold, 10)
    # El ancho de la sección es (boleta_left + boleta_width) - line_v2_x
    section_width = (boleta_left + boleta_width) - line_v2_x
    c.drawString(line_v2_x + (section_width - text_tunel_width) / 2, y, text_tunel)
    
    # --- N° TARJA Y CALIBRE (parte inferior, en columnas) ---
    tarja_y = boleta_bottom + 25  # Más cerca del borde inferior
    col_width = 40  # Ancho de cada columna
    # Columna izquierda: Nº TARJA
    c.setFont(bold, 12)
    c.drawCentredString(table_left + col_width+20 // 2, tarja_y + 32, "Nº TARJA:")
    c.setFont(bold, 28)
    c.drawCentredString(table_left + col_width+20 // 2, tarja_y, f"{datos['num_tarja']}")

    # Columna derecha: CALIBRE      
    calibre_x = table_left + col_width + col_width // 2 + 60  # Ajusta el +60 según el ancho de tu boleta
    c.setFont(bold, 12)
    c.drawCentredString(calibre_x+42, tarja_y + 32, "CALIBRE:")
    c.setFont(bold, 24)
    c.drawCentredString(calibre_x+42, tarja_y, f"{datos['calibre']}")
    #··············································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································
    section_width = ((boleta_left-60 )) - line_v2_x
    c.drawString(line_v2_x + (section_width - text_tunel_width) / 2, y,"")
    
    # --- Líneas divisorias para la sección inferior ---
    # Línea horizontal superior
    line_bottom_y = boleta_bottom + 65  # Ajusta según la altura de los títulos
    c.setLineWidth(1)
    #c.line(table_left-5, line_bottom_y, boleta_left + boleta_width, line_bottom_y)
    c.line(table_left-5, line_bottom_y+10, boleta_width-130, line_bottom_y+10)
    # Línea vertical entre columnas
    section_width = (boleta_left + boleta_width) - table_left
    col_div_x = table_left + section_width // 4
    c.line(col_div_x+10, boleta_bottom, col_div_x+10, line_bottom_y+10)


def draw_single_format_cajas(c, datos, qr_img, logo_path, y_offset):
    """
    Dibuja un único formato de boleta en el canvas en una posición vertical (y_offset) específica.
    """
    width, page_height = A4
    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    # Área de la boleta: se ajusta para caber en la mitad de la página con mejores márgenes
    total_block_height = page_height / 2
    
    # Reducimos la altura del recuadro principal y dejamos espacio abajo para la tarja
    boleta_height = 350
    boleta_width = width - 50  # Margen horizontal de 25 en cada lado
    boleta_left = 25
    
    # Centramos el recuadro en el bloque vertical que le corresponde
    padding_top = 40
    boleta_bottom = y_offset + total_block_height - boleta_height - padding_top
    
    # Cuadro exterior de la boleta (en negro)
    c.setStrokeColorRGB(0, 0, 0) # Color negro para el borde
    c.setLineWidth(2)
    c.rect(boleta_left, boleta_bottom, boleta_width, boleta_height)

    # --- Líneas de división ---
    c.setLineWidth(1)
    # Línea vertical para separar QR del resto
    line_v_x = boleta_left + 165 
    c.line(line_v_x, boleta_bottom, line_v_x, boleta_bottom + boleta_height)
    # Línea horizontal para separar cabecera de datos
    line_h_y = boleta_bottom + boleta_height - 70
    c.line(line_v_x, line_h_y, boleta_left + boleta_width, line_h_y)

    #c.setStrokeColorRGB(0, 0, 0) # Restaurar color negro para otras líneas

    # --- Logo ---
    logo_w, logo_h = 50, 50
    # Posición del recuadro del logo
    logo_box_x = line_v_x + 10
    logo_box_y = line_h_y + 10
    # Dibujar el recuadro para el logo
    c.setLineWidth(1)
    c.rect(logo_box_x, logo_box_y, logo_w, logo_h)
    
    if os.path.exists(logo_path):
        # Centrar el logo dentro de su recuadro
        c.drawImage(logo_path, logo_box_x, logo_box_y, width=logo_w, height=logo_h, mask='auto')
    else:
        # Si no hay logo, escribir "LOGO" como placeholder
        c.setFont("Helvetica", 12)
        c.drawCentredString(logo_box_x + logo_w / 2, logo_box_y + (logo_h - 12) / 2, "LOGO")

    # --- QR ---
    qr_size = 162 # Tamaño ajustado
    qr_x = boleta_left + 1
    qr_y = boleta_bottom + boleta_height - qr_size - 95
    qr_buffer = io.BytesIO()
    if hasattr(qr_img, 'get_image'):
        qr_img = qr_img.get_image()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)

    c.setFont("Helvetica",11)
    text_qr = datos['key_qr']
    text_width = c.stringWidth(text_qr, "Helvetica", 11)
    c.drawString(qr_x + (qr_size - text_width) / 2, qr_y - 10, text_qr)

    # --- Cabecera ---
    header_x_center = boleta_left + boleta_width / 2 + 60
    header_y_top = boleta_bottom + boleta_height - 15
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(header_x_center, header_y_top- 10, "FORMATO")
    c.setFont("Helvetica", 9)
    c.drawCentredString(header_x_center, header_y_top - 30, "BOLETA DE RECEPCION DE MATERIA PRIMA")
    
    # Código, versión, fecha
    info_x = boleta_left + boleta_width - 95
    info_y = header_y_top +5
    c.setFont("Helvetica", 7)
    c.drawString(info_x, info_y, "Código: APP - CC-FPP 002")
    c.drawString(info_x, info_y - 9, "Versión : 01-2")
    c.drawString(info_x, info_y - 18, f"Fecha : {fecha_actual}")

    # --- Tabla de datos ---
    table_left = boleta_left + 170 # Más espacio para el QR
    table_top = boleta_bottom + boleta_height -100
    col1_x = table_left
    col2_x = table_left + 230
    row_height = 23
    font_size = 8
    font_size_big=11
    bold = "Helvetica-Bold"
    normal = "Helvetica"
    
    # Línea vertical entre columnas de datos
    line_v2_x = col2_x - 10
    c.line(line_v2_x, boleta_bottom, line_v2_x, line_h_y)
    
    # --- Columna 1 ---
    y = table_top
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "CULTIVO:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['cultivo']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "TIPO DE PRODUCTO:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['tipo_producto']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "EMPRESA:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['empresa']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "FUNDO:")
    c.setFont(normal, 9)
    c.drawString(col1_x + 90, y, f"{datos['fundo']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "VARIEDAD:")
    c.setFont(normal, 9)
    c.drawString(col1_x + 90, y, f"{datos['variedad']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "Nº PALLET:")
    c.setFont(bold, 9)
    c.drawString(col1_x + 90, y, f"{datos['num_pallet']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "GUIA:")
    c.setFont(normal, 9)
    c.drawString(col1_x + 90, y, f"{datos['guia']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "VIAJE:")
    c.setFont(normal, 17)
    c.drawString(col1_x + 90, y, f"{datos['viaje']}")

    # --- Columna 2 ---
    y = table_top
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "FECHA:")
    c.setFont(bold, 14)
    c.drawString(col2_x + 50, y, f"{datos['fecha']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. BRUTO:")
    c.setFont(normal, 12)
    c.drawString(col2_x + 70, y, f"{datos['peso_bruto']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "DETALLE:")
    c.setFont(normal, 12)
    c.drawString(col2_x + 70, y, f"{datos['detalle']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "Nº CAJAS:")
    c.setFont(normal, 12)
    c.drawString(col2_x + 70, y, f"{datos['num_cajas']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. CAMPO:")
    c.setFont(normal, 12)
    c.drawString(col2_x + 70, y, f"{datos['peso_campo']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. NETO:")
    c.setFont(bold, 13) # Resaltado
    c.drawString(col2_x + 70, y, f"{datos['peso_neto']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "T° ESTADO:")
    c.setFont(bold, 9) # Resaltado
    c.drawString(col2_x + 70, y, f"{datos['temperatura_estado']}")#
    # --- Línea horizontal sobre TUNEL DE ENFRIAMIENTO ---
    line_h2_y = y - 20
    c.line(line_v2_x, line_h2_y, boleta_left + boleta_width, line_h2_y)

    y -= (row_height + 15) # Espacio extra para la nueva sección
    
    c.setFont(bold, 10)
    # Centrar el texto "TUNEL DE ENFRIAMIENTO" en el espacio disponible
    text_tunel = "TUNEL DE ENFRIAMIENTO:"
    text_tunel_width = c.stringWidth(text_tunel, bold, 10)
    # El ancho de la sección es (boleta_left + boleta_width) - line_v2_x
    section_width = (boleta_left + boleta_width) - line_v2_x
    c.drawString(line_v2_x + (section_width - text_tunel_width) / 2, y, text_tunel)
    
    # --- N° TARJA Y CALIBRE (parte inferior, en columnas) ---
    tarja_y = boleta_bottom + 25  # Más cerca del borde inferior
    col_width = 40  # Ancho de cada columna
    # Columna izquierda: Nº TARJA
    c.setFont(bold, 12)
    c.drawCentredString(table_left + col_width+20 // 2, tarja_y + 32, "Nº TARJA:")
    c.setFont(bold, 28)
    c.drawCentredString(table_left + col_width+20 // 2, tarja_y, f"{datos['num_tarja']}")

    # Columna derecha: CALIBRE      
    calibre_x = table_left + col_width + col_width // 2 + 60  # Ajusta el +60 según el ancho de tu boleta
    c.setFont(bold, 12)
    c.drawCentredString(calibre_x+42, tarja_y + 32, "CALIBRE:")
    c.setFont(bold, 24)
    c.drawCentredString(calibre_x+42, tarja_y, f"{datos['calibre']}")
    #··············································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································································
    section_width = ((boleta_left-60 )) - line_v2_x
    c.drawString(line_v2_x + (section_width - text_tunel_width) / 2, y,"")
    
    # --- Líneas divisorias para la sección inferior ---
    # Línea horizontal superior
    line_bottom_y = boleta_bottom + 65  # Ajusta según la altura de los títulos
    c.setLineWidth(1)
    #c.line(table_left-5, line_bottom_y, boleta_left + boleta_width, line_bottom_y)
    c.line(table_left-5, line_bottom_y+10, boleta_width-130, line_bottom_y+10)
    # Línea vertical entre columnas
    section_width = (boleta_left + boleta_width) - table_left
    col_div_x = table_left + section_width // 4
    c.line(col_div_x+10, boleta_bottom, col_div_x+10, line_bottom_y+10)




















# --- Nueva función principal para crear el PDF ---
def crear_pdf(lista_datos, logo_path):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    for i, datos in enumerate(lista_datos):
        # Generar QR para este registro
        qr_img = generar_qr(datos['key_qr'])

        # Determinar qué formato usar según el valor de detalle
        if datos.get('detalle', '').upper() == 'PT':
            formato_funcion = draw_single_format_cajas
        else:
            formato_funcion = draw_single_format

        if i % 2 == 0: # Elemento par (0, 2, 4...), va en la parte superior
            if i > 0: # Si no es el primero, añade nueva página
                c.showPage()
            y_offset = height / 2
            formato_funcion(c, datos, qr_img, logo_path, y_offset)
        else: # Elemento impar (1, 3, 5...), va en la parte inferior
            y_offset = 0
            formato_funcion(c, datos, qr_img, logo_path, y_offset)

    c.save()
    buffer.seek(0)
    return buffer


def generar_qr(data, box_size=10):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size, # Tamaño configurable
        border=2
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def crear_pdf_packing_list(df, logo_path="./src/assets/logo.jpg", header_data=None):
    """
    Crea un PDF del packing list en formato A4 horizontal
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Frame, PageTemplate
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import Image
    import io
    
    # Crear buffer para el PDF
    buffer = io.BytesIO()
    
    # Configurar documento A4 horizontal (landscape)
    from reportlab.lib.pagesizes import A4, landscape
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    # Función para agregar el logo en cada página
    def add_logo(canvas, doc):
        if os.path.exists(logo_path):
            # Obtener las dimensiones de la página
            page_width, page_height = landscape(A4)
            
            # Posicionar el logo en la esquina superior derecha
            logo_width = 1.2*inch
            logo_height = 1.2*inch
            logo_x = page_width - logo_width +20 # 30 puntos de margen derecho
            logo_y = page_height - logo_height +10 # 30 puntos de margen superior
            
            # Dibujar el logo
            canvas.drawImage(logo_path, logo_x, logo_y, width=50, height=70)
    
    # Crear el template de página con el logo
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='logo_template', frames=[frame], onPage=add_logo)
    doc.addPageTemplates([template])
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    # Elementos del documento
    elements = []
    
    # Título
    title = Paragraph("PACKING LIST", title_style)
    elements.append(title)
    elements.append(Spacer(0, 0))  # Reducir espacio entre título y tabla
    
    # Información del header - tabla más pequeña y centrada
    if header_data is None:
        # Datos por defecto si no se proporcionan
        header_data = [
            ["N° DESPACHO:", "FCL " + str(df["Nº FCL"].iloc[0]) if len(df) > 0 else "", "PUERTO DE CARGA:", "", "ETD:", ""],
            ["FECHA DE DESPACHO:", "", "DESTINO:", "", "ETA:", ""],
            ["EXPORTADOR:", "", "N° DE CONTENEDOR:", "", "PESO NETO:", ""],
            ["CLIENTE:", "", "BOOKING:", "", "PESO BRUTO:", ""],
            ["CONSIGNATARIO:", "", "NAVE:", "", "", ""]
        ]
    
    # Calcular ancho total disponible para centrar la tabla
    total_width = landscape(A4)[0]-180  # Ancho total menos márgenes
    header_table_width = 9*inch  # Ancho más pequeño para la tabla header
    header_margin = (total_width - header_table_width) / 2  # Margen para centrar
    
    header_table = Table(header_data, colWidths=[1.3*inch, 1.8*inch, 1.3*inch, 1.8*inch, 1.3*inch, 1.3*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('BACKGROUND', (4, 0), (4, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTNAME', (4, 0), (4, -1), 'Helvetica-Bold'),
        ('LEFTPADDING', (0, 0), (-1, -1), header_margin),  # Centrar la tabla
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 10))  # Reducir espacio después de la tabla header
    
    # Preparar datos de la tabla principal
    # Usar nombres originales del dataframe
    table_columns = [
        "Nº FCL", "Nº  PALLET", "FECHA DE PRODUCCIÓN", "PRODUCTO", "VARIEDAD", 
        "NOMBRE DEL FUNDO", "LDP", "NÚMERO DE GLOBAL GAP", "CODIGO DE PRODUCTOR",
        "DESCRIPCIÓN", "PESO DE CAJA", " Nº CAJAS", "TOTAL KILOS NETO (KG)"
    ]
    
    # Nombres de columnas para mostrar en el PDF (con saltos de línea)
    display_columns = [
        "Nº FCL", "Nº\nPALLET", "FECHA DE\nPRODUCCIÓN", "PRODUCTO", "VARIEDAD", 
        "NOMBRE DEL\nFUNDO", "LDP", "NÚMERO DE\nGLOBAL GAP", "CODIGO DE\nPRODUCTOR",
        "DESCRIPCIÓN", "PESO DE\nCAJA", "Nº\nCAJAS", "TOTAL KILOS\nNETO (KG)"
    ]
    
    # Crear tabla con los datos
    table_data = [display_columns]  # Header con nombres formateados para PDF
    
    # Calcular totales
    total_peso_caja = df[" Nº CAJAS"].sum()
    total_kilos = df["TOTAL KILOS NETO (KG)"].sum()
    
    # Agregar filas de datos
    for _, row in df.iterrows():
        table_row = []
        for col in table_columns:  # Usar nombres originales para acceder a los datos
            value = row[col]
            # Formatear fechas
            if col == "FECHA DE PRODUCCIÓN" and pd.notna(value):
                if hasattr(value, 'strftime'):
                    value = value.strftime("%d/%m/%Y")
                else:
                    value = str(value)
            # Formatear números grandes
            elif col == "NÚMERO DE GLOBAL GAP" and pd.notna(value):
                value = f"{value:.0f}" if isinstance(value, (int, float)) else str(value)
            # Formatear números decimales
            elif col in [" Nº CAJAS", "TOTAL KILOS NETO (KG)"] and pd.notna(value):
                value = f"{value:.1f}" if isinstance(value, (int, float)) else str(value)
            else:
                value = str(value) if pd.notna(value) else ""
            table_row.append(value)
        table_data.append(table_row)
    
    # Agregar fila de totales
    total_row = ["Total general", "", "", "", "", "", "", "", "", "", "", f"{total_peso_caja:.0f}", f"{total_kilos:.1f}"]
    table_data.append(total_row)
    
    # Crear tabla principal - optimizado para máximo uso del espacio horizontal con headers multilínea
    # Ajustado para dar más espacio a FCL, CODIGO DE PRODUCTOR y DESCRIPCIÓN
    col_widths = [1.2*inch, 0.7*inch, 0.7*inch, 0.6*inch, 0.7*inch, 0.9*inch, 0.7*inch, 0.9*inch, 1.2*inch, 1.8*inch, 0.6*inch, 0.6*inch, 0.8*inch]
    main_table = Table(table_data, colWidths=col_widths)
    
    # Estilo para la tabla principal con headers multilínea
    main_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -2), 'LEFT'),  # Datos alineados a la izquierda (excluyendo totales)
        # Alineación específica para columnas numéricas (últimas 3 columnas)
        ('ALIGN', (10, 1), (12, -2), 'RIGHT'),  # PESO DE CAJA, Nº CAJAS, TOTAL KILOS alineados a la derecha
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header en negrita
        ('FONTSIZE', (0, 0), (-1, -1), 5),
        # Tamaño de fuente mayor para columnas numéricas (últimas 3 columnas)
        ('FONTSIZE', (10, 1), (12, -2), 6),  # PESO DE CAJA, Nº CAJAS, TOTAL KILOS
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),  # Excluyendo fila de totales
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, 0), True),  # Permitir salto de línea en headers
        ('LEADING', (0, 0), (-1, 0), 8),  # Espaciado entre líneas en headers
        # Estilo especial para la fila de totales
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Totales en negrita
        ('FONTSIZE', (0, -1), (-1, -1), 6),  # Tamaño de fuente ligeramente mayor para totales
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),  # Fondo azul claro para totales
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),  # Totales centrados
    ]))
    
    elements.append(main_table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def crear_pdf_qr_tunel(CAMARA):
    """
    Crea un PDF con los códigos QR del túnel de enfriamiento organizados en grilla
    Orden: por niveles (S, M, I) con columnas en filas de 2
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Configuración de la grilla
    niveles = ['S', 'M', 'I']
    columnas = list(range(1, 16))  # 1 a 15
    
    # Dimensiones más grandes para recuadros QR
    qr_box_width = 260
    qr_box_height = 280
    qr_size = 210  # QR aún más grande
    margin_left = 10
    margin_top = 10
    spacing_x = 270 # Espacio horizontal entre recuadros
    spacing_y = 250 # Espacio vertical entre recuadros
    
    # Configuración de grilla: 2 columnas, 3 filas (una por nivel)
    
    # Título en la primera página
    #c.setFont("Helvetica-Bold", 18)
    #c.drawCentredString(width/2, height - 30, "TÚNEL QR ENFRIAMIENTO - CÁMARA 2")
    
    # Procesar por pares de columnas (cada página tendrá 2 columnas × 3 niveles = 6 QRs)
    for i in range(0, len(columnas), 2):  # Procesar columnas de 2 en 2
        col_pair = columnas[i:i+2]  # Tomar par de columnas (ej: [1,2], [3,4], etc.)
        
        # Si no es la primera página, crear nueva página
        if i > 0:
            c.showPage()
            #c.setFont("Helvetica-Bold", 18)
            #c.drawCentredString(width/2, height - 30, "TÚNEL QR ENFRIAMIENTO - CÁMARA 2")
        
        # Para cada nivel (S, M, I) crear una fila
        for nivel_idx, nivel in enumerate(niveles):
            # Mapear nivel a número
            if nivel == "S":
                nivel_num = "3"
            elif nivel == "M":
                nivel_num = "2"
            elif nivel == "I":
                nivel_num = "1"
            
            # Para cada columna en el par actual (máximo 2 columnas)
            for col_idx, col_num in enumerate(col_pair):
                # Calcular posición en la grilla de la página actual
                row = nivel_idx  # Fila basada en el nivel (0=S, 1=M, 2=I)
                col = col_idx    # Columna (0 o 1)
                
                # Calcular posición del recuadro
                x_pos = margin_left + (col * spacing_x)
                y_pos = height - margin_top - 20 - (row * spacing_y)
                
                # Dibujar recuadro con bordes
                #c.setStrokeColorRGB(0, 0, 0)
                #c.setLineWidth(3)
                #c.rect(x_pos, y_pos - qr_box_height, qr_box_width, qr_box_height, stroke=1, fill=0)
                
                # Datos del QR
                code = f"{CAMARA}{col_num}{nivel}"
                text = f"C{CAMARA}F{col_num}P(1-6){nivel}"
                text_nivel = f"NIVEL {nivel_num}"
                
                # Generar y dibujar QR más grande
                qr_img = generar_qr(code, box_size=15)  # QR con mayor resolución
                qr_buffer = io.BytesIO()
                qr_img.save(qr_buffer, format="PNG")
                qr_buffer.seek(0)
                
                # Centrar QR en el recuadro
                qr_x = x_pos + (qr_box_width - qr_size) / 2
                qr_y = y_pos - 50 - qr_size
                c.drawImage(ImageReader(qr_buffer), qr_x+30, qr_y+40, width=qr_size, height=qr_size)
                
                # Dibujar texto más grande debajo del QR
                c.setFont("Helvetica-Bold", 16)
                text_width = c.stringWidth(text, "Helvetica-Bold", 5)
                text_x = x_pos + (qr_box_width - text_width) / 2
                c.drawString(text_x, qr_y + 35, text)
                
                # Dibujar texto del nivel más grande
                c.setFont("Helvetica-Bold", 16)
                text_nivel_width = c.stringWidth(text_nivel, "Helvetica-Bold", -5)
                text_nivel_x = x_pos + (qr_box_width - text_nivel_width) / 2
                c.drawString(text_nivel_x, qr_y + 15, text_nivel)
    
    c.save()
    buffer.seek(0)
    return buffer


