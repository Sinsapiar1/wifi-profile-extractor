"""
Configuration settings for WiFi Profile Extractor.
"""

import os
from typing import Dict, List
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    APP_NAME: str = "WiFi Profile Extractor"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Professional WiFi profile extraction and management tool for Windows"
    PAGE_TITLE: str = "WiFi Profile Manager"
    PAGE_ICON: str = "🔐"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    MASK_PASSWORDS_DEFAULT: bool = True
    PASSWORD_MASK: str = "••••••••"
    SEARCH_PLACEHOLDER: str = "Search SSID..."
    SUPPORTED_FORMATS: List[str] = field(default_factory=lambda: ["CSV", "JSON", "XLSX"])

@dataclass
class NetshConfig:
    COMMAND_TIMEOUT: int = 30
    SHOW_PROFILES_CMD: List[str] = field(default_factory=lambda: ["netsh", "wlan", "show", "profiles"])
    PROFILE_MARKERS: Dict[str, List[str]] = field(default_factory=lambda: {
        "en": ["All User Profile"],
        "es": ["Perfil de todos los usuarios"]
    })
    FIELD_MAPPINGS: Dict[str, List[str]] = field(default_factory=lambda: {
        "auth": ["Authentication", "Autenticación"],
        "cipher": ["Cipher", "Cifrado"],
        "key": ["Key Content", "Contenido de la clave"],
        "type": ["Type", "Tipo"],
        "cost": ["Cost", "Costo"],
        "interface": ["Interface name", "Nombre de la interfaz"]
    })

app_config = AppConfig()
netsh_config = NetshConfig()
