"""
Custom exceptions for WiFi Profile Extractor.

This module defines custom exceptions used throughout the application
to provide better error handling and user feedback.
"""

from typing import Optional


class WiFiExtractorBaseException(Exception):
    """Base exception for all WiFi extractor related errors."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class UnsupportedOperatingSystemError(WiFiExtractorBaseException):
    """Raised when the application is run on an unsupported OS."""
    
    def __init__(self, current_os: str):
        message = f"This application only supports Windows. Current OS: {current_os}"
        super().__init__(message)


class NetshCommandError(WiFiExtractorBaseException):
    """Raised when netsh command execution fails."""
    
    def __init__(self, command: str, return_code: int, stderr: str):
        message = f"Netsh command failed: {command}"
        details = f"Return code: {return_code}, Error: {stderr}"
        super().__init__(message, details)


class InsufficientPrivilegesError(WiFiExtractorBaseException):
    """Raised when the application lacks necessary privileges."""
    
    def __init__(self):
        message = "Insufficient privileges to access WiFi passwords. Run as Administrator."
        super().__init__(message)


class NoWiFiProfilesFoundError(WiFiExtractorBaseException):
    """Raised when no WiFi profiles are found on the system."""
    
    def __init__(self):
        message = "No WiFi profiles found on this system."
        super().__init__(message)


class ProfileParsingError(WiFiExtractorBaseException):
    """Raised when profile data cannot be parsed correctly."""
    
    def __init__(self, profile_name: str, parsing_error: str):
        message = f"Failed to parse profile '{profile_name}'"
        super().__init__(message, parsing_error)