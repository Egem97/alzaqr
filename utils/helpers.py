import qrcode
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 # Cambiado a A4 normal
from reportlab.lib.utils import ImageReader
import os

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
    
    # --- Línea horizontal sobre TUNEL DE ENFRIAMIENTO ---
    line_h2_y = y - 10
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

        if i % 2 == 0: # Elemento par (0, 2, 4...), va en la parte superior
            if i > 0: # Si no es el primero, añade nueva página
                c.showPage()
            y_offset = height / 2
            draw_single_format(c, datos, qr_img, logo_path, y_offset)
        else: # Elemento impar (1, 3, 5...), va en la parte inferior
            y_offset = 0
            draw_single_format(c, datos, qr_img, logo_path, y_offset)

    c.save()
    buffer.seek(0)
    return buffer


def generar_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10, # Ajustado para el nuevo tamaño de QR
        border=2
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img