"""
System utilities for WiFi Profile Extractor.

This module provides system-level utilities for OS detection,
command execution, and privilege checking.
"""

import ctypes
import platform
import subprocess
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

from src.core.exceptions import (
    UnsupportedOperatingSystemError,
    NetshCommandError,
    InsufficientPrivilegesError
)
from src.config.settings import netsh_config


logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command execution."""
    
    command: str
    return_code: int
    stdout: str
    stderr: str
    success: bool
    
    @property
    def output(self) -> str:
        """Get the primary output (stdout if successful, stderr if failed)."""
        return self.stdout if self.success else self.stderr


class SystemUtils:
    """System utility functions."""
    
    @staticmethod
    def get_os_info() -> Tuple[str, str, str]:
        """
        Get operating system information.
        
        Returns:
            Tuple containing (system, release, version)
        """
        return (
            platform.system(),
            platform.release(),
            platform.version()
        )
    
    @staticmethod
    def is_windows() -> bool:
        """Check if the current OS is Windows."""
        return platform.system().lower() == "windows"
    
    @staticmethod
    def check_windows_compatibility() -> None:
        """
        Check if the current system is compatible (Windows).
        
        Raises:
            UnsupportedOperatingSystemError: If not running on Windows
        """
        if not SystemUtils.is_windows():
            current_os = platform.system()
            raise UnsupportedOperatingSystemError(current_os)
    
    @staticmethod
    def is_admin() -> bool:
        """
        Check if the current process has administrator privileges.
        
        Returns:
            True if running as administrator, False otherwise
        """
        if not SystemUtils.is_windows():
            return False
            
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            logger.warning(f"Could not check admin privileges: {e}")
            return False
    
    @staticmethod
    def run_command(
        command: List[str],
        timeout: Optional[int] = None,
        check_admin: bool = False
    ) -> CommandResult:
        """
        Execute a system command safely.
        
        Args:
            command: List of command parts
            timeout: Command timeout in seconds
            check_admin: Whether to check admin privileges before execution
            
        Returns:
            CommandResult object with execution details
            
        Raises:
            InsufficientPrivilegesError: If admin required but not available
            NetshCommandError: If command execution fails
        """
        if check_admin and not SystemUtils.is_admin():
            raise InsufficientPrivilegesError()
        
        command_str = " ".join(command)
        timeout = timeout or netsh_config.COMMAND_TIMEOUT
        
        logger.debug(f"Executing command: {command_str}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=False,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'  # Handle encoding issues gracefully
            )
            
            success = result.returncode == 0
            
            if not success:
                logger.warning(f"Command failed: {command_str}, Return code: {result.returncode}")
            
            return CommandResult(
                command=command_str,
                return_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                success=success
            )
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            logger.error(f"{error_msg}: {command_str}")
            raise NetshCommandError(command_str, -1, error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error executing command: {str(e)}"
            logger.error(f"{error_msg}: {command_str}")
            raise NetshCommandError(command_str, -1, error_msg)
    
    @staticmethod
    def parse_value_after_colon(line: str) -> str:
        """
        Parse value after colon in netsh output.
        
        Args:
            line: Line of text to parse
            
        Returns:
            Parsed value or original line if no colon found
        """
        if ":" in line:
            return line.split(":", 1)[1].strip()
        return line.strip()
    
    @staticmethod
    def get_system_locale() -> str:
        """
        Get system locale to determine language for netsh output.
        
        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            import locale
            lang = locale.getdefaultlocale()[0]
            if lang:
                return lang.split('_')[0].lower()
            return 'en'  # Default to English
        except Exception:
            logger.warning("Could not determine system locale, defaulting to English")
            return 'en'


class PrivilegeManager:
    """Manage and check system privileges."""
    
    @staticmethod
    def request_elevation() -> bool:
        """
        Request elevation to administrator privileges.
        
        Note: This is informational only. The user must manually
        restart the application as administrator.
        
        Returns:
            False (elevation must be done manually)
        """
        logger.info("Administrator privileges required. Please restart as administrator.")
        return False
    
    @staticmethod
    def get_privilege_status() -> dict:
        """
        Get comprehensive privilege status information.
        
        Returns:
            Dictionary with privilege information
        """
        is_admin = SystemUtils.is_admin()
        
        return {
            "is_admin": is_admin,
            "can_access_passwords": is_admin,
            "os_compatible": SystemUtils.is_windows(),
            "recommendations": SystemUtils._get_privilege_recommendations(is_admin)
        }
    
    @staticmethod
    def _get_privilege_recommendations(is_admin: bool) -> List[str]:
        """Get recommendations based on current privilege level."""
        if is_admin:
            return ["All features available"]
        
        return [
            "Run as Administrator to view WiFi passwords",
            "Right-click on Command Prompt and select 'Run as administrator'",
            "Then execute: streamlit run app.py"
        ]