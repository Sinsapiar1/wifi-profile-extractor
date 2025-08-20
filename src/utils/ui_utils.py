"""
UI utilities for WiFi Profile Extractor Streamlit application.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..config.settings import app_config
from ..config.constants import (
    PASSWORD_REVEAL_WARNING,
    MAX_PROFILES_DISPLAY,
    SUPPORTED_EXPORT_FORMATS
)


class UIComponents:
    """Reusable UI components for the Streamlit application."""
    
    @staticmethod
    def render_status_badge(status: str, message: str) -> None:
        """
        Render a status badge with color coding.
        
        Args:
            status: Status type ('success', 'error', 'warning', 'info')
            message: Message to display
        """
        status_colors = {
            'success': '🟢',
            'error': '🔴',
            'warning': '🟡',
            'info': '🔵'
        }
        
        icon = status_colors.get(status, '⚪')
        st.markdown(f"{icon} **{message}**")
    
    @staticmethod
    def render_metric_card(title: str, value: Any, delta: Optional[str] = None) -> None:
        """
        Render a metric card with optional delta.
        
        Args:
            title: Metric title
            value: Metric value
            delta: Optional delta value
        """
        st.metric(label=title, value=value, delta=delta)
    
    @staticmethod
    def render_profile_table(
        profiles_df: pd.DataFrame, 
        show_passwords: bool = False,
        search_query: str = ""
    ) -> pd.DataFrame:
        """
        Render WiFi profiles table with filtering and password masking.
        
        Args:
            profiles_df: DataFrame containing profile data
            show_passwords: Whether to show passwords in plain text
            search_query: Search query for filtering
            
        Returns:
            pd.DataFrame: Filtered and formatted DataFrame
        """
        if profiles_df.empty:
            st.info("No WiFi profiles found.")
            return profiles_df
        
        # Apply search filter
        if search_query:
            mask = profiles_df['SSID'].str.contains(
                search_query, 
                case=False, 
                na=False
            )
            profiles_df = profiles_df[mask]
        
        # Mask passwords if needed
        display_df = profiles_df.copy()
        if not show_passwords and 'Password' in display_df.columns:
            display_df['Password'] = display_df['Password'].apply(
                lambda x: app_config.PASSWORD_MASK if pd.notna(x) and x != "" else x
            )
        
        # Limit display rows
        if len(display_df) > MAX_PROFILES_DISPLAY:
            st.warning(f"Showing first {MAX_PROFILES_DISPLAY} profiles of {len(display_df)} total.")
            display_df = display_df.head(MAX_PROFILES_DISPLAY)
        
        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        return display_df
    
    @staticmethod
    def render_password_toggle() -> bool:
        """
        Render password visibility toggle with warning.
        
        Returns:
            bool: Current password visibility state
        """
        show_passwords = st.checkbox(
            "Show passwords in plain text",
            value=st.session_state.get('show_passwords', False),
            help="Toggle to reveal WiFi passwords"
        )
        
        if show_passwords:
            st.warning(PASSWORD_REVEAL_WARNING)
        
        return show_passwords
    
    @staticmethod
    def render_export_controls(profiles_df: pd.DataFrame) -> None:
        """
        Render export controls section.
        
        Args:
            profiles_df: DataFrame containing profile data to export
        """
        if profiles_df.empty:
            st.info("No data to export.")
            return
        
        st.subheader("📤 Export Options")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            export_format = st.selectbox(
                "Export Format",
                options=SUPPORTED_EXPORT_FORMATS,
                format_func=lambda x: x.upper()
            )
        
        with col2:
            include_passwords = st.checkbox(
                "Include passwords",
                value=False,
                help="Include passwords in exported file"
            )
        
        if include_passwords:
            st.warning("⚠️ Exported file will contain passwords in plain text!")
        
        filename = st.text_input(
            "Filename (without extension)",
            value=f"wifi_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        return {
            'format': export_format,
            'include_passwords': include_passwords,
            'filename': filename
        }
    
    @staticmethod
    def render_search_box(placeholder: str = None) -> str:
        """
        Render search input box.
        
        Args:
            placeholder: Placeholder text for search box
            
        Returns:
            str: Search query
        """
        placeholder = placeholder or app_config.SEARCH_PLACEHOLDER
        return st.text_input(
            "🔍 Search",
            placeholder=placeholder,
            label_visibility="collapsed"
        )
    
    @staticmethod
    def render_filter_controls() -> Dict[str, Any]:
        """
        Render advanced filter controls.
        
        Returns:
            Dict containing filter criteria
        """
        st.subheader("🔧 Advanced Filters")
        
        # Authentication filter
        auth_filter = st.multiselect(
            "Authentication Type",
            options=["Open", "WPA-Personal", "WPA2-Personal", "WPA3-Personal", "WEP"],
            help="Filter by authentication type"
        )
        
        # Has password filter
        password_filter = st.radio(
            "Password Status",
            options=["All", "With Password", "Without Password"],
            horizontal=True
        )
        
        # Cipher filter
        cipher_filter = st.multiselect(
            "Cipher Type",
            options=["None", "WEP", "TKIP", "CCMP", "GCMP"],
            help="Filter by cipher type"
        )
        
        return {
            'authentication': auth_filter,
            'password_status': password_filter,
            'cipher': cipher_filter
        }


class UIHelpers:
    """Helper functions for UI operations."""
    
    @staticmethod
    def format_timestamp(timestamp: Optional[datetime]) -> str:
        """
        Format timestamp for display.
        
        Args:
            timestamp: Timestamp to format
            
        Returns:
            str: Formatted timestamp string
        """
        if not timestamp:
            return "Never"
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            str: Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def create_download_button(
        data: bytes,
        filename: str,
        mime_type: str,
        button_text: str = "Download"
    ) -> bool:
        """
        Create a download button for data export.
        
        Args:
            data: Data to download as bytes
            filename: Name of the file
            mime_type: MIME type of the file
            button_text: Text for the download button
            
        Returns:
            bool: True if button was clicked
        """
        return st.download_button(
            label=button_text,
            data=data,
            file_name=filename,
            mime=mime_type,
            use_container_width=True
        )
    
    @staticmethod
    def show_progress_bar(current: int, total: int, text: str = "") -> None:
        """
        Show progress bar with optional text.
        
        Args:
            current: Current progress value
            total: Total progress value
            text: Optional progress text
        """
        progress = current / total if total > 0 else 0
        st.progress(progress, text=text)
    
    @staticmethod
    def render_info_expander(title: str, content: str) -> None:
        """
        Render an expandable info section.
        
        Args:
            title: Title of the expander
            content: Content to display
        """
        with st.expander(title):
            st.markdown(content)


class StyleHelper:
    """Helper for applying custom styles."""
    
    @staticmethod
    def apply_custom_css() -> None:
        """Apply custom CSS styles to the Streamlit app."""
        st.markdown("""
        <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
        }
        
        .status-success {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-error {
            color: #dc3545;
            font-weight: bold;
        }
        
        .status-warning {
            color: #ffc107;
            font-weight: bold;
        }
        
        .password-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 0.25rem;
            padding: 0.75rem;
            margin: 0.5rem 0;
        }
        
        .profile-table {
            font-family: 'Courier New', monospace;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_colored_text(text: str, color: str) -> None:
        """
        Render text with custom color.
        
        Args:
            text: Text to display
            color: CSS color value
        """
        st.markdown(
            f'<span style="color: {color}">{text}</span>',
            unsafe_allow_html=True
        )