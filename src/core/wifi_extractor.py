"""
WiFi Profile Extractor - Core functionality.

This module contains the main logic for extracting WiFi profiles
from Windows systems using netsh commands.
"""

import logging
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from src.utils.system_utils import SystemUtils, CommandResult
from src.core.exceptions import (
    UnsupportedOperatingSystemError,
    NoWiFiProfilesFoundError,
    ProfileParsingError,
    InsufficientPrivilegesError
)
from src.config.settings import netsh_config


logger = logging.getLogger(__name__)


@dataclass
class WiFiProfile:
    """Represents a WiFi profile with all its properties."""
    
    ssid: str
    authentication: str = ""
    cipher: str = ""
    password: str = ""
    connection_type: str = ""
    cost: str = ""
    interface: str = ""
    security_key: str = ""
    key_type: str = ""
    
    # Metadata
    extraction_time: datetime = field(default_factory=datetime.now)
    has_password: bool = field(init=False)
    
    def __post_init__(self):
        """Post-initialization processing."""
        self.has_password = bool(self.password and self.password.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "ssid": self.ssid,
            "authentication": self.authentication,
            "cipher": self.cipher,
            "password": self.password,
            "connection_type": self.connection_type,
            "cost": self.cost,
            "interface": self.interface,
            "security_key": self.security_key,
            "key_type": self.key_type,
            "has_password": self.has_password,
            "extraction_time": self.extraction_time.isoformat()
        }
    
    def get_security_summary(self) -> str:
        """Get a summary of security configuration."""
        if not self.authentication and not self.cipher:
            return "Unknown"
        
        parts = []
        if self.authentication:
            parts.append(self.authentication)
        if self.cipher:
            parts.append(self.cipher)
        
        return " / ".join(parts)


class WiFiProfileExtractor:
    """Main WiFi profile extraction class."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.system_utils = SystemUtils()
        self.locale = self.system_utils.get_system_locale()
        self._field_mappings = netsh_config.FIELD_MAPPINGS
        self._profile_markers = self._get_profile_markers()
        
        logger.info(f"WiFi Profile Extractor initialized (locale: {self.locale})")
    
    def _get_profile_markers(self) -> List[str]:
        """Get profile markers for current system locale."""
        markers = []
        for lang_markers in netsh_config.PROFILE_MARKERS.values():
            markers.extend(lang_markers)
        return markers
    
    def extract_profiles(self, require_admin: bool = True) -> List[WiFiProfile]:
        """
        Extract all WiFi profiles from the system.
        
        Args:
            require_admin: Whether to require admin privileges
            
        Returns:
            List of WiFiProfile objects
            
        Raises:
            UnsupportedOperatingSystemError: If not running on Windows
            InsufficientPrivilegesError: If admin required but not available
            NoWiFiProfilesFoundError: If no profiles found
        """
        logger.info("Starting WiFi profile extraction")
        
        # Check system compatibility
        self.system_utils.check_windows_compatibility()
        
        # Get list of profile names
        profile_names = self._get_profile_names()
        
        if not profile_names:
            raise NoWiFiProfilesFoundError()
        
        logger.info(f"Found {len(profile_names)} WiFi profiles")
        
        # Extract detailed information for each profile
        profiles = []
        for ssid in profile_names:
            try:
                profile = self._extract_profile_details(ssid, require_admin)
                profiles.append(profile)
                logger.debug(f"Successfully extracted profile: {ssid}")
            except Exception as e:
                logger.warning(f"Failed to extract profile '{ssid}': {e}")
                # Create basic profile with error info
                error_profile = WiFiProfile(
                    ssid=ssid,
                    authentication="Error during extraction",
                    cipher=str(e)
                )
                profiles.append(error_profile)
        
        logger.info(f"Successfully extracted {len(profiles)} profiles")
        return profiles
    
    def _get_profile_names(self) -> List[str]:
        """
        Get list of WiFi profile names from system.
        
        Returns:
            List of SSID names
        """
        logger.debug("Retrieving WiFi profile names")
        
        result = self.system_utils.run_command(
            list(netsh_config.SHOW_PROFILES_CMD)
        )
        
        if not result.success:
            logger.error(f"Failed to get profiles: {result.stderr}")
            return []
        
        ssids = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if any(marker in line for marker in self._profile_markers):
                ssid = self.system_utils.parse_value_after_colon(line)
                if ssid:
                    ssids.append(ssid)
        
        return ssids
    
    def _extract_profile_details(self, ssid: str, require_admin: bool) -> WiFiProfile:
        """
        Extract detailed information for a specific profile.
        
        Args:
            ssid: Network SSID name
            require_admin: Whether admin privileges are required
            
        Returns:
            WiFiProfile object with detailed information
        """
        logger.debug(f"Extracting details for profile: {ssid}")
        
        # Build command
        command = ["netsh", "wlan", "show", "profile", f"name={ssid}", "key=clear"]
        
        try:
            result = self.system_utils.run_command(
                command,
                check_admin=require_admin
            )
        except InsufficientPrivilegesError:
            # Try without key=clear if admin not available
            logger.debug(f"Admin not available, trying without password for: {ssid}")
            command = ["netsh", "wlan", "show", "profile", f"name={ssid}"]
            result = self.system_utils.run_command(command)
        
        if not result.success:
            raise ProfileParsingError(ssid, result.stderr)
        
        # Parse the output
        return self._parse_profile_output(ssid, result.stdout)
    
    def _parse_profile_output(self, ssid: str, output: str) -> WiFiProfile:
        """
        Parse netsh output for a specific profile.
        
        Args:
            ssid: Network SSID
            output: Raw netsh command output
            
        Returns:
            Parsed WiFiProfile object
        """
        profile = WiFiProfile(ssid=ssid)
        
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            
            # Parse each field type
            for field_key, field_labels in self._field_mappings.items():
                if any(line.startswith(label) for label in field_labels):
                    value = self.system_utils.parse_value_after_colon(line)
                    self._set_profile_field(profile, field_key, value)
                    break
        
        return profile
    
    def _set_profile_field(self, profile: WiFiProfile, field_key: str, value: str) -> None:
        """Set a field value on the profile object."""
        field_mapping = {
            "auth": "authentication",
            "cipher": "cipher",
            "key": "password",
            "type": "connection_type",
            "cost": "cost",
            "interface": "interface"
        }
        
        if field_key in field_mapping:
            setattr(profile, field_mapping[field_key], value)
    
    def to_dataframe(self, profiles: List[WiFiProfile]) -> pd.DataFrame:
        """
        Convert list of profiles to pandas DataFrame.
        
        Args:
            profiles: List of WiFiProfile objects
            
        Returns:
            DataFrame with profile data
        """
        if not profiles:
            return pd.DataFrame()
        
        data = [profile.to_dict() for profile in profiles]
        df = pd.DataFrame(data)
        
        # Ensure all expected columns exist
        expected_columns = [
            "ssid", "authentication", "cipher", "password", 
            "connection_type", "cost", "interface", "has_password"
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ""
        
        return df
    
    def get_extraction_summary(self, profiles: List[WiFiProfile]) -> Dict[str, Any]:
        """
        Get summary statistics about extracted profiles.
        
        Args:
            profiles: List of extracted profiles
            
        Returns:
            Dictionary with summary information
        """
        total_profiles = len(profiles)
        profiles_with_passwords = sum(1 for p in profiles if p.has_password)
        profiles_without_passwords = total_profiles - profiles_with_passwords
        
        # Security type distribution
        auth_types = {}
        cipher_types = {}
        
        for profile in profiles:
            if profile.authentication:
                auth_types[profile.authentication] = auth_types.get(profile.authentication, 0) + 1
            if profile.cipher:
                cipher_types[profile.cipher] = cipher_types.get(profile.cipher, 0) + 1
        
        return {
            "total_profiles": total_profiles,
            "profiles_with_passwords": profiles_with_passwords,
            "profiles_without_passwords": profiles_without_passwords,
            "password_percentage": (profiles_with_passwords / total_profiles * 100) if total_profiles > 0 else 0,
            "authentication_types": auth_types,
            "cipher_types": cipher_types,
            "extraction_time": datetime.now().isoformat(),
            "system_locale": self.locale
        }