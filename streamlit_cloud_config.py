"""
Configuración para despliegue en Streamlit Cloud (versión demo).
"""

# Para Streamlit Cloud, crea estos archivos:

# .streamlit/config.toml
STREAMLIT_CONFIG = """
[server]
headless = true
port = 8501

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""

# Para simular datos en la nube, modifica wifi_extractor.py:
DEMO_MODE_CODE = '''
def get_demo_profiles():
    """Datos de demostración para Streamlit Cloud."""
    return [
        {
            "ssid": "MiWiFi_Demo",
            "authentication": "WPA2-Personal", 
            "cipher": "CCMP",
            "password": "password123",
            "has_password": True
        },
        {
            "ssid": "GuestNetwork_Demo",
            "authentication": "Open",
            "cipher": "None", 
            "password": "",
            "has_password": False
        }
    ]
'''

print("Para Streamlit Cloud:")
print("1. Crea .streamlit/config.toml con la configuración de arriba")
print("2. Modifica wifi_extractor.py para usar datos demo en Linux")
print("3. Conecta tu repo GitHub a Streamlit Cloud")
print("4. Deploy desde: https://share.streamlit.io/")