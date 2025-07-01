import streamlit as st

from views.tools import qrtool, dashboard, qrgenerator
from views.prod import explorer_prod_excel




def pages():
    page_dict = {}
    page_dict["Qr Tool"] = [
        st.Page(page = qrtool,title="Qr Tool",icon = "📇"),
        st.Page(page = qrgenerator,title="Qr Generator",icon = "🛠️"),   
        st.Page(page = dashboard,title="Datos Agrupados",icon = "🔎") 
    ]
    page_dict["Producción"] = [
        st.Page(page = explorer_prod_excel,title="Explorer Data",icon = "📈")
    ]
    return page_dict