"""
Validation utilities for WiFi Profile Extractor.
"""

import re
import os
import platform
from typing import List, Optional, Dict, Any
from pathlib import Path

from src.core.exceptions import (
    UnsupportedOperatingSystemError,
    WiFiExtractorBaseException
)
from src.config.constants import WINDOWS_OS_NAMES, SUPPORTED_EXPORT_FORMATS


class SystemValidator:
    """Validates system requirements and compatibility."""
    
    @staticmethod
    def validate_operating_system() -> bool:
        """
        Validate that the current OS is supported (Windows).
        
        Returns:
            bool: True if OS is supported
            
        Raises:
            UnsupportedOperatingSystemError: If OS is not Windows
        """
        current_os = platform.system().lower()
        if current_os not in WINDOWS_OS_NAMES:
            raise UnsupportedOperatingSystemError(current_os)
        return True
    
    @staticmethod
    def validate_netsh_availability() -> bool:
        """
        Check if netsh command is available on the system.
        
        Returns:
            bool: True if netsh is available
        """
        try:
            import subprocess
            result = subprocess.run(
                ["netsh", "/?"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False


class DataValidator:
    """Validates data integrity and format."""
    
    @staticmethod
    def validate_ssid(ssid: str) -> bool:
        """
        Validate SSID format and length.
        
        Args:
            ssid: The SSID to validate
            
        Returns:
            bool: True if valid SSID
        """
        if not ssid or not isinstance(ssid, str):
            return False
        
        # SSID should be 1-32 characters
        if len(ssid) < 1 or len(ssid) > 32:
            return False
        
        # Check for invalid characters (control characters)
        if any(ord(char) < 32 for char in ssid):
            return False
        
        return True
    
    @staticmethod
    def validate_export_format(format_type: str) -> bool:
        """
        Validate export format type.
        
        Args:
            format_type: The format to validate
            
        Returns:
            bool: True if format is supported
        """
        return format_type.lower() in SUPPORTED_EXPORT_FORMATS
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Validate file path for export.
        
        Args:
            file_path: The file path to validate
            
        Returns:
            bool: True if path is valid
        """
        try:
            path = Path(file_path)
            # Check if parent directory exists or can be created
            parent_dir = path.parent
            return parent_dir.exists() or parent_dir == Path('.')
        except (OSError, ValueError):
            return False


class ProfileValidator:
    """Validates WiFi profile data."""
    
    @staticmethod
    def validate_profile_data(profile_data: Dict[str, Any]) -> bool:
        """
        Validate WiFi profile data structure.
        
        Args:
            profile_data: Dictionary containing profile data
            
        Returns:
            bool: True if profile data is valid
        """
        required_fields = ["ssid", "authentication", "cipher"]
        
        if not isinstance(profile_data, dict):
            return False
        
        # Check required fields
        for field in required_fields:
            if field not in profile_data:
                return False
            if not profile_data[field]:
                return False
        
        # Validate SSID
        if not DataValidator.validate_ssid(profile_data["ssid"]):
            return False
        
        return True
    
    @staticmethod
    def sanitize_profile_name(profile_name: str) -> str:
        """
        Sanitize profile name for safe usage.
        
        Args:
            profile_name: The profile name to sanitize
            
        Returns:
            str: Sanitized profile name
        """
        if not profile_name:
            return "Unknown_Profile"
        
        # Remove or replace invalid filename characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', profile_name)
        
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')
        
        # Ensure it's not empty after sanitization
        return sanitized if sanitized else "Unknown_Profile"


class InputValidator:
    """Validates user input and parameters."""
    
    @staticmethod
    def validate_search_query(query: str) -> bool:
        """
        Validate search query format.
        
        Args:
            query: The search query to validate
            
        Returns:
            bool: True if query is valid
        """
        if not query or not isinstance(query, str):
            return False
        
        # Basic length check
        if len(query.strip()) < 1 or len(query) > 100:
            return False
        
        return True
    
    @staticmethod
    def validate_filter_criteria(criteria: Dict[str, Any]) -> bool:
        """
        Validate filter criteria structure.
        
        Args:
            criteria: Dictionary containing filter criteria
            
        Returns:
            bool: True if criteria is valid
        """
        if not isinstance(criteria, dict):
            return False
        
        valid_keys = ["ssid", "authentication", "cipher", "has_password"]
        
        # Check that all keys are valid
        for key in criteria.keys():
            if key not in valid_keys:
                return False
        
        return True