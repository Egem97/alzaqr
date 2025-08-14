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
    
    
    col_head1,col_head2,col_head3,col_head4 = st.columns([4,3,3,2])
    with col_head1:
        st.title("📄Packing List")
    

    
    @st.cache_data(show_spinner="Cargando datos...",ttl=300)
    def get_data():
        access_token = get_access_token()
        DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!Mx2p-6knhUeohEjU-L-a3w-JZv1JawxAkEY9khgxn7hWjhq65fg_To08YnAwHSc0", "01L5M4SATOWDS7G66DCNCYJLOJVNY7SPTV")
        data_ = get_download_url_by_name(DATAS, "REGISTRO DE PHL - PRODUCTO TERMINADO -154.xlsm")
        
        return pd.read_excel(data_, sheet_name="TD-DATOS PT"),pd.read_excel(data_, sheet_name="BD1",skiprows=6)
    
    df,producto_peso_df = get_data()
    
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
    df["F. PRODUCCION"] = pd.to_datetime(df['F. PRODUCCION'], errors="coerce").dt.date
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
        input_fecha = st.selectbox("Selecciona fecha",sorted(dff["FECHA DE PRODUCCIÓN"].unique()),index=None,placeholder="Selecciona fecha")
        if input_fecha:
            dff = dff[dff["FECHA DE PRODUCCIÓN"] == input_fecha]
    with col_head3:
        input_fundo = st.selectbox("Selecciona fundo",dff["NOMBRE DEL FUNDO"].unique(),index=None,placeholder="Selecciona fundo")
        if input_fundo:
            dff = dff[dff["NOMBRE DEL FUNDO"] == input_fundo]
    with col_head4:
        input_container = st.selectbox("Selecciona contenedor",dff["Nº FCL"].unique(),index=None,placeholder="Selecciona contenedor")
        if input_container:
            dff = dff[dff["Nº FCL"] == input_container]
    dff = dff.sort_values(by="FECHA DE PRODUCCIÓN",ascending=True)
    validador_pdf = len(dff["Nº FCL"].unique())
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
    
    # Sección de descarga mejorada
    
    

    
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
        if len(dff) > 0 and validador_pdf == 1:
            pdf_buffer = crear_pdf_packing_list(dff, "./src/assets/logo.jpg")
            
            
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
    









    
    
    
    
    
    
    
    