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
    boleta_height = 300
    boleta_width = width - 50  # Margen horizontal de 25 en cada lado
    boleta_left = 25
    
    # Centramos el recuadro en el bloque vertical que le corresponde
    padding_top = 40
    boleta_bottom = y_offset + total_block_height - boleta_height - padding_top
    
    # Cuadro exterior de la boleta (en negro)
    c.setStrokeColorRGB(0, 0, 0) # Color negro para el borde
    c.setLineWidth(2)
    c.rect(boleta_left, boleta_bottom, boleta_width, boleta_height)
    #c.setStrokeColorRGB(0, 0, 0) # Restaurar color negro para otras líneas

    # --- Logo ---
    logo_w, logo_h = 35, 40
    logo_x = boleta_left +10
    logo_y = boleta_bottom + boleta_height - logo_h - 10
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 190, logo_y, width=logo_w, height=logo_h, mask='auto')

    # --- QR ---
    qr_size = 150 # Tamaño ajustado
    qr_x = logo_x
    qr_y = logo_y - qr_size - 0
    qr_buffer = io.BytesIO()
    if hasattr(qr_img, 'get_image'):
        qr_img = qr_img.get_image()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)

    c.setFont("Helvetica", 8)
    text_qr = datos['key_qr']
    text_width = c.stringWidth(text_qr, "Helvetica", 8)
    c.drawString(qr_x + (qr_size - text_width) / 2, qr_y - 10, text_qr)

    # --- Cabecera ---
    header_x_center = boleta_left + boleta_width / 2 + 50
    header_y_top = boleta_bottom + boleta_height - 15
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(header_x_center, header_y_top, "FORMATO")
    c.setFont("Helvetica", 9)
    c.drawCentredString(header_x_center, header_y_top - 12, "BOLETA DE RECEPCION DE MATERIA PRIMA")
    
    # Código, versión, fecha
    info_x = boleta_left + boleta_width - 95
    info_y = header_y_top +5
    c.setFont("Helvetica", 7)
    c.drawString(info_x, info_y, "Código: APP - CC-FPP 002")
    c.drawString(info_x, info_y - 9, "Versión : 01")
    c.drawString(info_x, info_y - 18, f"Fecha : {fecha_actual}")

    # --- Tabla de datos ---
    table_left = boleta_left + 160 # Más espacio para el QR
    table_top = boleta_bottom + boleta_height -70
    col1_x = table_left
    col2_x = table_left + 210
    row_height = 21
    font_size = 8
    bold = "Helvetica-Bold"
    normal = "Helvetica"
    
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
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['fundo']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "VARIEDAD:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['variedad']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "Nº PALLET:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['num_pallet']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "GUIA:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['guia']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "VIAJE:")
    c.setFont(normal, font_size)
    c.drawString(col1_x + 90, y, f"{datos['viaje']}")

    # --- Columna 2 ---
    y = table_top
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "FECHA:")
    c.setFont(normal, font_size)
    c.drawString(col2_x + 90, y, f"{datos['fecha']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. BRUTO:")
    c.setFont(normal, font_size)
    c.drawString(col2_x + 90, y, f"{datos['peso_bruto']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "Nº JABAS:")
    c.setFont(normal, font_size)
    c.drawString(col2_x + 90, y, f"{datos['num_jabas']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "Nº JARRAS:")
    c.setFont(normal, font_size)
    c.drawString(col2_x + 90, y, f"{datos['num_jarras']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. CAMPO:")
    c.setFont(normal, font_size)
    c.drawString(col2_x + 90, y, f"{datos['peso_campo']}")

    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. NETO:")
    c.setFont(bold, font_size + 2) # Resaltado
    c.drawString(col2_x + 90, y, f"{datos['peso_neto']}")
    
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "TUNEL DE ENFRIAMIENTO:")
    c.setFont(normal, font_size)
    c.drawString(col2_x + 90, y, f"{datos['tunel_enfriamiento']}")

    # --- N° TARJA Y FIRMA  ---
    tarja_y = boleta_bottom + 30 # Posición debajo del recuadro
    
    c.setFont(bold, 12)
    c.drawString(table_left, tarja_y, "N° TARJA:")
    c.setFont(bold, 14)
    c.drawString(table_left + 90, tarja_y, f"{datos['num_tarja']}")
    
    # Firma
    firma_x = table_left + 210
    c.setDash(2, 2)
    c.line(firma_x, tarja_y, firma_x + 150, tarja_y)
    c.setDash()
    c.setFont(normal, 9)
    c.drawCentredString(firma_x + 75, tarja_y - 12, "ASISTENTE RECEPCION")

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