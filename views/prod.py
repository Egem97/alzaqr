import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime
from styles import styles
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode ,JsCode
from io import StringIO, BytesIO
from utils.helpers import crear_pdf, generar_qr
from utils.components import aggrid_builder,aggrid_builder_prod,aggrid_editing_prod
from utils.helpers import generar_qr


def explorer_prod_excel():
    styles(2)
    formatos_produccion_dff = pd.read_parquet("src/data/FORMATOS PRODUCCION.parquet")
    formatos_produccion_dff = formatos_produccion_dff[["DESCRIPCION","Detalles","PESO CAJA","SOBRE PESO"]]
    formatos_produccion_dff = formatos_produccion_dff.rename({"DESCRIPCION":"DESCRIPCION DEL PRODUCTO"},axis=1)
    #4.4OZ C/E SAN LUCAR UK ANUSAYA-A
    formatos_produccion_dff = pd.concat([formatos_produccion_dff,pd.DataFrame([{"DESCRIPCION DEL PRODUCTO":"4.4OZ C/E SAN LUCAR UK ANUSAYA-A","Detalles":240,"PESO CAJA":1.5,"SOBRE PESO":1.03}])])
    col_header1,col_header2 = st.columns([6,6])
    with col_header1:
        st.title("PRODUCTO TERMINADO")
    with col_header2:
        with st.expander("SUBIR ARCHIVO EXCEL",expanded=True):
            uploaded_file = st.file_uploader("Escoja su archivo excel", accept_multiple_files=False,type=['xlsx'],key="uploaded_file")
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file,sheet_name="BD")
        print(df.columns)
        df = df[df["F. PRODUCCION"].notna()]
        df["F. PRODUCCION"] = pd.to_datetime(df["F. PRODUCCION"]).dt.date
        df["CONTENEDOR"] = df["CONTENEDOR"].fillna("NO ESPECIFICADO")
        df["TIPO DE PALLET"] = df["TIPO DE PALLET"].fillna("NO ESPECIFICADO")
        df["OBSERVACIONES"] = df["OBSERVACIONES"].fillna("NO ESPECIFICADO")
        df["CLIENTE"] = df["CLIENTE"].fillna("NO ESPECIFICADO")
        df["DESCRIPCION DEL PRODUCTO"] = df["DESCRIPCION DEL PRODUCTO"].fillna("NO ESPECIFICADO")
        df["DESCRIPCION DEL PRODUCTO"] = df["DESCRIPCION DEL PRODUCTO"].str.strip()
        #with st.expander("Datos Originales",expanded=True):
        #    st.write(df.shape)
        #     st.dataframe(df)
        
        dff = df.groupby(["ENVIO","F. PRODUCCION","CLIENTE","CONTENEDOR","TIPO DE PALLET","DESCRIPCION DEL PRODUCTO",
        "DESTINO","FUNDO",'VARIEDAD',"OBSERVACIONES"]).agg({
            "Nº CAJAS":"sum","Nº DE PALLET":"count","KG EXPORTABLES":"sum"
        
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
                select_contenedor = st.selectbox("Contenedor",dff["CONTENEDOR"].unique(),key="contenedor",index=None,placeholder="Selecciona un contenedor")
                if select_contenedor != None:
                    dff = dff[dff["CONTENEDOR"] == select_contenedor]
        with col_r1_4:
                select_presentacion = st.selectbox("Presentación",dff["DESCRIPCION DEL PRODUCTO"].unique(),key="tipo_pallet",index=None,placeholder="Selecciona una presentación")
                if select_presentacion != None:
                    dff = dff[dff["DESCRIPCION DEL PRODUCTO"] == select_presentacion]
        #dff["F. PRODUCCION"] = pd.to_datetime(dff["F. PRODUCCION"])
        tab1, tab2,tab3 = st.tabs(["RESUMEN", "DASHBOARD","PROGRAMA DE EMPAQUE"])
        with tab1:
            table1_dff = dff.groupby(["CLIENTE","F. PRODUCCION","DESCRIPCION DEL PRODUCTO","FUNDO","VARIEDAD","OBSERVACIONES"]).agg({
                "Nº DE PALLET":"count","Nº CAJAS":"sum"
            }).reset_index()
            # Agregar fila total
            table1_dff["Nº DE PALLET"] = table1_dff["Nº DE PALLET"].astype(int)
            table1_dff = table1_dff.rename({"Nº DE PALLET":"Nº PALLETS"},axis=1)
            total_row = {col: '' for col in table1_dff.columns}
            total_row[table1_dff.columns[0]] = 'TOTAL'
            for col in ["Nº CAJAS","Nº PALLETS"]:
                total_row[col] = table1_dff[col].sum()
            table1_dff = pd.concat([table1_dff, pd.DataFrame([total_row])], ignore_index=True)

            st.subheader("Resumen PT")
           
            aggrid_builder_prod(table1_dff)
            st.subheader("Resumen Programa")
            table2_dff = dff.groupby(["CLIENTE","F. PRODUCCION","CONTENEDOR","DESCRIPCION DEL PRODUCTO","VARIEDAD",])[["Nº CAJAS"]].sum().reset_index()
            table2_dff["F. PRODUCCION"] = table2_dff["F. PRODUCCION"].astype(str)
            table2_pivot_dff = pd.pivot_table(
                    table2_dff,
                    values="Nº CAJAS",
                    index=["CLIENTE", "CONTENEDOR", "DESCRIPCION DEL PRODUCTO", "VARIEDAD"],
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
            ####################################################################
            
            
            
            #table3_dff["Nº DE PALLET"] = table3_dff["Nº DE PALLET"].astype(int)
            #table3_dff = table3_dff.rename({"Nº DE PALLET":"Nº PALLETS"},axis=1)
            #st.write(table3_dff.shape)

            ###################################################################
            
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
            LIST_VAR_NUM = ["Nº CAJAS","KG EXPORTABLES"]#,"KG EMPACADOS","KG EXPORTABLES "
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

            medida_contenedor_df = dff.groupby(["CONTENEDOR","CLIENTE"])[[select_tipo_var_num]].sum().reset_index()
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
                fig1= px.bar(medida_contenedor_df, x="CONTENEDOR", y=select_tipo_var_num, color="CLIENTE",
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
        with tab3:
            st.subheader("PROGRAMA DE EMPAQUE")
            table3_dff = dff.groupby(["ENVIO","CONTENEDOR","DESCRIPCION DEL PRODUCTO","VARIEDAD","F. PRODUCCION","DESTINO"]).agg({
                "Nº DE PALLET":"count","Nº CAJAS":"sum"
            }).reset_index()
            list_fechas = sorted(list(table3_dff["F. PRODUCCION"].unique()))
            list_fechas_str = [fecha.strftime('%Y-%m-%d') for fecha in list_fechas]
            table3_group_npallets_df = table3_dff.groupby(["ENVIO","CONTENEDOR","DESCRIPCION DEL PRODUCTO","VARIEDAD","DESTINO"]).agg({"Nº DE PALLET":"sum"}).reset_index()
            table3_group_npallets_df["STOCK"] = 0
            with st.expander("EDITOR DE STOCK",expanded=True):
                dataframe_aggrid = aggrid_editing_prod(table3_group_npallets_df)
            table3_pivot_dff = pd.pivot_table(
                    table3_dff,
                    values="Nº CAJAS",
                    index=["ENVIO","CONTENEDOR","DESCRIPCION DEL PRODUCTO","VARIEDAD", "DESTINO"],
                    columns="F. PRODUCCION",
                    aggfunc="sum",
                    fill_value=0,
            
            )
            table3_pivot_dff = table3_pivot_dff.reset_index()
            table3_pivot_dff.columns = [
                col.strftime('%d/%m/%Y') if isinstance(col, (pd.Timestamp, datetime, np.datetime64)) else str(col)
                for col in table3_pivot_dff.columns
            ]
            table3_pivot_dff = table3_pivot_dff.merge(dataframe_aggrid.data,on=["ENVIO","CONTENEDOR","DESCRIPCION DEL PRODUCTO","VARIEDAD","DESTINO"],how="left")
            table3_pivot_dff = table3_pivot_dff.merge(formatos_produccion_dff,on="DESCRIPCION DEL PRODUCTO",how="left")
            table3_pivot_dff["BALANCE"] = table3_pivot_dff["Nº DE PALLET"] * table3_pivot_dff["Detalles"]
            table3_pivot_dff["CAJAS FALTANTES"] = table3_pivot_dff[["STOCK"]+list_fechas_str].sum(axis=1)
            table3_pivot_dff["PALLETS FALTANTES"] = round(table3_pivot_dff["CAJAS FALTANTES"]/table3_pivot_dff["Detalles"],2)
            table3_pivot_dff["KG FALTANTES"] = table3_pivot_dff["CAJAS FALTANTES"] * table3_pivot_dff["PESO CAJA"]* table3_pivot_dff["SOBRE PESO"]
            table3_pivot_dff["ESTADO"] = table3_pivot_dff["PALLETS FALTANTES"].apply(lambda x: "COMPLETO" if x <= 0 else "EN PROCESO")
            #table3_pivot_dff = table3_pivot_dff.sort_values(by="ESTADO")
            table3_pivot_dff["MARKET"] = ""
            table3_pivot_dff["ENVIO"] = table3_pivot_dff["ENVIO"].replace({"MARITIMO":"M","AEREO":"A"})
            table3_pivot_dff["Detalles"] = (table3_pivot_dff["Detalles"].astype(str)+" CAJAS/PALLET")
            #print(table3_pivot_dff.columns)
            table3_pivot_dff = table3_pivot_dff[
                ['ENVIO', 'CONTENEDOR', 'DESCRIPCION DEL PRODUCTO', 'VARIEDAD','Nº DE PALLET','STOCK']+list_fechas_str+
                ['BALANCE','CAJAS FALTANTES','PALLETS FALTANTES','PESO CAJA','SOBRE PESO','KG FALTANTES','MARKET','DESTINO','Detalles','ESTADO' ]
            ]
            table3_pivot_dff.columns = ['ENVIO', 'FCL', 'DESCRIPCION', 'VARIEDAD','PHL','STOCK']+list_fechas_str+['BALANCE','CAJAS FALTANTES','PALLETS FALTANTES','PESO CAJA','SOBRE PESO','KG FALTANTES','MARKET','DESTINO','DETALLES','ESTADO' ]

            st.dataframe(table3_pivot_dff)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                table3_pivot_dff.to_excel(writer, sheet_name='PROGRAMA DE EMPAQUE', index=False)
                workbook  = writer.book
                worksheet1 = writer.sheets['PROGRAMA DE EMPAQUE']
                
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1})
                for worksheet, df in zip([worksheet1], [table3_pivot_dff]):
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    for i, col in enumerate(df.columns):
                        max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                        worksheet.set_column(i, i, max_len)
            processed_data = output.getvalue()
            st.download_button(
                label="Descargar Excel",
                data=processed_data,
                file_name="programa_empaque.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
def tunel_qr_enfiramiento():
    styles(2)
    st.title("🧊TUNEL QR ENFIRAMIENTO ")
    
     # 1 a 15

    #st.write("### Matriz de posiciones de almacenamiento (3 niveles x 15 columnas)")
    st.write("### CAMARA 1")
    with st.container(border=True):
        niveles = ['S', 'M', 'I']
        columnas = list(range(1, 16)) 
        for fila_idx, nivel in enumerate(niveles, start=1):
            cols = st.columns(len(columnas))
            for idx, col_num in enumerate(columnas):
                code = f"C1C({col_num}-{fila_idx}){nivel}"
                qr_img = generar_qr(code)
                img_buffer = BytesIO()
                qr_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                with cols[idx]:
                    st.image(img_buffer, width=80)
                    st.write(f"**{code}**")


"""

def explorer_prod_excel():
    styles(2)
    col_header1,col_header2 = st.columns([6,6])
    with col_header1:
        st.title("PHL-PT")
    with col_header2:
        with st.expander("SUBIR ARCHIVO EXCEL",expanded=True):
            uploaded_file = st.file_uploader("Escoja su archivo excel", accept_multiple_files=False,type=['xlsx'],key="uploaded_file")
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df = df[df["F. PRODUCCION"].notna()]
        df["F. PRODUCCION"] = pd.to_datetime(df["F. PRODUCCION"]).dt.date
        df["CONTENEDOR"] = df["CONTENEDOR"].fillna("NO ESPECIFICADO")
        df["TIPO DE PALLET"] = df["TIPO DE PALLET"].fillna("NO ESPECIFICADO")
        df["OBSERVACIONES"] = df["OBSERVACIONES"].fillna("NO ESPECIFICADO")
        df["CLIENTE"] = df["CLIENTE"].fillna("NO ESPECIFICADO")
        df["DESCRIPCION DEL PRODUCTO"] = df["DESCRIPCION DEL PRODUCTO"].fillna("NO ESPECIFICADO")
        #with st.expander("Datos Originales",expanded=True):
        #    st.write(df.shape)
        #     st.dataframe(df)
        
        dff = df.groupby(["F. PRODUCCION","CLIENTE","CONTENEDOR","TIPO DE PALLET","DESCRIPCION DEL PRODUCTO",
        "DESTINO","FUNDO",'VARIEDAD',"OBSERVACIONES"]).agg({
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
"""


