import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from styles import styles
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode ,JsCode
from io import StringIO, BytesIO
from utils.helpers import crear_pdf, generar_qr
from utils.components import aggrid_builder
from utils.g_sheets import read_sheet

def qrtool():
    st.session_state['uploaded_dataframe'] = None
    styles(2)
    col_header1,col_header2,col_header3,col_header4,col_header5 = st.columns([5,2,2,2,2])
    with col_header1:
        st.title("Generador de QR")
    
    try:
        #try:
        data = read_sheet("1PWz0McxGvGGD5LzVFXsJTaNIAEYjfWohqtimNVCvTGQ","KF")
        df = pd.DataFrame(data[1:], columns=data[0],)#dtype={'N° TARJETA PALLET': str}
        #df.to_excel("recepcion.xlsx",index=False)
        
        #st.dataframe(df)
        #df.to_excel("recepcion.xlsx",index=False)
        del data
    except:
        st.error("Error al cargar la información, actualice la pagina")
    
    #st.dataframe(df)
    #print(df["N° JABAS"].unique()	)
    df['FECHA RECEPCION'] = df['FECHA SALIDA CAMPO'] 
    
    df["PESO NETO CAMPO"] = df["PESO NETO CAMPO"].str.replace(",", ".", regex=False).astype(float)
    df["KILOS BRUTO"] = df["KILOS BRUTO"].str.replace(",", ".", regex=False).astype(float)
    df["KILOS NETO"] = df["KILOS NETO"].str.replace(",", ".", regex=False).astype(float)
    df["N° JABAS"] = df["N° JABAS"].replace('',0)
    df["N° JABAS"] = df["N° JABAS"].astype(float)
    df["N° JARRAS"] = df["N° JARRAS"].replace('','0')
    
    df["N° JARRAS"] = df["N° JARRAS"].str.replace(",", ".", regex=False).astype(float)
    df["PESO PROMEDIO JARRA"] = df["PESO PROMEDIO JARRA"].replace('',"0")
    df["PESO PROMEDIO JARRA"] = df["PESO PROMEDIO JARRA"].str.replace(",", ".", regex=False).astype(float)
    df["TEMPERATURA"] = df["TEMPERATURA"].fillna("0")
    df["TEMPERATURA"] = df["TEMPERATURA"].str.replace("", "0", regex=False)
    df["TEMPERATURA"] = df["TEMPERATURA"].str.replace(",", ".", regex=False).astype(float)
    df["PESO PROMEDIO JABA"] = df["PESO PROMEDIO JABA"].replace('',"0")
    df["PESO PROMEDIO JABA"] = df["PESO PROMEDIO JABA"].str.replace(",", ".", regex=False).astype(float)
    df["DIF"] = df["DIF"].str.replace(",", ".", regex=False).astype(float)
    df["TRASLADO"] = df["TRASLADO"].str.replace(",", ".", regex=False).astype(float)

    df["PESO PALLET"] = df["PESO PALLET"].replace('',"0")
    df["PESO PALLET"] = df["PESO PALLET"].astype(float)
    
    df["DETALLE"] = df["DETALLE"].fillna("N/A")
    df["DETALLE"] = df["DETALLE"].str.strip()
    df["#CAJAS"] = df["#CAJAS"].replace('',"0")
    df["#CAJAS"] = df["#CAJAS"].astype(int)

    df["FUNDO"] = df["FUNDO"].str.strip()


    var_category = ['CODIGO QR','EMPRESA','TIPO PRODUCTO','FUNDO', 'VARIEDAD', 'N° PALLET',  'PLACA','N° TARJETA PALLET','GUIA']
    var_numeric = ["KILOS BRUTO","KILOS NETO","PESO NETO CAMPO","N° JABAS","N° JARRAS"]
    df = df[df['FECHA RECEPCION'].notna()]
    df['FECHA RECEPCION'] = pd.to_datetime(df['FECHA RECEPCION'], dayfirst=True).dt.strftime('%Y-%m-%d')
    df['FECHA SALIDA CAMPO'] = pd.to_datetime(df['FECHA SALIDA CAMPO'], dayfirst=True).dt.strftime('%Y-%m-%d')
    df['N° VIAJE'] = df['N° VIAJE'].astype(str)
        
    df['T° ESTADO'] = df['T° ESTADO'].fillna("-")
    df[var_category] = df[var_category].fillna("-")
    df[var_numeric] = df[var_numeric].fillna(0)
        
    df["GUIA CONSOLIDADA"] = df["GUIA CONSOLIDADA"].fillna("-")

    fecha_recep_list =sorted(df['FECHA RECEPCION'].unique())
    
            
            #del df
    fcol1,fcol2,fcol3,fcol4,fcol5 = st.columns(5)
    with fcol1:
            fecha_filtro = st.selectbox("Fecha Recepción",fecha_recep_list,index=None,placeholder="Seleccione una fecha")
    if fecha_filtro is not None:
            df = df[df["FECHA RECEPCION"]==fecha_filtro]
    viaje_list =sorted(df['N° VIAJE'].unique())
    detalle_list = sorted(df["DETALLE"].unique())
    with fcol2:
                detalle_filtro = st.selectbox("DETALLE",detalle_list,index=None,placeholder="Seleccione detalle")
                if detalle_filtro is not None:
                    df = df[df["DETALLE"]==detalle_filtro]
    tarjeta_list =sorted(df['N° TARJETA PALLET'].unique())
    with fcol3:
                viaje_filtro = st.multiselect("N° de Viaje",viaje_list,placeholder="Seleccione un N° de Viaje")
                if len(viaje_filtro)> 0:
                    df = df[df["N° VIAJE"].isin(viaje_filtro)]
    tarjeta_list =sorted(df['N° TARJETA PALLET'].unique())
    with fcol4:
                tarja_filtro = st.selectbox("N° de Tarja",tarjeta_list,index=None,placeholder="Seleccione una tarja")
                if tarja_filtro is not None:
                    df = df[df["N° TARJETA PALLET"]==tarja_filtro]
    with fcol5:
                find_cod = st.text_input("Busque el QR",placeholder="Ingrese el codigo qr")
    #except:
    #    st.error("Error al cargar la información")

            
    

    if df is not None:

        st.session_state['uploaded_dataframe'] = df
        try:
            df["OBSERVACIONES"] = df["OBSERVACIONES"].fillna("")
            df["OBSERVACIONES"] = df["OBSERVACIONES"]+"-"
        except:
            pass

        df = df.groupby([
            'CODIGO QR','EMPRESA','FECHA RECEPCION', 'TIPO PRODUCTO','FUNDO', 'VARIEDAD', 'N° PALLET', 'N° VIAJE', 'PLACA','N° TARJETA PALLET','GUIA','CALIBRE','T° ESTADO','DETALLE'
            ]).agg(
                {
                    "KILOS BRUTO": "sum",
                    "KILOS NETO": "sum",
                    "PESO NETO CAMPO": "sum",
                    "N° JABAS": "sum",
                    "N° JARRAS": "sum",
                    "#CAJAS": "sum",
                    "OBSERVACIONES":"sum"
                }
            ).reset_index()
        def remove_duplicate_text(text):
            """
            Elimina texto repetido en un string
            Ejemplo: "FRUTA MOJADA-FRUTA MOJADA" -> "FRUTA MOJADA"
            """
            if pd.isna(text) or text == "":
                return text
            
            text = str(text)
            
            # Dividir por guiones y eliminar duplicados manteniendo el orden
            parts = text.split('-')
            unique_parts = []
            for part in parts:
                part = part.strip()
                if part and part not in unique_parts:
                    unique_parts.append(part)
            
            return '-'.join(unique_parts)
        try:
            df['OBSERVACIONES'] = df['OBSERVACIONES'].apply(remove_duplicate_text)
        except:
            pass
        with col_header2:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; background: #f8f9fa;">
                <p style="margin: 0; font-size: 14px; color: #666;">N° Pallets</p>
                <p style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">{len(df['CODIGO QR'].unique()):,}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_header3:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; background: #f8f9fa;">
                <p style="margin: 0; font-size: 14px; color: #666;">Peso Neto Campo</p>
                <p style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">{df['PESO NETO CAMPO'].sum().round(1):,}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_header4:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; background: #f8f9fa;">
                <p style="margin: 0; font-size: 14px; color: #666;">Peso Neto</p>
                <p style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">{df['KILOS NETO'].sum().round(1):,}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_header5:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; background: #f8f9fa;">
                <p style="margin: 0; font-size: 14px; color: #666;">Peso Bruto</p>
                <p style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">{df['KILOS BRUTO'].sum().round(1):,}</p>
            </div>
            """, unsafe_allow_html=True)
        
        df["PESO NETO CAMPO"] = df["PESO NETO CAMPO"].round(2)
        df = df[df["CODIGO QR"].str.contains(find_cod)]
        show_dff = df.copy()
        show_dff = show_dff[['CODIGO QR','FECHA RECEPCION', 'TIPO PRODUCTO','FUNDO', 'VARIEDAD', 'N° PALLET', 'N° VIAJE', 'PLACA','N° TARJETA PALLET','CALIBRE','KILOS BRUTO','KILOS NETO','PESO NETO CAMPO','N° JABAS','N° JARRAS','#CAJAS']]
        #st.write(show_dff.shape)
        #st.write(len(show_dff['CODIGO QR'].unique()))
        #show_dff.to_excel("show_dff.xlsx",index=False)
        
        gb = GridOptionsBuilder.from_dataframe(show_dff)
        gb.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True)
        #
        gb.configure_column("CODIGO QR", width=400)
        grid_options = gb.build()

        grid_response = AgGrid(show_dff, # Dataframe a mostrar
                                gridOptions=grid_options,
                                enable_enterprise_modules=False,
                                #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                                update_mode=GridUpdateMode.SELECTION_CHANGED , 
                                fit_columns_on_grid_load=True,
                                height=550
        )
        #st.write(grid_response['selected_rows'])
        st.dataframe(df)
        try:
            #st.write(list(grid_response['selected_rows']["N° TARJETA PALLET"].values))
            df = df[df["N° TARJETA PALLET"].isin(list(grid_response['selected_rows']["N° TARJETA PALLET"].values))]
            #st.dataframe(df)
            df["KILOS NETO"] = df["KILOS NETO"].round(3)
            df["KILOS BRUTO"] = df["KILOS BRUTO"].round(3)
            df["PESO NETO CAMPO"] = df["PESO NETO CAMPO"].round(3)
            df["N° JABAS"] = df["N° JABAS"].round(3)
            df["N° JARRAS"] = df["N° JARRAS"].round(3)
            
            
            
            
            if not df.empty:
                lista_datos = []
                for i in range(len(df)):
                    datos = {
                        'key_qr': df["CODIGO QR"].values[i],
                        'cultivo': "ARANDANO",
                        'tipo_producto': df["TIPO PRODUCTO"].values[i],
                        'empresa': df["EMPRESA"].values[i],
                        'fundo': df["FUNDO"].values[i],
                        'variedad': df["VARIEDAD"].values[i],
                        'num_pallet': df["N° PALLET"].values[i],
                        'guia': df["GUIA"].values[i],
                        'viaje': df["N° VIAJE"].values[i],
                        'num_tarja': df["N° TARJETA PALLET"].values[i],
                        'fecha': df["FECHA RECEPCION"].values[i],
                        'peso_bruto': df["KILOS BRUTO"].values[i],
                        'num_jabas': df["N° JABAS"].values[i],
                        'num_jarras': df["N° JARRAS"].values[i],
                        'peso_campo': df["PESO NETO CAMPO"].values[i],
                        'peso_neto': df["KILOS NETO"].values[i],
                        'calibre': df["CALIBRE"].values[i],
                        'temperatura_estado': df["T° ESTADO"].values[i],
                        'tunel_enfriamiento': "",
                        'detalle': df["DETALLE"].values[i],
                        'num_cajas': df["#CAJAS"].values[i],
                        'observaciones': df["OBSERVACIONES"].values[i]
                    }
                    lista_datos.append(datos)
                
                # Generar el PDF consolidado
                pdf_buffer = crear_pdf(lista_datos, "./src/assets/logo.jpg")
                
                # Botón único para descargar el PDF con todos los formatos
                st.download_button(
                    label=f"📄 Descargar PDF Consolidado ({len(lista_datos)} registros)",
                    data=pdf_buffer,
                    file_name="boletas_consolidadas.pdf",
                    mime="application/pdf",
                    key="pdf_consolidado_download"
                )
                
            else:
                st.info("Por favor, seleccione al menos un registro para generar el PDF.")
        except:
            st.error("Debe seleccionar un registro")

    
        

        



def dashboard():
    styles(1)
    col_header1,col_header2,col_header3,col_header4,col_header5 = st.columns([4,2,2,2,2])
    with col_header1:
        st.title("📈Datos de Recepcion")
    
    
    # Verificar si hay datos disponibles en session state
    if 'uploaded_dataframe' in st.session_state :
        st.success("✅ Datos cargados desde QR Tool")
        df = st.session_state['uploaded_dataframe']
        df["PESO PROMEDIO JARRA"] = df["PESO PROMEDIO JARRA"].fillna(0)
        
        list_fecha = sorted(df["FECHA SALIDA CAMPO"].unique())
        list_viaje = sorted(df["N° VIAJE"].unique())
        #list_empresa = sorted(df["EMPRESA"].unique())
        list_fundo = sorted(df["FUNDO"].unique())
        list_detalle = sorted(df["DETALLE"].unique())
        #list_variedad = sorted(df["VARIEDAD"].unique())
        #list_tarjeta = sorted(df["N° TARJETA PALLET"].unique())
        #list_jaba = sorted(df["JABA"].unique())
        with col_header2:
            fecha_out_campo = st.selectbox("Fecha Salida Campo",list_fecha,index=None,placeholder="Seleccione una fecha")
            if fecha_out_campo is not None:
                df = df[df["FECHA SALIDA CAMPO"]==fecha_out_campo]
        with col_header3:
            viaje = st.selectbox("N° de Viaje",list_viaje,index=None,placeholder="Seleccione un N° de Viaje")
            if viaje is not None:
                df = df[df["N° VIAJE"]==viaje]
        with col_header4:
            fundo = st.selectbox("Fundo",list_fundo,index=None,placeholder="Seleccione un Fundo")    
            if fundo is not None:
                df = df[df["FUNDO"]==fundo]
        with col_header5:
            detalle_input = st.selectbox("Detalle",list_detalle,index=None,placeholder="Seleccione un Detalle")
            if detalle_input is not None:
                df = df[df["DETALLE"]==detalle_input]
        #st.dataframe(df)
        tab1,tab2,tab3,tab4 = st.tabs(["Reporte","Stock","RP Semana","Campaña 2025"])
        with tab1:
            ingreso_dff= df.groupby([
                "EMPRESA","FUNDO","VARIEDAD","CALIBRE"
            ]).agg({"KILOS NETO": "sum"}).reset_index()
            ingreso_dff["KILOS NETO"] = ingreso_dff["KILOS NETO"].round(2)
            # Crear fila total para ingreso_dff
            total_row_ingreso = {
                "EMPRESA": "TOTAL",
                "FUNDO": "",
                "VARIEDAD": "",
                "CALIBRE": "",
                "KILOS NETO": ingreso_dff["KILOS NETO"].sum()
            }
            ingreso_dff = pd.concat([ingreso_dff, pd.DataFrame([total_row_ingreso])], ignore_index=True)

            aggrid_builder(ingreso_dff)
            
            ingreso2_dff = df.groupby([
                  "FECHA RECEPCION","EMPRESA","FUNDO","VARIEDAD","TIPO PRODUCTO"
            ]).agg({"N° JABAS": "sum","N° JARRAS": "sum","KILOS NETO": "sum"}).reset_index()
            #
            ingreso2_dff["KILOS NETO"] = ingreso2_dff["KILOS NETO"].round(2)
            # Crear fila total para ingreso2_dff
            total_row_ingreso2 = {
                "FECHA RECEPCION": "TOTAL",
                "EMPRESA": "",
                "FUNDO": "",
                "VARIEDAD": "",
                "TIPO PRODUCTO": "",
                "N° JABAS": ingreso2_dff["N° JABAS"].sum(),
                "N° JARRAS": ingreso2_dff["N° JARRAS"].sum(),
                "KILOS NETO": ingreso2_dff["KILOS NETO"].sum()
            }
            ingreso2_dff = pd.concat([ingreso2_dff, pd.DataFrame([total_row_ingreso2])], ignore_index=True)

            aggrid_builder(ingreso2_dff)
        with tab2:
            
            grouped_df = df.groupby([
                "FECHA RECEPCION","N° VIAJE","EMPRESA","FUNDO","VARIEDAD",
                "N° TARJETA PALLET","CALIBRE"
            ]).agg({
                "KILOS BRUTO": "sum",
                "PESO NETO CAMPO": "sum", 
                "KILOS NETO": "sum",
                "N° JABAS": "sum",
                "PESO PROMEDIO JARRA": "mean"  
            }).reset_index()
            grouped_df["KILOS BRUTO"] = grouped_df["KILOS BRUTO"].round(2)

            
            total_row = {
                "FECHA RECEPCION": "TOTAL",
                "N° VIAJE": np.nan,
                "EMPRESA": "",
                "FUNDO": "",
                "VARIEDAD": "",
                "N° TARJETA PALLET": "",
                "CALIBRE": "",
                "KILOS BRUTO": grouped_df['KILOS BRUTO'].sum().round(2),
                "PESO NETO CAMPO": grouped_df['PESO NETO CAMPO'].sum().round(2),
                "KILOS NETO": grouped_df['KILOS NETO'].sum().round(2),
                "N° JABAS": grouped_df['N° JABAS'].sum().round(2),
                "PESO PROMEDIO JARRA": grouped_df['PESO PROMEDIO JARRA'].mean().round(2)
            }
            grouped_df["PESO NETO CAMPO"] = grouped_df["PESO NETO CAMPO"].round(2)
            grouped_df["KILOS NETO"] = grouped_df["KILOS NETO"].round(2)
            # Agrega la fila al final
            grouped_dff = pd.concat([grouped_df, pd.DataFrame([total_row])], ignore_index=True)
            
            gb = GridOptionsBuilder.from_dataframe(grouped_dff)
            
            # Ajustar automáticamente el ancho de todas las columnas
            for col in grouped_dff.columns:
                gb.configure_column(col, autoWidth=True)

            # --- Estilo para resaltar la última fila en todas las columnas con texto más grande ---
            cellstyle_last_row = JsCode(f"""
                function(params) {{
                    if (params.node.rowIndex === {len(grouped_dff) - 1}) {{
                        return {{
                            'font-weight': 'bold',
                            'background': '#33373a',
                            'color': '#fff',
                            'font-size': '16px'
                        }}
                    }}
                }}
            """)
            # Aplica el estilo a todas las columnas
            for col in grouped_df.columns:
                gb.configure_column(col, cellStyle=cellstyle_last_row)

            grid_options = gb.build()

            # Reducir el tamaño de fuente de la tabla para ver más columnas
            custom_css = {
                ".ag-theme-streamlit .ag-cell": {"font-size": "12px !important"},
                ".ag-theme-streamlit .ag-header-cell-label": {"font-size": "13px !important"},
            }
            
            row_height = 35
            header_height = 35
            num_rows = len(grouped_dff)
            height = header_height + (num_rows * row_height)
            height = max(height, 120)  # Altura mínima

            grid_response = AgGrid(
                grouped_dff,
                gridOptions=grid_options,
                enable_enterprise_modules=False,
                update_mode='MODEL_CHANGED',
                fit_columns_on_grid_load=True,
                height=height-20,
                allow_unsafe_jscode=True,
                custom_css=custom_css
            )


            with tab3:
                df_wsemana = df.copy()
                df_wsemana["SEMANA"] = df_wsemana["SEMANA"].astype(str)
                #st.dataframe(df_wsemana)
                #df_wsemana["FECHA RECEPCION"] = pd.to_datetime(df_wsemana["FECHA RECEPCION"], dayfirst=True, errors='coerce')
                #df_wsemana["SEMANA"] = df_wsemana["FECHA RECEPCION"].dt.isocalendar().week
                #df_wsemana["FECHA RECEPCION"] = pd.to_datetime(df_wsemana["FECHA RECEPCION"]).dt.strftime("%d/%m/%Y")
                df_wsemana["KILOS NETO"] = df_wsemana["KILOS NETO"].round(2)
                #st.dataframe(df_wsemana)
                semana = st.selectbox("Semana",df_wsemana["SEMANA"].unique())
                
                df_wsemana = df_wsemana[df_wsemana["SEMANA"]==semana]
                
                #df_wsemana_group = df_wsemana.groupby([
                #    "EMPRESA","FUNDO","VARIEDAD","TIPO PRODUCTO","FECHA RECEPCION"
                #]).agg({"KILOS NETO": "sum"}).reset_index()
                wsemana_pivot_dff = pd.pivot_table(
                    df_wsemana,
                    values="KILOS NETO",
                    index=["EMPRESA", "FUNDO", "VARIEDAD", "TIPO PRODUCTO"],
                    columns="FECHA RECEPCION",
                    aggfunc="sum",
                    fill_value=0,
            
                ).reset_index()
                
                
                wsemana_pivot_dff["TOTAL"] = wsemana_pivot_dff[wsemana_pivot_dff.columns[4:]].sum(axis=1).round(2)
                wsemana_pivot_dff = wsemana_pivot_dff.reset_index()
                wsemana_pivot_dff = wsemana_pivot_dff.drop(columns=["index"])

                total_row = {col: "" for col in wsemana_pivot_dff.columns}
                total_row["EMPRESA"] = "TOTAL"
                for col in wsemana_pivot_dff.columns:
                    if col not in ["EMPRESA", "FUNDO", "VARIEDAD", "TIPO PRODUCTO"]:
                        total_row[col] = wsemana_pivot_dff[col].sum().round(2)  
                wsemana_pivot_dff = pd.concat([wsemana_pivot_dff, pd.DataFrame([total_row])], ignore_index=True)
                aggrid_builder(wsemana_pivot_dff)
                #st.line_chart(df_wsemana, x="FECHA RECEPCION", y="KILOS NETO")
                
        with tab4:
            df_week = df.copy()
            
            df_week["FECHA RECEPCION"] = pd.to_datetime(df_week["FECHA RECEPCION"], dayfirst=True, errors='coerce')
            #df_week["SEMANA"] = df_week["FECHA RECEPCION"].dt.isocalendar().week
            #df_week["SEMANA"] = df_week["SEMANA"].astype(str)
            df_week["FECHA RECEPCION"] = pd.to_datetime(df_week["FECHA RECEPCION"]).dt.strftime("%d/%m/%Y")
            df_week["KILOS NETO"] = df_week["KILOS NETO"].round(2)
            week_pivot = pd.pivot_table(
                df_week,
                values="KILOS NETO",
                index=["EMPRESA", "FUNDO", "VARIEDAD", "TIPO PRODUCTO"],
                columns="SEMANA",
                aggfunc="sum",
                fill_value=0
            )
            week_pivot["TOTAL"] = week_pivot.sum(axis=1)
            week_pivot = week_pivot.reset_index()
            total_row_week = {col: "" for col in week_pivot.columns}
            total_row_week["EMPRESA"] = "TOTAL"
            for col in week_pivot.columns:
                if col not in ["EMPRESA", "FUNDO", "VARIEDAD", "TIPO PRODUCTO"]:
                    total_row_week[col] = week_pivot[col].sum().round(0)
            week_pivot = pd.concat([week_pivot, pd.DataFrame([total_row_week])], ignore_index=False)
            
            aggrid_builder(week_pivot)
            
        
        
    else:
        st.warning("⚠️ No hay datos disponibles. Por favor, carga un archivo Excel en la sección 'Generador de QR' primero.")
        st.info("💡 Ve a la pestaña 'Generador de QR', sube un archivo Excel y luego regresa aquí para ver el dashboard.")



def qrgenerator():
    styles(2)
    dict_resumen_empresa = {
        "AGRICOLA BLUE GOLD S.A.C":{"ACORTADOR":"ABG"},
        "GMH BERRIES S.A.C": {"ACORTADOR":"GMH"},
        "EXCELLENCE FRUIT S.A.C": {"ACORTADOR":"EXC"},
        "GAP BERRIES S.A.C": {"ACORTADOR":"GAP"},
        "BIG BERRIES S.A.C": {"ACORTADOR":"BIG"},
        "CANYON BERRIES S.A.C": {"ACORTADOR":"CAN"},
        "TARA FARMS S.A.C": {"ACORTADOR":"TAF"},
        "Q BERRIES S.A.C": {"ACORTADOR":"QBE"},
        "SAN EFISIO S.A.C": {"ACORTADOR":"SEF"},
        
    }
    dict_fundos_empresa ={
        "AGRICOLA BLUE GOLD S.A.C":{
            "FUNDO":{
                "VISTA HERMOSA":"VH",
                "CERRO VERDE":"CV",
                "SAN ANDRES":"SA",
                "EL MILAGRO":"EM"
            }
        },
        "GMH BERRIES S.A.C": {
            "FUNDO":{
                "LA ESPERANZA":"LE"
            }},
        "EXCELLENCE FRUIT S.A.C": {
            "FUNDO":{
                "SAN PEDRO":"SP",
                "SAN JOSE":"SJ",
            }
        },
        "GAP BERRIES S.A.C": {
            "FUNDO":{
                "GAP BERRIES S.A.C":"GB"
            }
        },
        "BIG BERRIES S.A.C": {
            "FUNDO":{
                "LA COLINA":"LC"
            }
        },
        "CANYON BERRIES S.A.C": {
            "FUNDO":{
                "EL POTRERO":"EP"
            }
        },
        "TARA FARMS S.A.C": {
            "FUNDO":{
                "LAS BRISAS":"LB"
            }
        },
        "Q BERRIES S.A.C": {
            "FUNDO":{
                "LICAPA":"LI"
            }
        },
        "SAN EFISIO S.A.C": {
            "FUNDO":{
                "SAN EFISIO":"SE"
            }
        }
    }
    col_header1,col_header2,col_header3  = st.columns([5,3,3])
    with col_header1:
        st.title("Generador de QR")
    with  col_header2:
        input_empresa = st.selectbox("EMPRESA",dict_resumen_empresa.keys())
    with col_header3:
        input_fundo = st.selectbox("FUNDO",dict_fundos_empresa[input_empresa]["FUNDO"].keys())
    
    btn = st.button("GENERAR QR ", type="primary", use_container_width=True)
    if btn:
        fecha_actual = datetime.now().strftime("%Y%m%d%H%M%S")
        
        empresa_ = dict_resumen_empresa[input_empresa]["ACORTADOR"]
        fundo_ = dict_fundos_empresa[input_empresa]["FUNDO"][input_fundo]
        concat_code = empresa_+fundo_+fecha_actual
        qr_img = generar_qr(concat_code)
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Centrar la imagen QR
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(img_buffer, width=450,use_column_width=False)
            st.markdown(f"<h2 style='text-align: center;'>{concat_code}</h2>", unsafe_allow_html=True)


"""
        with st.expander("PREVIEW DE DATOS",expanded=False):
                st.subheader("📋 Preview de Datos")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Información General:**")
                    st.write(f" **KEY QR:** {datos['key_qr']}")
                    st.write(f" **Cultivo:** {datos['cultivo']}")
                    st.write(f" **Tipo de Producto:** {datos['tipo_producto']}")
                    st.write(f" **Empresa:** {datos['empresa']}")
                    st.write(f" **Fundo:** {datos['fundo']}")
                    st.write(f" **Variedad:** {datos['variedad']}")
                    st.write(f" **Fecha:** {datos['fecha']}")
                
                with col2:
                    st.markdown("**Información de Transporte:**")
                    st.write(f" **Guía:** {datos['guia']}")
                    st.write(f" **Viaje:** {datos['viaje']}")
                    st.write(f" **N° Tarja:** {datos['num_tarja']}")
                    st.write(f" **N° Pallet:** {datos['num_pallet']}")
                    st.write(f" **N° Jabas:** {datos['num_jabas']}")
                    st.write(f" **N° Jarras:** {datos['num_jarras']}")
                
                # Información de pesos
                st.markdown("**⚖️ Información de Pesos:**")
                col_peso1, col_peso2, col_peso3 = st.columns(3)
                with col_peso1:
                    st.metric("Peso Bruto", f"{datos['peso_bruto']} kg")
                with col_peso2:
                    st.metric("Peso Campo", f"{datos['peso_campo']} kg")
                with col_peso3:
                    st.metric("Peso Neto", f"{datos['peso_neto']} kg", delta="Final")
        """  



















"""
# Mostrar el dataframe filtrado
        st.subheader("📊 Datos Filtrados")
        #st.dataframe(filtered_df, use_container_width=True)
        
        # Análisis básico
        st.subheader("📈 Análisis de Datos")
        
        # Estadísticas por fundo
        if 'FUNDO' in df.columns:
            st.write("**Distribución por Fundo:**")
            fundo_counts = df['FUNDO'].value_counts()
            st.bar_chart(fundo_counts)
        
        # Estadísticas por variedad
        if 'VARIEDAD' in df.columns:
            st.write("**Distribución por Variedad:**")
            variedad_counts = df['VARIEDAD'].value_counts()
            st.bar_chart(variedad_counts)
        
        # Estadísticas de pesos
        if 'KILOS NETO' in df.columns:
            col_peso1, col_peso2 = st.columns(2)
            with col_peso1:
                st.write("**Estadísticas de Kilos Neto:**")
                st.write(f"Promedio: {df['KILOS NETO'].mean():.2f} kg")
                st.write(f"Máximo: {df['KILOS NETO'].max():.2f} kg")
                st.write(f"Mínimo: {df['KILOS NETO'].min():.2f} kg")
            
            with col_peso2:
                st.write("**Estadísticas de Kilos Bruto:**")
                st.write(f"Promedio: {df['KILOS BRUTO'].mean():.2f} kg")
                st.write(f"Máximo: {df['KILOS BRUTO'].max():.2f} kg")
                st.write(f"Mínimo: {df['KILOS BRUTO'].min():.2f} kg")
"""