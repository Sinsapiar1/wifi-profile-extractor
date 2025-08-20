"""
Script para crear ejecutable standalone de WiFi Profile Extractor.
"""

import subprocess
import sys
from pathlib import Path

def create_executable():
    """Crear ejecutable usando PyInstaller."""
    
    # Instalar PyInstaller si no está instalado
    try:
        import PyInstaller
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Comando para crear ejecutable
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "WiFiProfileExtractor",
        "--icon", "assets/icon.ico",  # Si tienes un icono
        "--add-data", "src;src",
        "--hidden-import", "streamlit",
        "--hidden-import", "pandas",
        "--hidden-import", "openpyxl",
        "src/app.py"
    ]
    
    print("Creando ejecutable...")
    subprocess.run(cmd)
    print("✅ Ejecutable creado en dist/WiFiProfileExtractor.exe")

if __name__ == "__main__":
    create_executable()