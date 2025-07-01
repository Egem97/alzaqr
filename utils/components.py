import streamlit as st
import pandas as pd
import numpy as np
from styles import styles
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode ,JsCode


def aggrid_builder(dataframe = pd.DataFrame(),columns_totales = []):
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    #gb.configure_pagination(enabled=True)
    #gb.configure_side_bar()
    #gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    #gb.configure_column("action", cellRenderer="agGroupCellRenderer", headerName="Action", width=100)
    cellstyle_last_row = JsCode(f"""
                function(params) {{
                    if (params.node.rowIndex === {len(dataframe) - 1}) {{
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
    for col in dataframe.columns:
        gb.configure_column(col, cellStyle=cellstyle_last_row)
    grid_options = gb.build()

    row_height = 35
    header_height = 35
    num_rows = len(dataframe)
    height = header_height + (num_rows * row_height)
    height = max(height, 120)  # Altura mínima

    return AgGrid(
        dataframe,
        gridOptions = grid_options,
        update_mode = 'MODEL_CHANGED',#GridUpdateMode.NO_UPDATE,
        height = height,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True
        #width = "100%",
        #theme = "light"
    )



def aggrid_builder_prod(dataframe = pd.DataFrame(),columns_totales = []):
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    #gb.configure_pagination(enabled=True)
    #gb.configure_side_bar()
    #gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    #gb.configure_column("action", cellRenderer="agGroupCellRenderer", headerName="Action", width=100)
    cellstyle_last_row = JsCode(f"""
                function(params) {{
                    if (params.node.rowIndex === {len(dataframe) - 1}) {{
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
    for col in dataframe.columns:
        gb.configure_column(col, cellStyle=cellstyle_last_row)
    grid_options = gb.build()

    row_height = 35
    header_height = 35
    num_rows = len(dataframe)
    min_height = 120
    max_height = 600
    height = min(max(header_height + (num_rows * row_height), min_height), max_height)

    return AgGrid(
        dataframe,
        gridOptions = grid_options,
        update_mode = 'MODEL_CHANGED',#GridUpdateMode.NO_UPDATE,
        height = height,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True
        #width = "100%",
        #theme = "light"
    )
