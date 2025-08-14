import requests
import time
import pandas as pd
import io
from pathlib import Path
from utils.get_token import get_access_token


def listar_archivos_en_carpeta_compartida(access_token: str  ,drive_id: str, item_id: str):
    """
    Lista los archivos dentro de una carpeta compartida en OneDrive / SharePoint usando Microsoft Graph.

    :param access_token: Token de acceso válido con permisos Files.Read.All
    :param drive_id: El ID del drive compartido
    :param item_id: El ID de la carpeta compartida
    :return: Lista de archivos o carpetas dentro de esa carpeta
    """
    
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/children"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print("❌ Error al obtener archivos:", response.status_code)
        print(response.json())
        return []

def get_download_url_by_name(json_data, name):
    """
    Busca en el JSON un archivo por su nombre y retorna su downloadUrl
    
    Args:
        json_data (list): Lista de diccionarios con información de archivos
        name (str): Nombre del archivo a buscar
    
    Returns:
        str: URL de descarga del archivo encontrado, o None si no se encuentra
    """
    for item in json_data:
        if item.get('name') == name:
            return item.get('@microsoft.graph.downloadUrl')