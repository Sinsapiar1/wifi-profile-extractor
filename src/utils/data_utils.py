"""
Data utilities for WiFi Profile Extractor.

This module provides utilities for data processing, export,
and formatting operations.
"""

import io
import json
import csv
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path

import pandas as pd

from utils.system_utils import SystemUtils  
from core.exceptions import WiFiExtractorBaseException
from config.settings import app_config


logger = logging.getLogger(__name__)


class DataExporter:
    """Handle data export in various formats."""
    
    @staticmethod
    def to_csv(
        df: pd.DataFrame,
        include_metadata: bool = True,
        mask_passwords: bool = False
    ) -> str:
        """
        Export DataFrame to CSV format.
        
        Args:
            df: DataFrame to export
            include_metadata: Whether to include metadata header
            mask_passwords: Whether to mask password fields
            
        Returns:
            CSV data as string
        """
        if df.empty:
            return "No data to export"
        
        # Prepare data
        export_df = df.copy()
        
        if mask_passwords and 'password' in export_df.columns:
            export_df['password'] = export_df['password'].apply(
                lambda x: app_config.PASSWORD_MASK if x and str(x).strip() else ""
            )
        
        output = io.StringIO()
        
        # Write metadata header if requested
        if include_metadata:
            output.write(f"# WiFi Profile Export\n")
            output.write(f"# Generated: {datetime.now().isoformat()}\n")
            output.write(f"# Total profiles: {len(export_df)}\n")
            output.write(f"# Passwords masked: {mask_passwords}\n")
            output.write("#\n")
        
        # Write CSV data
        export_df.to_csv(
            output,
            index=False,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'
        )
        
        return output.getvalue()
    
    @staticmethod
    def to_json(
        df: pd.DataFrame,
        include_metadata: bool = True,
        mask_passwords: bool = False,
        pretty_print: bool = True
    ) -> str:
        """
        Export DataFrame to JSON format.
        
        Args:
            df: DataFrame to export
            include_metadata: Whether to include metadata
            mask_passwords: Whether to mask password fields
            pretty_print: Whether to format JSON with indentation
            
        Returns:
            JSON data as string
        """
        if df.empty:
            return json.dumps({"profiles": [], "metadata": {"message": "No data to export"}})
        
        # Prepare data
        export_df = df.copy()
        
        if mask_passwords and 'password' in export_df.columns:
            export_df['password'] = export_df['password'].apply(
                lambda x: app_config.PASSWORD_MASK if x and str(x).strip() else ""
            )
        
        # Convert to records
        records = export_df.to_dict(orient="records")
        
        # Build output structure
        output_data = {"profiles": records}
        
        if include_metadata:
            output_data["metadata"] = {
                "export_time": datetime.now().isoformat(),
                "total_profiles": len(records),
                "passwords_masked": mask_passwords,
                "exported_by": app_config.APP_NAME,
                "version": app_config.APP_VERSION
            }
        
        indent = 2 if pretty_print else None
        return json.dumps(output_data, ensure_ascii=False, indent=indent)
    
    @staticmethod
    def to_excel(
        df: pd.DataFrame,
        include_metadata: bool = True,
        mask_passwords: bool = False
    ) -> bytes:
        """
        Export DataFrame to Excel format.
        
        Args:
            df: DataFrame to export
            include_metadata: Whether to include metadata sheet
            mask_passwords: Whether to mask password fields
            
        Returns:
            Excel file as bytes
        """
        if df.empty:
            # Return empty workbook
            empty_df = pd.DataFrame({"message": ["No data to export"]})
            return empty_df.to_excel(None, index=False, engine='openpyxl').getvalue()
        
        # Prepare data
        export_df = df.copy()
        
        if mask_passwords and 'password' in export_df.columns:
            export_df['password'] = export_df['password'].apply(
                lambda x: app_config.PASSWORD_MASK if x and str(x).strip() else ""
            )
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write main data
            export_df.to_excel(writer, sheet_name='WiFi_Profiles', index=False)
            
            # Write metadata if requested
            if include_metadata:
                metadata_df = pd.DataFrame({
                    'Property': [
                        'Export Time',
                        'Total Profiles',
                        'Passwords Masked',
                        'Application',
                        'Version'
                    ],
                    'Value': [
                        datetime.now().isoformat(),
                        len(export_df),
                        mask_passwords,
                        app_config.APP_NAME,
                        app_config.APP_VERSION
                    ]
                })
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        return output.getvalue()


class DataFilter:
    """Handle data filtering and search operations."""
    
    @staticmethod
    def filter_by_ssid(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """
        Filter DataFrame by SSID search term.
        
        Args:
            df: DataFrame to filter
            search_term: Search term to match against SSID
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or not search_term:
            return df
        
        search_term = search_term.strip().lower()
        
        # Filter by SSID containing search term
        mask = df['ssid'].astype(str).str.lower().str.contains(
            search_term, 
            na=False, 
            regex=False
        )
        
        return df[mask]
    
    @staticmethod
    def filter_by_security(df: pd.DataFrame, security_types: List[str]) -> pd.DataFrame:
        """
        Filter DataFrame by security/authentication types.
        
        Args:
            df: DataFrame to filter
            security_types: List of security types to include
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or not security_types:
            return df
        
        mask = df['authentication'].isin(security_types)
        return df[mask]
    
    @staticmethod
    def filter_by_password_availability(df: pd.DataFrame, has_password: bool) -> pd.DataFrame:
        """
        Filter DataFrame by password availability.
        
        Args:
            df: DataFrame to filter
            has_password: True to show only profiles with passwords,
                         False to show only profiles without passwords
            
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df
        
        if 'has_password' in df.columns:
            mask = df['has_password'] == has_password
        else:
            # Fallback to checking password field directly
            if has_password:
                mask = (df['password'].astype(str).str.strip() != "")
            else:
                mask = (df['password'].astype(str).str.strip() == "")
        
        return df[mask]


class DataFormatter:
    """Handle data formatting and display operations."""
    
    @staticmethod
    def mask_passwords(series: pd.Series, show_passwords: bool) -> pd.Series:
        """
        Mask or unmask passwords in a Series.
        
        Args:
            series: Series containing passwords
            show_passwords: Whether to show actual passwords
            
        Returns:
            Series with masked/unmasked passwords
        """
        if show_passwords:
            return series.fillna("")
        
        return series.apply(
            lambda x: app_config.PASSWORD_MASK if isinstance(x, str) and x.strip() != "" else ""
        )
    
    @staticmethod
    def format_for_display(df: pd.DataFrame, show_passwords: bool = False) -> pd.DataFrame:
        """
        Format DataFrame for display in UI.
        
        Args:
            df: DataFrame to format
            show_passwords: Whether to show passwords
            
        Returns:
            Formatted DataFrame
        """
        if df.empty:
            return df
        
        display_df = df.copy()
        
        # Rename columns for better display
        column_mapping = {
            'ssid': 'SSID',
            'authentication': 'Authentication',
            'cipher': 'Cipher',
            'password': 'Password',
            'connection_type': 'Type',
            'cost': 'Cost',
            'interface': 'Interface'
        }
        
        # Only rename columns that exist
        existing_columns = {k: v for k, v in column_mapping.items() if k in display_df.columns}
        display_df = display_df.rename(columns=existing_columns)
        
        # Mask passwords if needed
        if 'Password' in display_df.columns:
            display_df['Password'] = DataFormatter.mask_passwords(
                display_df['Password'], 
                show_passwords
            )
        
        # Select and order columns for display
        display_columns = ['SSID', 'Authentication', 'Cipher', 'Type', 'Interface', 'Password']
        available_columns = [col for col in display_columns if col in display_df.columns]
        
        return display_df[available_columns]
    
    @staticmethod
    def get_security_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get security summary statistics.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with security statistics
        """
        if df.empty:
            return {"total": 0, "secure": 0, "open": 0, "unknown": 0}
        
        # Count security types
        secure_count = 0
        open_count = 0
        unknown_count = 0
        
        for _, row in df.iterrows():
            auth = str(row.get('authentication', '')).lower()
            if 'wpa' in auth or 'wep' in auth or auth in ['shared', 'ieee8021x']:
                secure_count += 1
            elif auth in ['open', 'none', '']:
                open_count += 1
            else:
                unknown_count += 1
        
        return {
            "total": len(df),
            "secure": secure_count,
            "open": open_count,
            "unknown": unknown_count
        }
    
    @staticmethod
    def generate_filename(base_name: str, extension: str, include_timestamp: bool = True) -> str:
        """
        Generate a filename for exports.
        
        Args:
            base_name: Base name for the file
            extension: File extension (without dot)
            include_timestamp: Whether to include timestamp
            
        Returns:
            Generated filename
        """
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{base_name}_{timestamp}.{extension}"
        
        return f"{base_name}.{extension}"