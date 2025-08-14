import streamlit as st

from views.tools import qrtool, dashboard, qrgenerator
from views.prod import explorer_prod_excel, tunel_qr_enfiramiento
from views.despacho import packing_list
from views.gestion_humana import gestion_humana_packing




def pages():
    page_dict = {}
    page_dict["Recepción"] = [
        st.Page(page = qrtool,title="Qr Tool",icon = "📇"),
        st.Page(page = qrgenerator,title="Qr Generator",icon = "🛠️"),   
        st.Page(page = dashboard,title="Datos Agrupados",icon = "🔎") 
    ]
    page_dict["Producción"] = [
        st.Page(page = explorer_prod_excel,title="Explorer Data",icon = "📈"),
        
    ]
    page_dict["Despacho"] = [
        st.Page(page = packing_list,title="Packing List",icon = "📄"),
        st.Page(page = tunel_qr_enfiramiento,title="Tunel QR Enfiramiento",icon = "🧊")
    ]
    page_dict["Gestión Humana"] = [
        st.Page(page = gestion_humana_packing,title="Gestión Humana",icon = "👥")
    ]
    return page_dict