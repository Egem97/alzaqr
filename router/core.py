import streamlit as st

from views.tools import qrtool, dashboard




def pages():
    page_dict = {}
    page_dict["Qr Tool"] = [
        st.Page(page = qrtool,title="Qr Tool",icon = ":material/home:")
    ]
    page_dict["Dashboard"] = [
        st.Page(page = dashboard,title="Dashboard",icon = ":material/home:")
    ]
    return page_dict