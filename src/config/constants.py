"""
Constants for WiFi Profile Extractor.
"""

# Application constants
DEFAULT_EXPORT_FILENAME = "wifi_profiles"
SUPPORTED_EXPORT_FORMATS = ["csv", "json", "xlsx"]

# System constants
WINDOWS_OS_NAMES = ["windows", "nt"]
REQUIRED_PRIVILEGE_LEVEL = "admin"

# UI constants
MAX_PROFILES_DISPLAY = 1000
REFRESH_COOLDOWN_SECONDS = 5
PASSWORD_REVEAL_WARNING = "⚠️ Passwords will be visible in plain text"

# Netsh command constants
NETSH_EXECUTABLE = "netsh"
WLAN_COMMAND = "wlan"
SHOW_PROFILES_SUBCOMMAND = "show profiles"
SHOW_PROFILE_SUBCOMMAND = "show profile"
KEY_CLEAR_OPTION = "key=clear"

# Error messages
ERROR_UNSUPPORTED_OS = "This application only supports Windows operating systems."
ERROR_NO_PRIVILEGES = "Administrator privileges required to access WiFi passwords."
ERROR_NO_PROFILES = "No WiFi profiles found on this system."
ERROR_COMMAND_FAILED = "Failed to execute netsh command."

# Success messages
SUCCESS_PROFILES_LOADED = "WiFi profiles loaded successfully."
SUCCESS_EXPORT_COMPLETED = "Export completed successfully."

# File extensions
CSV_EXTENSION = ".csv"
JSON_EXTENSION = ".json"
XLSX_EXTENSION = ".xlsx"