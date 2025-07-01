import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from styles import styles
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode ,JsCode
from io import StringIO, BytesIO
from utils.helpers import crear_pdf, generar_qr
from utils.components import aggrid_builder,aggrid_builder_prod



def explorer_prod_excel():
    styles(2)
    col_header1,col_header2 = st.columns([6,6])
    with col_header1:
        st.title("PHL-PT")
    with col_header2:
        with st.expander("SUBIR ARCHIVO EXCEL",expanded=True):
            uploaded_file = st.file_uploader("Escoja su archivo excel", accept_multiple_files=False,type=['xlsx','xlsm'],key="uploaded_file")
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file,sheet_name="TD-DATOS PT")
        df = df[df["F. PRODUCCION"].notna()]
        df["F. PRODUCCION"] = pd.to_datetime(df["F. PRODUCCION"]).dt.date
        df["CONTENERDOR"] = df["CONTENERDOR"].fillna("NO ESPECIFICADO")
        df["TIPO DE PALLET"] = df["TIPO DE PALLET"].fillna("NO ESPECIFICADO")
        df["OBS"] = df["OBS"].fillna("NO ESPECIFICADO")
        df["CLIENTE"] = df["CLIENTE"].fillna("NO ESPECIFICADO")
        df["DESCRIPCION DEL PRODUCTO"] = df["DESCRIPCION DEL PRODUCTO"].fillna("NO ESPECIFICADO")
        #with st.expander("Datos Originales",expanded=True):
        #    st.write(df.shape)
        #     st.dataframe(df)
        
        dff = df.groupby(["F. PRODUCCION","CLIENTE","CONTENERDOR","TIPO DE PALLET","DESCRIPCION DEL PRODUCTO",
        "DESTINO","FUNDO",'VARIEDAD',"OBS"]).agg({
            "Nº CAJAS":"sum","Nº DE PALLET":"count","KG EXPORTABLES ":"sum","KG EMPACADOS":"sum"
        
        }).reset_index()
        
        
        col_r1_1,col_r1_2,col_r1_3,col_r1_4 = st.columns(4)
        with col_r1_1:
                select_f_prod = st.selectbox("Fecha Producción",dff["F. PRODUCCION"].unique(),key="f_prod",index=None,placeholder="Selecciona una fecha")
                if select_f_prod != None:
                    dff = dff[dff["F. PRODUCCION"] == select_f_prod]
            
        with col_r1_2:
                select_cliente = st.selectbox("Empresa",dff["CLIENTE"].unique(),key="cliente",index=None,placeholder="Selecciona una empresa")
                if select_cliente != None:
                    dff = dff[dff["CLIENTE"] == select_cliente]
        with col_r1_3:
                select_contenedor = st.selectbox("Contenedor",dff["CONTENERDOR"].unique(),key="contenedor",index=None,placeholder="Selecciona un contenedor")
                if select_contenedor != None:
                    dff = dff[dff["CONTENERDOR"] == select_contenedor]
        with col_r1_4:
                select_presentacion = st.selectbox("Presentación",dff["DESCRIPCION DEL PRODUCTO"].unique(),key="tipo_pallet",index=None,placeholder="Selecciona una presentación")
                if select_presentacion != None:
                    dff = dff[dff["DESCRIPCION DEL PRODUCTO"] == select_presentacion]
        #dff["F. PRODUCCION"] = pd.to_datetime(dff["F. PRODUCCION"])
        tab1, tab2 = st.tabs(["RESUMEN", "DASHBOARD",])
        with tab1:
            table1_dff = dff.groupby(["CLIENTE","F. PRODUCCION","DESCRIPCION DEL PRODUCTO","FUNDO","VARIEDAD","OBS"])[[
                "Nº CAJAS","KG EMPACADOS","KG EXPORTABLES "
            ]].sum().reset_index()
            # Agregar fila total
            total_row = {col: '' for col in table1_dff.columns}
            total_row[table1_dff.columns[0]] = 'TOTAL'
            for col in ["Nº CAJAS","KG EMPACADOS","KG EXPORTABLES "]:
                total_row[col] = table1_dff[col].sum()
            table1_dff = pd.concat([table1_dff, pd.DataFrame([total_row])], ignore_index=True)

            st.subheader("Resumen PT")
            aggrid_builder_prod(table1_dff)
            st.subheader("Resumen Programa")
            table2_dff = dff.groupby(["CLIENTE","F. PRODUCCION","CONTENERDOR","DESCRIPCION DEL PRODUCTO","VARIEDAD",])[["Nº CAJAS"]].sum().reset_index()
            table2_dff["F. PRODUCCION"] = table2_dff["F. PRODUCCION"].astype(str)
            table2_pivot_dff = pd.pivot_table(
                    table2_dff,
                    values="Nº CAJAS",
                    index=["CLIENTE", "CONTENERDOR", "DESCRIPCION DEL PRODUCTO", "VARIEDAD"],
                    columns="F. PRODUCCION",
                    aggfunc="sum",
                    fill_value=0,
            
            )
            table2_pivot_dff = table2_pivot_dff.reset_index()

            # Agregar columna TOTAL sumando las columnas de fechas
            fecha_cols = [col for col in table2_pivot_dff.columns if pd.api.types.is_numeric_dtype(table2_pivot_dff[col])]
            table2_pivot_dff['TOTAL'] = table2_pivot_dff[fecha_cols].sum(axis=1)

            # Agregar fila total
            total_row = {col: '' for col in table2_pivot_dff.columns}
            total_row[table2_pivot_dff.columns[0]] = 'TOTAL'
            for col in table2_pivot_dff.columns:
                if pd.api.types.is_numeric_dtype(table2_pivot_dff[col]):
                    total_row[col] = table2_pivot_dff[col].sum()
            table2_pivot_dff = pd.concat([table2_pivot_dff, pd.DataFrame([total_row])], ignore_index=True)
            #print(table2_pivot_dff.columns)
            #st.dataframe(table2_pivot_dff)
            aggrid_builder_prod(table2_pivot_dff)

            # Exportar ambos DataFrames a un Excel con formato agradable
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                table1_dff.to_excel(writer, sheet_name='Resumen PT', index=False)
                table2_pivot_dff.to_excel(writer, sheet_name='Resumen Programa', index=False)
                workbook  = writer.book
                worksheet1 = writer.sheets['Resumen PT']
                worksheet2 = writer.sheets['Resumen Programa']
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1})
                for worksheet, df in zip([worksheet1, worksheet2], [table1_dff, table2_pivot_dff]):
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    for i, col in enumerate(df.columns):
                        max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                        worksheet.set_column(i, i, max_len)
            processed_data = output.getvalue()
            st.download_button(
                label="Descargar Excel",
                data=processed_data,
                file_name="resumenes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with tab2:
            LIST_VAR_NUM = ["Nº CAJAS","KG EMPACADOS","KG EXPORTABLES "]
            col_header1,col_header2 = st.columns([6,6])
            with col_header1:
                st.subheader("DASHBOARD")
            with col_header2:
                select_tipo_var_num = st.selectbox("MEDIDA",LIST_VAR_NUM,key="tipo_var_num",placeholder="Selecciona una medida")
            
            
            #####
            medida_seriet_df = dff.groupby(["F. PRODUCCION"])[[select_tipo_var_num]].sum().reset_index()
            medida_seriet_df = medida_seriet_df.sort_values(by="F. PRODUCCION",ascending=True)
            medida_seriet_df[select_tipo_var_num] = medida_seriet_df[select_tipo_var_num].round(1)
            
            ####

            medida_contenedor_df = dff.groupby(["CONTENERDOR","CLIENTE"])[[select_tipo_var_num]].sum().reset_index()
            medida_contenedor_df[select_tipo_var_num] = medida_contenedor_df[select_tipo_var_num].round(1)
            #########################
            medida_producto_df = dff.groupby(["DESCRIPCION DEL PRODUCTO"])[[select_tipo_var_num]].sum().reset_index()
            medida_producto_df[select_tipo_var_num] = medida_producto_df[select_tipo_var_num].round(1)
            medida_producto_df= medida_producto_df.rename({"DESCRIPCION DEL PRODUCTO":"PRESENTACION"},axis=1)
            medida_producto_df = medida_producto_df.sort_values(by=select_tipo_var_num,ascending=True)


            ######################
            medida_fundo_df = dff.groupby(["CLIENTE","FUNDO"])[[select_tipo_var_num]].sum().reset_index()
            medida_fundo_df[select_tipo_var_num] = medida_fundo_df[select_tipo_var_num].round(1)
            medida_fundo_df = medida_fundo_df.sort_values(by=select_tipo_var_num,ascending=True)




            #########################
            col1,col2 = st.columns(2)
            with col1:
                fig1= px.bar(medida_contenedor_df, x="CONTENERDOR", y=select_tipo_var_num, color="CLIENTE",
                             title=f'Contenedores - {select_tipo_var_num}',text=select_tipo_var_num)
                fig1.update_traces(textposition='outside')
                fig1.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
                st.plotly_chart(fig1)
                
            with col2:
                fig = px.line(medida_seriet_df, x="F. PRODUCCION", y=select_tipo_var_num,title=f'Serie de Tiempo Fecha Producción - {select_tipo_var_num}', markers=True)
                
                st.plotly_chart(fig)
            col3,col4 = st.columns(2)
            with col3:
                
                fig2= px.bar(medida_producto_df, x=select_tipo_var_num, y="PRESENTACION",
                             title=f'Presentaciones - {select_tipo_var_num}',text=select_tipo_var_num,orientation="h")
                fig2.update_traces(textposition='outside')
                fig2.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
                st.plotly_chart(fig2)
            with col4:
                fig3= px.bar(medida_fundo_df, x="FUNDO", y=select_tipo_var_num ,
                             title=f'Fundo - {select_tipo_var_num}',text=select_tipo_var_num,color="CLIENTE")
                fig3.update_traces(textposition='outside')
                fig3.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
                st.plotly_chart(fig3)




