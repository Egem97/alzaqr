import re
import pandas as pd
import gspread
import streamlit as st
import time
from oauth2client.service_account import ServiceAccountCredentials

# Paso 1: Autenticación
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("nifty-might-269005-cd303aaaa33f.json", scope)
client = gspread.authorize(creds)

@st.cache_data(show_spinner="Cargando datos...",ttl=180)  # Cache se actualiza cada 3 minutos (180 segundos)
def read_sheet(key_sheet, sheet_name):
    try:
        spreadsheet = client.open_by_key(key_sheet)
        sheet = spreadsheet.worksheet(sheet_name)
        data = sheet.get_all_values()

        return data
    except Exception as e:
        return key_sheet, f"Error: {str(e)}"


def read_sheet_with_polling(key_sheet, sheet_name, refresh_interval=60):
    """
    Función que carga datos de Google Sheets con polling inteligente usando Session State.
    
    Args:
        key_sheet (str): ID de la hoja de Google Sheets
        sheet_name (str): Nombre de la hoja específica
        refresh_interval (int): Intervalo de actualización en segundos (default: 60)
    
    Returns:
        data: Datos de la hoja o mensaje de error
    """
    current_time = time.time()
    
    # Crear una clave única para este sheet específico
    cache_key = f"sheet_data_{key_sheet}_{sheet_name}"
    last_update_key = f"last_update_{key_sheet}_{sheet_name}"
    
    # Inicializar session state si no existe
    if cache_key not in st.session_state:
        st.session_state[cache_key] = None
        st.session_state[last_update_key] = 0
    
    # Verificar si necesitamos actualizar los datos
    time_since_update = current_time - st.session_state[last_update_key]
    
    if (st.session_state[cache_key] is None or 
        time_since_update > refresh_interval):
        
        # Mostrar indicador de carga solo en primera carga o cuando han pasado muchos minutos
        if st.session_state[cache_key] is None or time_since_update > 300:  # 5 minutos
            with st.spinner(f"Cargando datos de {sheet_name}..."):
                new_data = _fetch_sheet_data(key_sheet, sheet_name)
        else:
            # Actualización silenciosa en background
            new_data = _fetch_sheet_data(key_sheet, sheet_name)
        
        # Actualizar session state
        st.session_state[cache_key] = new_data
        st.session_state[last_update_key] = current_time
        
        # Opcional: mostrar mensaje de actualización
        if st.session_state[cache_key] is not None and time_since_update > 0:
            st.success(f"✅ Datos actualizados - {sheet_name}")
    
    return st.session_state[cache_key]


def _fetch_sheet_data(key_sheet, sheet_name):
    """
    Función auxiliar para cargar datos de Google Sheets.
    Separada para facilitar el manejo de errores y testing.
    """
    try:
        spreadsheet = client.open_by_key(key_sheet)
        sheet = spreadsheet.worksheet(sheet_name)
        data = sheet.get_all_values()
        return data
    except Exception as e:
        st.error(f"Error cargando {sheet_name}: {str(e)}")
        return None


def get_sheet_status(key_sheet, sheet_name):
    """
    Función auxiliar para obtener información sobre el estado del cache.
    Útil para debugging y monitoreo.
    """
    cache_key = f"sheet_data_{key_sheet}_{sheet_name}"
    last_update_key = f"last_update_{key_sheet}_{sheet_name}"
    
    if cache_key in st.session_state:
        last_update = st.session_state[last_update_key]
        current_time = time.time()
        time_since_update = current_time - last_update
        
        return {
            "has_data": st.session_state[cache_key] is not None,
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_update)),
            "seconds_since_update": int(time_since_update),
            "minutes_since_update": round(time_since_update / 60, 1)
        }
    return {"has_data": False, "last_update": "Never", "seconds_since_update": 0}


def clear_sheet_cache(key_sheet=None, sheet_name=None):
    """
    Función para limpiar manualmente el cache de polling.
    Si no se especifican parámetros, limpia todo el cache relacionado con sheets.
    """
    if key_sheet and sheet_name:
        # Limpiar cache específico
        cache_key = f"sheet_data_{key_sheet}_{sheet_name}"
        last_update_key = f"last_update_{key_sheet}_{sheet_name}"
        
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        if last_update_key in st.session_state:
            del st.session_state[last_update_key]
        
        st.success(f"Cache limpiado para {sheet_name}")
    else:
        # Limpiar todos los caches de sheets
        keys_to_remove = [key for key in st.session_state.keys() 
                         if key.startswith(("sheet_data_", "last_update_"))]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        st.success(f"Cache completo limpiado ({len(keys_to_remove)} items)")







