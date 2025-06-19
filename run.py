
import subprocess
import os
import sys
def run_streamlit():
    script_path = os.path.join(os.path.dirname(__file__), "app_streamlit.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])
if __name__ == "__main__":
    run_streamlit()
"""
def run_streamlit():
    script_path = os.path.join(os.path.dirname(__file__), "app_streamlit.py")

    subprocess.run(["streamlit", "run", script_path])

import streamlit.web.bootstrap as bootstrap

if __name__ == "__main__":
    # Obtener la ruta del directorio actual
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Configurar la ruta del script de Streamlit
    script_path = os.path.join(dir_path, "app_streamlit.py")
    
    # Configurar argumentos
    sys.argv = ["streamlit", "run", script_path]
    
    # Ejecutar Streamlit
    bootstrap.run(script_path, "", [], {})
"""

