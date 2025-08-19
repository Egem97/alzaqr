import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime
from styles import styles
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode ,JsCode
from io import StringIO, BytesIO
from utils.helpers import crear_pdf, generar_qr, crear_pdf_qr_tunel, crear_pdf_packing_list
from utils.components import aggrid_builder,aggrid_builder_prod,aggrid_editing_prod
from utils.get_api import listar_archivos_en_carpeta_compartida, get_download_url_by_name
from utils.get_token import get_access_token

def packing_list():
    styles(2)
    
    
    col_head1,col_head2,col_head3= st.columns([4,6,2])
    with col_head1:
        st.title("📄Packing List")
    

    
    @st.cache_data(show_spinner="Cargando datos...",persist="disk")
    def get_data():
        access_token = get_access_token()
        DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!Mx2p-6knhUeohEjU-L-a3w-JZv1JawxAkEY9khgxn7hWjhq65fg_To08YnAwHSc0", "01L5M4SATOWDS7G66DCNCYJLOJVNY7SPTV")
        data_ = get_download_url_by_name(DATAS, "REGISTRO DE PHL - PRODUCTO TERMINADO -154.xlsm")
        
        return pd.read_excel(data_, sheet_name="TD-DATOS PT"),pd.read_excel(data_, sheet_name="BD1",skiprows=6),pd.read_excel(data_, sheet_name="GMH-ABG-CYN")#GMH-ABG-CYN
    
    df,producto_peso_df,df_gmh = get_data()
    df_gmh = df_gmh[df_gmh["F. PRODUCCION"].notna()]
    df_gmh["DESCRIPCION DEL PRODUCTO"] = df_gmh["DESCRIPCION DEL PRODUCTO"].str.strip()


    st.dataframe(df_gmh)
    producto_peso_df = producto_peso_df[['DESCRIPCION DE PRODUCTO', 'PESO caja']]
    producto_peso_df = producto_peso_df[producto_peso_df["DESCRIPCION DE PRODUCTO"].notna()]
    producto_peso_df["DESCRIPCION DE PRODUCTO"] = producto_peso_df["DESCRIPCION DE PRODUCTO"].str.strip()
    producto_peso_df["PESO caja"] = producto_peso_df["PESO caja"].fillna(0)
    #producto_peso_df["SOBRE PESO"] = producto_peso_df["SOBRE PESO"].fillna(0)
    producto_peso_df["PESO caja"] = producto_peso_df["PESO caja"].astype(float) 
    #producto_peso_df["SOBRE PESO"] = producto_peso_df["SOBRE PESO"].astype(float)
    producto_peso_df = producto_peso_df.rename(columns={"DESCRIPCION DE PRODUCTO":"DESCRIPCION DEL PRODUCTO"})
    
    producto_peso_df = producto_peso_df.drop_duplicates()
   
    df["DESCRIPCION DEL PRODUCTO"] = df["DESCRIPCION DEL PRODUCTO"].fillna("NO ESPECIFICADO")
    
 
    df["DESCRIPCION DEL PRODUCTO"] = df["DESCRIPCION DEL PRODUCTO"].str.strip()
    df = df[df["F. PRODUCCION"].notna()]
    df["DESCRIPCION DEL PRODUCTO"] = df["DESCRIPCION DEL PRODUCTO"].replace(
        {
            "125 GRS C/E SAN LUCAR +22MM-M":"125 GRS C/E SAN LUCAR+22MM-M",
            "125 GRS C/E SAN LUCAR +24MM-M":"125 GRS C/E SAN LUCAR+24MM-M",
            "125 GRS C/E SAN LUCAR +20MM-M":"125 GRS C/E SAN LUCAR+20MM-M",
        }
    )
    df["CONTENERDOR"] = df["CONTENERDOR"].fillna("NO ESPECIFICADO")
    df["CONTENERDOR"] = df["CONTENERDOR"].str.strip()
    df["Nº DE PALLET"] = df["Nº DE PALLET"].fillna("NO ESPECIFICADO")
    df["Nº DE PALLET"] = df["Nº DE PALLET"].str.strip()
    # Convert F. PRODUCCION to datetime and format as date only
    #df["F. PRODUCCION"] = pd.to_datetime(df['F. PRODUCCION'], errors="coerce").dt.date
    #df["F. COSECHA"] = pd.to_datetime(df['F. COSECHA'], errors="coerce").dt.date
    
    df["PRODUCTO"] = "ARANDANO"
    df["VARIEDAD"] = df["VARIEDAD"].fillna("NO ESPECIFICADO")
    df["VARIEDAD"] = df["VARIEDAD"].str.strip()
    df["FUNDO"] = df["FUNDO"].fillna("NO ESPECIFICADO")
    df["FUNDO"] = df["FUNDO"].str.strip()
    df["LDP"] = df["LDP"].fillna("009-00000-00000")
    df["LDP"] = df["LDP"].str.strip()
    df["GGN"] = df["GGN"].fillna(0)
    
    df["CODIGO DE FUNDO"] = df["CODIGO DE FUNDO"].fillna(0)
    #df["KG EXPORTABLES"] = df["KG EXPORTABLES"].fillna(0)
    df["KG EMPACADOS"] = df["KG EMPACADOS"].fillna(0)
   
    #st.write(df.shape)
    df = pd.merge(df,producto_peso_df,on="DESCRIPCION DEL PRODUCTO",how="left")
    df["PESO caja"] = df["PESO caja"].fillna(0)

    #st.write(df.shape)
    df["TOTAL KILOS NETO (KG)"] = df["Nº CAJAS"] * df["PESO caja"]
    #st.dataframe(df)
    dff = df.groupby(["CONTENERDOR","Nº DE PALLET","F. PRODUCCION","PRODUCTO","VARIEDAD","FUNDO","LDP","GGN","CODIGO DE FUNDO","DESCRIPCION DEL PRODUCTO","PESO caja"])[["Nº CAJAS","TOTAL KILOS NETO (KG)"]].sum().reset_index()
    dff.columns = [
        "Nº FCL",	"Nº  PALLET",	"FECHA DE PRODUCCIÓN",	"PRODUCTO",	"VARIEDAD",	"NOMBRE DEL FUNDO",	"LDP",	"NÚMERO DE GLOBAL GAP",
        "CODIGO DE PRODUCTOR",	"DESCRIPCIÓN",	"PESO DE CAJA",	" Nº CAJAS",	"TOTAL KILOS NETO (KG)"
    ]
    with col_head2:
        input_container = st.multiselect("Selecciona contenedor",dff["Nº FCL"].unique(),placeholder="Selecciona contenedor")
        if len(input_container) > 0:
            dff = dff[dff["Nº FCL"].isin(input_container)]
    with col_head3:
        if st.button("Actualizar Datos"): 
            st.cache_data.clear()
            st.rerun()
    dff = dff.sort_values(by="FECHA DE PRODUCCIÓN",ascending=True)
    
    gb = GridOptionsBuilder.from_dataframe(dff)
    #gb.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True)
    
    gb.configure_column("Nº FCL", width=300,pinned=True)
    gb.configure_column("Nº  PALLET", width=300,pinned=True)
    gb.configure_column("FECHA DE PRODUCCIÓN", width=200, type=["dateColumnFilter", "customDateTimeFormat"], custom_format_string="yyyy/MM/dd")
    gb.configure_column("LDP", width=300)
    grid_options = gb.build()

    grid_response = AgGrid(dff, # Dataframe a mostrar
        gridOptions=grid_options,
        #enable_enterprise_modules=False,
        update_mode=GridUpdateMode.SELECTION_CHANGED , 
        fit_columns_on_grid_load=True,
        #height=550
    )
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Crear una copia del dataframe para agregar la fila de totales
        dff_with_totals = dff.copy()
        
        # Calcular totales
        total_cajas = dff[" Nº CAJAS"].sum()
        total_kilos = dff["TOTAL KILOS NETO (KG)"].sum()
        
        # Crear fila de totales
        total_row = pd.DataFrame([{
            "Nº FCL": "TOTAL GENERAL",
            "Nº  PALLET": "",
            "FECHA DE PRODUCCIÓN": "",
            "PRODUCTO": "",
            "VARIEDAD": "",
            "NOMBRE DEL FUNDO": "",
            "LDP": "",
            "NÚMERO DE GLOBAL GAP": "",
            "CODIGO DE PRODUCTOR": "",
            "DESCRIPCIÓN": "",
            "PESO DE CAJA": "",
            " Nº CAJAS": total_cajas,
            "TOTAL KILOS NETO (KG)": total_kilos
        }])
        
        # Concatenar el dataframe original con la fila de totales
        dff_with_totals = pd.concat([dff_with_totals, total_row], ignore_index=True)
        
        dff_with_totals.to_excel(writer, sheet_name='PACKING LIST', index=False)
        workbook = writer.book
        worksheet1 = writer.sheets['PACKING LIST']
        
        # Formato corporativo para headers
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'align': 'center',
            'fg_color': '#1f4e79',  # Azul corporativo
            'font_color': 'white',
            'border': 1,
            'font_size': 10
        })
        
        # Formato para la fila de totales
        total_format = workbook.add_format({
            'bold': True,
            'fg_color': '#d4edda',  # Verde claro para totales
            'border': 1,
            'font_size': 10,
            'align': 'center'
        })
        
        # Formato para datos normales
        data_format = workbook.add_format({
            'border': 1,
            'font_size': 9,
            'valign': 'top'
        })
        
        # Agregar título corporativo
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'fg_color': '#1f4e79',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Escribir título en la primera fila
        worksheet1.merge_range(0, 0, 0, len(dff_with_totals.columns) - 1, 'PACKING LIST', title_format)
        
        # Ajustar altura de la fila del título
        worksheet1.set_row(0, 30)
        
        # Formato de fecha para la columna de fecha de producción
        date_format = workbook.add_format({
            'border': 1,
            'font_size': 9,
            'valign': 'top',
            'num_format': 'dd/mm/yyyy'
        })
        
        # Aplicar formatos
        for worksheet, df in zip([worksheet1], [dff_with_totals]):
            # Aplicar formato de header a la segunda fila (después del título)
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(1, col_num, value, header_format)
            
            # Aplicar formato de datos a las filas de datos
            for row_num in range(len(df) - 1):  # Excluir fila de totales
                for col_num, value in enumerate(df.iloc[row_num]):
                    col_name = df.columns[col_num]
                    
                    # Aplicar formato de fecha específico para la columna de fecha de producción
                    if col_name == "FECHA DE PRODUCCIÓN" and pd.notna(value):
                        if hasattr(value, 'strftime'):
                            # Si es un objeto date, convertirlo a datetime para Excel
                            from datetime import datetime
                            if hasattr(value, 'year'):
                                excel_date = datetime.combine(value, datetime.min.time())
                                worksheet.write_datetime(row_num + 2, col_num, excel_date, date_format)
                            else:
                                worksheet.write(row_num + 2, col_num, value, data_format)
                        else:
                            worksheet.write(row_num + 2, col_num, value, data_format)
                    else:
                        worksheet.write(row_num + 2, col_num, value, data_format)
            
            # Aplicar formato de totales a la última fila
            last_row = len(df) - 1
            for col_num, value in enumerate(df.iloc[last_row]):
                worksheet.write(last_row + 2, col_num, value, total_format)
            
            # Ajustar ancho de columnas con anchos específicos
            column_widths = {
                "Nº FCL": 25,  # Más espacio para FCL (texto largo)
                "Nº  PALLET": 15,  # Reducir espacio
                "FECHA DE PRODUCCIÓN": 12,  # Reducir espacio
                "PRODUCTO": 10,  # Reducir espacio
                "VARIEDAD": 12,  # Reducir espacio
                "NOMBRE DEL FUNDO": 15,  # Reducir espacio
                "LDP": 15,  # Reducir espacio
                "NÚMERO DE GLOBAL GAP": 18,  # Reducir espacio
                "CODIGO DE PRODUCTOR": 12,  # Reducir espacio
                "DESCRIPCIÓN": 35,  # Mucho más espacio para descripción (texto muy largo)
                "PESO DE CAJA": 10,  # Reducir espacio
                " Nº CAJAS": 10,  # Reducir espacio
                "TOTAL KILOS NETO (KG)": 15  # Reducir espacio
            }
            
            for i, col in enumerate(df.columns):
                if col in column_widths:
                    worksheet.set_column(i, i, column_widths[col])
                else:
                    # Para columnas no especificadas, usar cálculo automático
                    max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                    worksheet.set_column(i, i, max_len)
        
    processed_data = output.getvalue()
    
    # Inicializar session state para los datos del encabezado
    if 'header_data' not in st.session_state:
        st.session_state.header_data = {
            'n_despacho': "",
            'fecha_despacho': "",
            'exportador': "",
            'cliente': "",
            'consignatario': "",
            'puerto_carga': "",
            'destino': "",
            'n_contenedor': "",
            'booking': "",
            'nave': "",
            'etd': "",
            'eta': "",
            'peso_neto': "0.0",  # Inicializar como string numérico
            'peso_bruto': "0.0"  # Inicializar como string numérico
        }
    
    # Actualizar datos del encabezado basado en la selección actual
    if len(dff) > 0:
        # Obtener el FCL actual seleccionado
        current_fcl = dff['Nº FCL'].iloc[0]
        current_total_kilos = dff["TOTAL KILOS NETO (KG)"].sum()
        
        # Verificar si el FCL ha cambiado
        current_n_despacho = f"FCL {current_fcl}"
        
        # Solo actualizar automáticamente si los datos no han sido modificados manualmente
        if not st.session_state.data_manually_modified:
            # Actualizar N° Despacho si el FCL ha cambiado o está vacío
            if (st.session_state.header_data['n_despacho'] == "" or 
                st.session_state.header_data['n_despacho'] == "0.0" or
                not st.session_state.header_data['n_despacho'].startswith(f"FCL {current_fcl}")):
                st.session_state.header_data['n_despacho'] = current_n_despacho
            
            # Actualizar peso neto si ha cambiado o está en valor por defecto
            if (st.session_state.header_data['peso_neto'] == "0.0" or 
                st.session_state.header_data['peso_neto'] == "" or
                abs(float(st.session_state.header_data['peso_neto']) - current_total_kilos) > 0.1):
                st.session_state.header_data['peso_neto'] = str(current_total_kilos)
    
    # Inicializar flags para controlar mensajes de confirmación
    if 'data_saved' not in st.session_state:
        st.session_state.data_saved = False
    
    if 'form_cleared' not in st.session_state:
        st.session_state.form_cleared = False
    
    # Flag para controlar si los datos han sido modificados manualmente
    if 'data_manually_modified' not in st.session_state:
        st.session_state.data_manually_modified = False
    
    # Función para el diálogo de configuración de encabezado
    @st.experimental_dialog("📋 Configurar Encabezado del PDF",width="large")
    def configurar_encabezado():

        
        # Usar st.form para evitar re-ejecuciones
        with st.form("header_form", clear_on_submit=False):
            # Primera fila: Información de Despacho
            st.markdown("**📤 Información de Despacho:**")
            col1, col2 = st.columns(2)
            
            with col1:
                temp_n_despacho = st.text_input(
                    "N° Despacho:", 
                    value=st.session_state.header_data['n_despacho'],
                    help="Número de despacho"
                )
                temp_exportador = st.text_input(
                    "Exportador:", 
                    value=st.session_state.header_data['exportador'],
                    help="Nombre del exportador"
                )
                temp_cliente = st.text_input(
                    "Cliente:", 
                    value=st.session_state.header_data['cliente'],
                    help="Nombre del cliente"
                )
            
            with col2:
                temp_fecha_despacho = st.text_input(
                    "Fecha de Despacho:", 
                    value=st.session_state.header_data['fecha_despacho'],
                    help="Fecha de despacho (ej: 15/12/2024)"
                )
                temp_consignatario = st.text_input(
                    "Consignatario:", 
                    value=st.session_state.header_data['consignatario'],
                    help="Nombre del consignatario"
                )
            
            # Segunda fila: Información de Envío
            st.markdown("**🚢 Información de Envío:**")
            col3, col4 = st.columns(2)
            
            with col3:
                temp_puerto_carga = st.text_input(
                    "Puerto de Carga:", 
                    value=st.session_state.header_data['puerto_carga'],
                    help="Puerto de carga"
                )
                temp_n_contenedor = st.text_input(
                    "N° de Contenedor:", 
                    value=st.session_state.header_data['n_contenedor'],
                    help="Número del contenedor"
                )
                temp_booking = st.text_input(
                    "Booking:", 
                    value=st.session_state.header_data['booking'],
                    help="Número de booking"
                )
            
            with col4:
                temp_destino = st.text_input(
                    "Destino:", 
                    value=st.session_state.header_data['destino'],
                    help="Puerto de destino"
                )
                temp_nave = st.text_input(
                    "Nave:", 
                    value=st.session_state.header_data['nave'],
                    help="Nombre de la nave"
                )
            
            # Tercera fila: Fechas
            st.markdown("**📅 Fechas:**")
            col5, col6 = st.columns(2)
            
            with col5:
                temp_etd = st.text_input(
                    "ETD:", 
                    value=st.session_state.header_data['etd'],
                    help="Estimated Time of Departure"
                )
            
            with col6:
                temp_eta = st.text_input(
                    "ETA:", 
                    value=st.session_state.header_data['eta'],
                    help="Estimated Time of Arrival"
                )
            
            # Cuarta fila: Pesos (usando number_input para valores numéricos)
            st.markdown("**⚖️ Pesos:**")
            col7, col8 = st.columns(2)
            
            with col7:
                 # Convertir a float si es posible, sino usar el total calculado
                 peso_neto_value = total_kilos
                 if st.session_state.header_data['peso_neto']:
                     try:
                         peso_neto_value = float(st.session_state.header_data['peso_neto'])
                     except:
                         peso_neto_value = total_kilos
                 
                 temp_peso_neto = st.number_input(
                     "Peso Neto (kg):", 
                     value=peso_neto_value,
                     min_value=0.0,
                     step=0.1,
                     format="%.1f",
                     help="Peso neto total en kilogramos"
                 )
            
            with col8:
                # Convertir a float si es posible, sino usar 0.0
                peso_bruto_value = 0.0
                if st.session_state.header_data['peso_bruto']:
                    try:
                        peso_bruto_value = float(st.session_state.header_data['peso_bruto'])
                    except:
                        peso_bruto_value = 0.0
                
                temp_peso_bruto = st.number_input(
                    "Peso Bruto (kg):", 
                    value=peso_bruto_value,
                    min_value=0.0,
                    step=0.1,
                    format="%.1f",
                    help="Peso bruto total en kilogramos"
                )
            
            # Botones de acción dentro del formulario
            col_btn1, col_btn2= st.columns([1, 1])
            
            with col_btn1:
                submit_button = st.form_submit_button("💾 Guardar Datos", type="primary", use_container_width=True)
            
            with col_btn2:
                clear_button = st.form_submit_button("🗑️ Limpiar Formulario", type="secondary", use_container_width=True)
            
            #with col_btn3:
            #    cancel_button = st.form_submit_button("❌ Cancelar", type="secondary", use_container_width=True)
        
        # Manejar las acciones del formulario usando session state para evitar re-ejecuciones
        if submit_button:
            # Guardar los datos temporales en session state
            st.session_state.header_data = {
                'n_despacho': temp_n_despacho,
                'fecha_despacho': temp_fecha_despacho,
                'exportador': temp_exportador,
                'cliente': temp_cliente,
                'consignatario': temp_consignatario,
                'puerto_carga': temp_puerto_carga,
                'destino': temp_destino,
                'n_contenedor': temp_n_contenedor,
                'booking': temp_booking,
                'nave': temp_nave,
                'etd': temp_etd,
                'eta': temp_eta,
                'peso_neto': str(temp_peso_neto),  # Convertir a string para mantener compatibilidad
                'peso_bruto': str(temp_peso_bruto)  # Convertir a string para mantener compatibilidad
            }
            # Marcar que se guardaron datos para mostrar mensaje
            st.session_state.data_saved = True
            # Marcar que los datos han sido modificados manualmente
            st.session_state.data_manually_modified = True
            st.rerun()
        
        if clear_button:
            # Limpiar todos los campos del formulario
            st.session_state.header_data = {
                'n_despacho': f"FCL {dff['Nº FCL'].iloc[0]}" if len(dff) > 0 else "",
                'fecha_despacho': "",
                'exportador': "",
                'cliente': "",
                'consignatario': "",
                'puerto_carga': "",
                'destino': "",
                'n_contenedor': "",
                'booking': "",
                'nave': "",
                'etd': "",
                'eta': "",
                'peso_neto': str(dff["TOTAL KILOS NETO (KG)"].sum()) if len(dff) > 0 else "0.0",  # Usar el total actual
                'peso_bruto': "0.0"  # Resetear peso bruto
            }
            st.session_state.data_saved = False
            st.session_state.form_cleared = True
            # Resetear el flag de modificación manual para permitir actualizaciones automáticas
            st.session_state.data_manually_modified = False
            st.rerun()
        
       
    
    # Botón para abrir el diálogo
    col_dialog1, col_dialog2 = st.columns([3, 1])
    with col_dialog1:
        st.markdown("#### **Configuración de Encabezado:**")
    with col_dialog2:
        if st.button("📋 Configurar Encabezado", type="secondary", use_container_width=True):
            configurar_encabezado()
    
    # Mostrar mensajes de confirmación usando session state
    if st.session_state.get('data_saved', False):
        st.success("✅ **¡Datos guardados exitosamente!** Los datos del encabezado se usarán al generar el PDF.")
        st.toast('Datos Guardados!', icon='🎉')
        # Resetear el flag para evitar mostrar el mensaje repetidamente
        st.session_state.data_saved = False
    
    if st.session_state.get('form_cleared', False):
        st.info("🗑️ **Formulario limpiado.** Todos los campos han sido restablecidos.")
        st.toast('Formulario Limpiado!', icon='🧹')
        # Resetear el flag para evitar mostrar el mensaje repetidamente
        st.session_state.form_cleared = False
    # Botones de descarga con mejor diseño
    st.markdown("#### **Formatos de Descarga:**")
    
    col_download1, col_download2 = st.columns(2)
    
    with col_download1:
        st.download_button(
            label="📊 **Descargar Excel**",
            data=processed_data,
            file_name="packing_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Descargar en formato Excel",
            use_container_width=True
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_download2:
        try :
            if len(dff) > 0:
                # Preparar los datos del encabezado para el PDF
                header_data_for_pdf = [
                    ["N° DESPACHO:", st.session_state.header_data['n_despacho'], "PUERTO DE CARGA:", st.session_state.header_data['puerto_carga'], "ETD:", st.session_state.header_data['etd']],
                    ["FECHA DE DESPACHO:", st.session_state.header_data['fecha_despacho'], "DESTINO:", st.session_state.header_data['destino'], "ETA:", st.session_state.header_data['eta']],
                    ["EXPORTADOR:", st.session_state.header_data['exportador'], "N° DE CONTENEDOR:", st.session_state.header_data['n_contenedor'], "PESO NETO:", st.session_state.header_data['peso_neto']],
                    ["CLIENTE:", st.session_state.header_data['cliente'], "BOOKING:", st.session_state.header_data['booking'], "PESO BRUTO:", st.session_state.header_data['peso_bruto']],
                    ["CONSIGNATARIO:", st.session_state.header_data['consignatario'], "NAVE:", st.session_state.header_data['nave'], "", ""]
                ]
                
                pdf_buffer = crear_pdf_packing_list(dff, "./src/assets/logo.jpg", header_data_for_pdf)
                
                st.download_button(
                    label="📄 **Descargar PDF**",
                    data=pdf_buffer.getvalue(),
                    file_name="packing_list.pdf",
                    mime="application/pdf",
                    help="Descargar en formato PDF horizontal para impresión",
                    use_container_width=True
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: #f0f0f0;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    color: #666;
                    margin: 10px 0;
                ">
                📄 **PDF no disponible**
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")

def packing_list_testing():
    styles(2)
    
    
    col_head1,col_head2,col_head3= st.columns([4,6,2])
    with col_head1:
        st.title("📄Packing List Testing")
    

    
    @st.cache_data(show_spinner="Cargando datos...",persist="disk")
    def get_data():
        access_token = get_access_token()
        DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!Mx2p-6knhUeohEjU-L-a3w-JZv1JawxAkEY9khgxn7hWjhq65fg_To08YnAwHSc0", "01L5M4SATOWDS7G66DCNCYJLOJVNY7SPTV")
        data_ = get_download_url_by_name(DATAS, "REGISTRO DE PHL - PRODUCTO TERMINADO -154.xlsm")
        
        return (
             pd.read_excel(data_, sheet_name="BD1",skiprows=6),
             pd.read_excel(data_, sheet_name="GMH-ABG-CYN"),
             pd.read_excel(data_, sheet_name="SAN LUCAR"),
             pd.read_excel(data_, sheet_name="SAN EFISIO"),
             pd.read_excel(data_, sheet_name="GAP BERRIES"),
        )
    
    _,df_gmh,df_san_lucar,df_san_efisio,df_gap_berries = get_data()
    df_gmh = df_gmh[df_gmh["F. PRODUCCION"].notna()]
    df_gmh["DESCRIPCION DEL PRODUCTO"] = df_gmh["DESCRIPCION DEL PRODUCTO"].str.strip()
    print(df_gmh.columns)
    df_gmh["CONTENEDOR"] = df_gmh["CONTENEDOR"].fillna("NO ESPECIFICADO")
    df_gmh["CONTENEDOR"] = df_gmh["CONTENEDOR"].str.strip()
    df_gmh["Nº DE PALLET"] = df_gmh["Nº DE PALLET"].fillna("NO ESPECIFICADO")
    df_gmh["Nº DE PALLET"] = df_gmh["Nº DE PALLET"].str.strip()

    df_gmh["PRODUCTO"] = "ARANDANO"
    df_gmh["VARIEDAD"] = df_gmh["VARIEDAD"].fillna("NO ESPECIFICADO")
    df_gmh["VARIEDAD"] = df_gmh["VARIEDAD"].str.strip()
    df_gmh["FUNDO"] = df_gmh["FUNDO"].fillna("NO ESPECIFICADO")
    df_gmh["FUNDO"] = df_gmh["FUNDO"].str.strip()
    















    st.write(f"GMH {df_gmh.shape[1]}")
    st.dataframe(df_gmh)
    st.write(f"SAN LUCAR {df_san_lucar.shape[1]}")
    st.dataframe(df_san_lucar)
    st.write(f"SAN EFISIO {df_san_efisio.shape[1]}")
    st.dataframe(df_san_efisio)
    st.write(f"GAP BERRIES {df_gap_berries.shape[1]}")
    st.dataframe(df_gap_berries)









    
    
    
    
    
    
    
    