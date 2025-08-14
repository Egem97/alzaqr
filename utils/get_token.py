import requests
from typing import Optional
from utils.config import load_config



# Cargar configuración al inicializar el módulo
config = load_config()

def get_access_token() -> Optional[str]:
    """
    Obtiene el token de acceso para Microsoft Graph API
    """
    if not config:
        print("Error: No se pudo cargar la configuración")
        return None
    
    AUTHORITY = f"https://login.microsoftonline.com/{config['microsoft_graph']['tenant_id']}/oauth2/v2.0/token"
    try:
        response = requests.post(AUTHORITY, data={
            "grant_type": "client_credentials",
            "client_id": config['microsoft_graph']['client_id'],
            "client_secret": config['microsoft_graph']['client_secret'],
            "scope": "https://graph.microsoft.com/.default"
        })
        
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get("access_token")
            
            if access_token:
                print("Token de acceso obtenido exitosamente")
                return access_token
            else:
                print("Error: No se pudo obtener el token de acceso")
                return None
        else:
            print(f"Error HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error al obtener el token: {e}")
        return None