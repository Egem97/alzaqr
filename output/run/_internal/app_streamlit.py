import streamlit as st
from PIL import Image
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
import io
import os
import pandas as pd
from datetime import datetime
def generar_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=2
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# --- Generación de PDF ---
def crear_pdf(datos, qr_img, logo_path):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Área de la boleta: 780x400 px, esquina superior izquierda
    boleta_left = 20
    boleta_top = height - 20
    boleta_width = 810
    boleta_height = 400
    boleta_bottom = boleta_top - boleta_height

    # Cuadro exterior de la boleta
    c.setLineWidth(2)
    c.rect(boleta_left, boleta_bottom, boleta_width, boleta_height)

    ##########################################
    logo_w, logo_h = 60, 60
    logo_x = boleta_left + 10
    logo_y = boleta_top - logo_h - 5
    if os.path.exists(logo_path):
        c.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h, mask='auto')


    # --- QR (aún más grande y centrado verticalmente) ---
    qr_size = 250
    qr_col_width = 180
    qr_col_height = boleta_height
    qr_x = boleta_left + (qr_col_width - qr_size) / 15
    qr_y = boleta_bottom + (qr_col_height - qr_size) / 2 + 10
    qr_buffer = io.BytesIO()
    if hasattr(qr_img, 'get_image'):
        qr_img = qr_img.get_image()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)
    # PDF QR botón (debajo del QR, centrado)
    btn_width = 55
    btn_height = 20
    btn_x = boleta_left + (qr_col_width - btn_width) / 2
    btn_y = qr_y - btn_height - 6
    c.setFillGray(0.2)
    c.rect(btn_x, btn_y, btn_width, btn_height, fill=1)
    c.setFillColorRGB(1,1,1)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(btn_x + 8, btn_y + 6, "PDF QR")
    c.setFillColorRGB(0,0,0)
    # Texto QR (debajo del botón, centrado)
    c.setFont("Helvetica", 8)
    text_qr = datos['key_qr']
    text_width = c.stringWidth(text_qr, "Helvetica", 8)
    c.drawString(boleta_left + (qr_col_width - text_width) / 2, btn_y - 12, text_qr)

    # --- Cabecera ---
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(boleta_left + boleta_width/2, boleta_top - 15, "FORMATO")
    c.setFont("Helvetica", 11)
    c.drawCentredString(boleta_left + boleta_width/2, boleta_top - 30, "BOLETA DE RECEPCION DE MATERIA PRIMA")
    # Código, versión, fecha
    c.setFont("Helvetica", 8)
    var_high = 15
    c.drawString(boleta_left + boleta_width - 110, boleta_top - 25 +var_high, "Código: APP - CC-FPP 002")
    c.drawString(boleta_left + boleta_width - 110, boleta_top - 37+var_high, "Versión : 02")
    c.drawString(boleta_left + boleta_width - 110, boleta_top - 49+var_high, "Fecha : 16/06/2025")

    # --- Tabla de datos (2 columnas) ---
    table_left = boleta_left + qr_col_width
    table_top = boleta_top - 30
    table_width = boleta_width - qr_col_width
    col1_x = table_left + 80
    col2_x = table_left + table_width/2 + 85
    row_height = 30
    font_size = 11
    bold = "Helvetica-Bold"
    normal = "Helvetica"

    # Encabezados de fila
    c.setFont(normal, font_size)
    c.drawString(col1_x, table_top - row_height, f"CULTIVO    : {datos['cultivo']}")
    c.drawString(col2_x, table_top - row_height, f"FECHA    : {datos['fecha']}")
    c.drawString(col1_x, table_top - 2*row_height, f"TIPO DE PRODUCTO    : {datos['tipo_producto']}")
    c.drawString(col2_x, table_top - 2*row_height, "")

    # Datos principales (negrita y normal)
    y = table_top - 3*row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "EMPRESA")
    c.setFont(normal, font_size)
    c.drawString(col1_x+90, y, f"{datos['empresa']}")
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. BRUTO")
    c.setFont(normal, font_size)
    c.drawString(col2_x+90, y, f"{datos['peso_bruto']}")
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "FUNDO")
    c.setFont(normal, font_size)
    c.drawString(col1_x+90, y, f"{datos['fundo']}")
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "Nº JABAS")
    c.setFont(normal, font_size)
    c.drawString(col2_x+90, y, f"{datos['num_jabas']}")
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "VARIEDAD")
    c.setFont(normal, font_size)
    c.drawString(col1_x+90, y, f"{datos['variedad']}")
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "Nº JARRAS")
    c.setFont(normal, font_size)
    c.drawString(col2_x+90, y, f"{datos['num_jarras']}")
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "Nº PALLET")
    c.setFont(normal, font_size)
    c.drawString(col1_x+90, y, f"{datos['num_pallet']}")
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. CAMPO")
    c.setFont(normal, font_size)
    c.drawString(col2_x+90, y, f"{datos['peso_campo']}")
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "GUIA")
    c.setFont(normal, font_size)
    c.drawString(col1_x+90, y, f"{datos['guia']}")
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "P. NETO")
    c.setFont(bold, 16)
    c.drawString(col2_x+90, y, f"{datos['peso_neto']}")
    y -= row_height
    c.setFont(bold, font_size)
    c.drawString(col1_x, y, "VIAJE")
    c.setFont(normal, 16)
    c.drawString(col1_x+90, y, f"{datos['viaje']}")
    c.setFont(bold, font_size)
    c.drawString(col2_x, y, "TUNEL DE ENFRIAMIENTO")
    c.setFont(normal, font_size)
    c.drawString(col2_x+90, y, f"{datos['tunel_enfriamiento']}")

    # --- Fila N° TARJA (más abajo, en una fila separada) ---
    tarja_y = boleta_bottom + 30###################### MOD POSICION TARJA
    c.setFont(bold, 16)
    c.drawString(col1_x, tarja_y, f"N° TARJA")
    c.setFont(bold, 18)
    c.drawString(col1_x+120, tarja_y, f"{datos['num_tarja']}")
    # Espacio a la derecha

    # --- Fila firma y botón ---
    firma_y = boleta_bottom + 30
    c.setDash(2, 2)
    c.line(col2_x, firma_y+20, boleta_left + boleta_width - 120, firma_y+20)
    c.setDash()
    c.setFont(normal, 12)
    c.drawString(col2_x, firma_y, "ASISTENTE RECEPCION")
    # Botón Nuevo Registro
    c.setFillGray(0.2)
    #c.rect(boleta_left + boleta_width - 110, firma_y, 90, 35, fill=1)
    #c.setFillColorRGB(1,1,1)
    #c.setFont(bold, 12)
    #c.drawString(boleta_left + boleta_width - 100, firma_y+20, "Nuevo Registro")
    #c.setFillColorRGB(0,0,0)

    c.save()
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Boleta de Recepción de Materia Prima", layout="centered")
st.title("Boleta de Recepción de Materia Prima")
df =pd.read_excel("BD.xlsx")
find_cod = st.text_input("Busque el codigo")

if find_cod:
    df = df[df["KEY"]==find_cod]
    print(df.columns)
    st.dataframe(df)
    #data_for_qr = {}
    key_qr = df["KEY"].values[0]
    cultivo= "ARANDANO"       
    tipo_producto = df["TIPO PRODUCTO"].values[0]
    empresa= df["EMPRESA"].values[0]
    fundo= df["FUNDO"].values[0]
    variedad = df["VARIEDAD"].values[0]
    num_pallet = df["N° PALLET"].values[0]
    guia = df["GUIA"].values[0]
    viaje = df["N° VIAJE"].values[0]
    num_tarja = df["N° TARJETA PALLET"].values[0]
    fecha= df["FECHARECEPCION"].values[0]
    peso_bruto= df["KILOS BRUTOS"].values[0]
    num_jabas = df["N° JABAS"].values[0]
    num_jarras = df["N° JARRAS"].values[0]
    peso_campo = df["PESO NETO CAMPO"].values[0]
    peso_neto = df["KILOS NETOS"].values[0]
    tunel_enfriamiento = ""
    qr_img = generar_qr(key_qr)
    datos = {
        'key_qr': key_qr,
        'cultivo': cultivo,
        'tipo_producto': tipo_producto,
        'empresa': empresa,
        'fundo': fundo,
        'variedad': variedad,
        'num_pallet': num_pallet,
        'guia': guia,
        'viaje': viaje,
        'num_tarja': num_tarja,
        'fecha': fecha,
        'peso_bruto': peso_bruto,
        'num_jabas': num_jabas,
        'num_jarras': num_jarras,
        'peso_campo': peso_campo,
        'peso_neto': peso_neto,
        'tunel_enfriamiento': tunel_enfriamiento
    }
    pdf_buffer = crear_pdf(datos, qr_img, "LOGO PACKING.png")
    st.success("PDF generado correctamente.")
    st.download_button(
            label="Descargar PDF",
            data=pdf_buffer,
            file_name=f"boleta_{num_tarja}.pdf",
            mime="application/pdf"
    )
    #st.image(qr_img, caption="QR generado", width=150)
    
    













