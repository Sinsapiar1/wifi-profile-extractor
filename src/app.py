"""
WiFi Profile Extractor - Professional Streamlit Application.
"""

import logging
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Agregar raíz del proyecto al path para importaciones
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import application modules con manejo de errores
try:
    from src.core.wifi_extractor import WiFiProfileExtractor, WiFiProfile
    from src.core.exceptions import (
        UnsupportedOperatingSystemError,
        InsufficientPrivilegesError,
        NoWiFiProfilesFoundError,
        WiFiExtractorBaseException
    )
    from src.utils.system_utils import SystemUtils, PrivilegeManager
    from src.utils.data_utils import DataExporter, DataFilter, DataFormatter
    from src.config.settings import app_config
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.error("Please ensure all project files are in place")
    st.stop()


class WiFiProfileApp:
    """Main application class for WiFi Profile Extractor."""
    
    def __init__(self):
        """Initialize the application."""
        try:
            self.extractor = WiFiProfileExtractor()
            self.system_utils = SystemUtils()
            self.privilege_manager = PrivilegeManager()
        except Exception as e:
            st.error(f"Failed to initialize application: {e}")
            st.stop()
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'profiles_data' not in st.session_state:
            st.session_state.profiles_data = None
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = None
        if 'show_passwords' not in st.session_state:
            st.session_state.show_passwords = not app_config.MASK_PASSWORDS_DEFAULT
        if 'privilege_status' not in st.session_state:
            st.session_state.privilege_status = None
    
    def configure_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=app_config.PAGE_TITLE,
            page_icon=app_config.PAGE_ICON,
            layout=app_config.LAYOUT,
            initial_sidebar_state=app_config.SIDEBAR_STATE,
            menu_items={
                'About': f"{app_config.APP_DESCRIPTION} v{app_config.APP_VERSION}"
            }
        )
    
    def render_header(self):
        """Render application header."""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.title(f"{app_config.PAGE_ICON} {app_config.APP_NAME}")
            st.caption(
                "Professional WiFi profile extraction and management tool for Windows. "
                "Use only on systems and networks under your control."
            )
        
        with col2:
            st.metric("Version", app_config.APP_VERSION)
    
    def render_sidebar(self):
        """Render sidebar with controls and information."""
        with st.sidebar:
            st.header("🔧 Controls")
            
            # System status
            self._render_system_status()
            
            st.divider()
            
            # Main controls
            self._render_main_controls()
            
            st.divider()
            
            # Filter controls
            self._render_filter_controls()
            
            st.divider()
            
            # Export controls
            self._render_export_controls()
            
            st.divider()
            
            # Help section
            self._render_help_section()
    
    def _render_system_status(self):
        """Render system status information."""
        st.subheader("🖥️ System Status")
        
        # Get current privilege status
        privilege_status = self.privilege_manager.get_privilege_status()
        st.session_state.privilege_status = privilege_status
        
        # OS Compatibility
        if privilege_status['os_compatible']:
            st.success("✅ Windows OS detected")
        else:
            st.error("❌ Unsupported OS")
        
        # Admin privileges
        if privilege_status['is_admin']:
            st.success("✅ Administrator privileges")
        else:
            st.warning("⚠️ Limited privileges")
        
        # Password access
        if privilege_status['can_access_passwords']:
            st.success("✅ Can access passwords")
        else:
            st.warning("⚠️ Cannot access passwords")
    
    def _render_main_controls(self):
        """Render main control buttons."""
        st.subheader("🔄 Data Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Scan Profiles", use_container_width=True, type="primary"):
                self._scan_profiles()
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                self._refresh_data()
        
        # Password visibility toggle
        st.session_state.show_passwords = st.toggle(
            "👁️ Show Passwords",
            value=st.session_state.show_passwords,
            help="Toggle password visibility (requires admin privileges)"
        )
    
    def _render_filter_controls(self):
        """Render filter controls."""
        st.subheader("🔍 Filters")
        
        # SSID search
        search_term = st.text_input(
            "Search SSID",
            placeholder=app_config.SEARCH_PLACEHOLDER,
            help="Search for specific network names"
        )
        st.session_state.search_term = search_term
        
        # Security filter
        if st.session_state.profiles_data is not None and not st.session_state.profiles_data.empty:
            auth_types = st.session_state.profiles_data['authentication'].unique()
            auth_types = [auth for auth in auth_types if auth and str(auth).strip()]
            
            if auth_types:
                selected_auth = st.multiselect(
                    "Authentication Types",
                    options=auth_types,
                    default=auth_types,
                    help="Filter by authentication method"
                )
                st.session_state.selected_auth = selected_auth
        
        # Password availability filter
        password_filter = st.selectbox(
            "Password Status",
            options=["All", "With Password", "Without Password"],
            help="Filter by password availability"
        )
        st.session_state.password_filter = password_filter
    
    def _render_export_controls(self):
        """Render export controls."""
        st.subheader("📤 Export")
        
        export_format = st.selectbox(
            "Format",
            options=app_config.SUPPORTED_FORMATS,
            index=0,
            help="Select export format"
        )
        st.session_state.export_format = export_format
        
        include_metadata = st.checkbox(
            "Include Metadata",
            value=True,
            help="Include export metadata"
        )
        st.session_state.include_metadata = include_metadata
        
        mask_passwords = st.checkbox(
            "Mask Passwords",
            value=True,
            help="Mask passwords in export"
        )
        st.session_state.mask_passwords = mask_passwords
    
    def _render_help_section(self):
        """Render help and information section."""
        st.subheader("ℹ️ Help")
        
        with st.expander("System Requirements"):
            privilege_status = st.session_state.get('privilege_status', {})
            recommendations = privilege_status.get('recommendations', [])
            
            for rec in recommendations:
                st.info(rec)
        
        with st.expander("Security Notice"):
            st.warning(
                "⚠️ **Security Notice**\n\n"
                "- Use only on systems you own or have permission to audit\n"
                "- WiFi passwords are sensitive information\n"
                "- Consider running from a secure, private environment\n"
                "- Clear browser history after use if in shared environment"
            )
        
        with st.expander("Command Line Alternative"):
            cmd_txt = (
                'for /f "tokens=1,* delims=:" %a in (\'netsh wlan show profiles ^| '
                'findstr /i /c:"All User Profile" /c:"Perfil de todos los usuarios"\') '
                'do @for /f "tokens=* delims= " %i in ("%b") do @echo SSID: %i & '
                'netsh wlan show profile name="%i" key=clear ^| '
                'findstr /i /c:"Key Content" /c:"Contenido de la clave" & echo.'
            )
            st.code(cmd_txt, language="batch")
    
    def _scan_profiles(self):
        """Scan for WiFi profiles."""
        try:
            with st.spinner("Scanning WiFi profiles..."):
                # Check admin privileges for password access
                require_admin = st.session_state.show_passwords
                
                profiles = self.extractor.extract_profiles(require_admin=require_admin)
                df = self.extractor.to_dataframe(profiles)
                
                st.session_state.profiles_data = df
                st.session_state.last_refresh = datetime.now()
                
                st.success(f"✅ Found {len(profiles)} WiFi profiles")
                
        except UnsupportedOperatingSystemError as e:
            st.error(f"❌ {e.message}")
        except InsufficientPrivilegesError as e:
            st.error(f"❌ {e.message}")
            st.info("💡 Try running as Administrator to access passwords")
        except NoWiFiProfilesFoundError as e:
            st.warning(f"⚠️ {e.message}")
        except WiFiExtractorBaseException as e:
            st.error(f"❌ Error: {e.message}")
            if e.details:
                st.error(f"Details: {e.details}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            logger.exception("Unexpected error during profile scanning")
    
    def _refresh_data(self):
        """Refresh current data."""
        if st.session_state.profiles_data is not None:
            self._scan_profiles()
        else:
            st.info("No data to refresh. Please scan profiles first.")
    
    def render_main_content(self):
        """Render main content area."""
        if st.session_state.profiles_data is None:
            self._render_welcome_screen()
        else:
            self._render_data_view()
    
    def _render_welcome_screen(self):
        """Render welcome screen when no data is loaded."""
        st.markdown("## 🚀 Welcome to WiFi Profile Extractor")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            ### Getting Started
            
            1. **Check System Status** - Ensure you're on Windows
            2. **Run as Administrator** - For password access (optional)
            3. **Click 'Scan Profiles'** - Extract WiFi information
            4. **Review & Export** - Manage your WiFi data
            
            ### Features
            
            - 🔍 **Extract WiFi Profiles** - Get all saved networks
            - 🔐 **Access Passwords** - View saved passwords (admin required)
            - 📊 **Filter & Search** - Find specific networks
            - 📤 **Multiple Export Formats** - CSV, JSON, Excel
            - 🛡️ **Security Focused** - Local processing only
            """)
            
            if st.button("🔍 Start Scanning", use_container_width=True, type="primary"):
                self._scan_profiles()
    
    def _render_data_view(self):
        """Render data view with profiles information."""
        df = st.session_state.profiles_data
        
        if df.empty:
            st.warning("No WiFi profiles found.")
            return
        
        # Apply filters
        filtered_df = self._apply_filters(df)
        
        # Render metrics
        self._render_metrics(df, filtered_df)
        
        # Render data table
        self._render_data_table(filtered_df)
        
        # Render detailed view
        self._render_detailed_view(filtered_df)
        
        # Render export section
        self._render_export_section(filtered_df)
    
    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to the DataFrame."""
        filtered_df = df.copy()
        
        # Apply SSID search filter
        search_term = st.session_state.get('search_term', '')
        if search_term:
            filtered_df = DataFilter.filter_by_ssid(filtered_df, search_term)
        
        # Apply authentication filter
        selected_auth = st.session_state.get('selected_auth', [])
        if selected_auth:
            filtered_df = DataFilter.filter_by_security(filtered_df, selected_auth)
        
        # Apply password filter
        password_filter = st.session_state.get('password_filter', 'All')
        if password_filter == 'With Password':
            filtered_df = DataFilter.filter_by_password_availability(filtered_df, True)
        elif password_filter == 'Without Password':
            filtered_df = DataFilter.filter_by_password_availability(filtered_df, False)
        
        return filtered_df
    
    def _render_metrics(self, full_df: pd.DataFrame, filtered_df: pd.DataFrame):
        """Render metrics cards."""
        col1, col2, col3, col4 = st.columns(4)
        
        total_profiles = len(full_df)
        visible_profiles = len(filtered_df)
        
        # Count profiles with passwords
        profiles_with_passwords = 0
        profiles_without_passwords = 0
        
        if 'has_password' in filtered_df.columns:
            profiles_with_passwords = filtered_df['has_password'].sum()
        else:
            profiles_with_passwords = (filtered_df['password'].astype(str).str.strip() != "").sum()
        
        profiles_without_passwords = visible_profiles - profiles_with_passwords
        
        col1.metric("Total Profiles", total_profiles)
        col2.metric("Showing", visible_profiles)
        col3.metric("With Password", profiles_with_passwords)
        col4.metric("Without Password", profiles_without_passwords)
        
        # Show refresh time
        if st.session_state.last_refresh:
            st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _render_data_table(self, df: pd.DataFrame):
        """Render main data table."""
        st.subheader("📋 WiFi Profiles")
        
        if df.empty:
            st.info("No profiles match the current filters.")
            return
        
        # Format data for display
        display_df = DataFormatter.format_for_display(
            df, 
            show_passwords=st.session_state.show_passwords
        )
        
        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=min(len(display_df) * 35 + 38, 600)  # Dynamic height with max
        )
    
    def _render_detailed_view(self, df: pd.DataFrame):
        """Render detailed view of profiles."""
        if df.empty:
            return
        
        with st.expander("🔍 Detailed View", expanded=False):
            for idx, row in df.iterrows():
                with st.container(border=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**SSID:** {row.get('ssid', 'Unknown')}")
                        st.markdown(f"**Type:** {row.get('connection_type', 'Unknown')}")
                    
                    with col2:
                        st.markdown(f"**Auth:** {row.get('authentication', 'Unknown')}")
                        st.markdown(f"**Cipher:** {row.get('cipher', 'Unknown')}")
                    
                    with col3:
                        password = row.get('password', '')
                        if st.session_state.show_passwords:
                            password_display = password if password else "None"
                        else:
                            password_display = app_config.PASSWORD_MASK if password else "None"
                        
                        st.markdown(f"**Password:** {password_display}")
                        st.markdown(f"**Interface:** {row.get('interface', 'Unknown')}")
    
    def _render_export_section(self, df: pd.DataFrame):
        """Render export section."""
        if df.empty:
            return
        
        st.subheader("📤 Export Data")
        
        col1, col2, col3 = st.columns([2, 2, 3])
        
        # Generate export data
        export_format = st.session_state.get('export_format', 'CSV')
        include_metadata = st.session_state.get('include_metadata', True)
        mask_passwords = st.session_state.get('mask_passwords', True)
        
        try:
            if export_format == 'CSV':
                export_data = DataExporter.to_csv(df, include_metadata, mask_passwords)
                mime_type = 'text/csv'
                file_extension = 'csv'
            elif export_format == 'JSON':
                export_data = DataExporter.to_json(df, include_metadata, mask_passwords)
                mime_type = 'application/json'
                file_extension = 'json'
            elif export_format == 'XLSX':
                export_data = DataExporter.to_excel(df, include_metadata, mask_passwords)
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_extension = 'xlsx'
            else:
                st.error("Unsupported export format")
                return
            
            filename = DataFormatter.generate_filename(
                "wifi_profiles",
                file_extension,
                include_timestamp=True
            )
            
            with col1:
                if export_format == 'XLSX':
                    st.download_button(
                        "📥 Download",
                        data=export_data,
                        file_name=filename,
                        mime=mime_type,
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.download_button(
                        "📥 Download",
                        data=export_data.encode('utf-8') if isinstance(export_data, str) else export_data,
                        file_name=filename,
                        mime=mime_type,
                        type="primary",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("📋 Copy Data", use_container_width=True):
                    if export_format != 'XLSX':
                        st.code(export_data[:500] + "..." if len(export_data) > 500 else export_data)
                    else:
                        st.info("Excel data cannot be displayed as text")
            
            with col3:
                st.info(f"**Export Info**\n\n"
                       f"Format: {export_format}\n\n"
                       f"Records: {len(df)}\n\n"
                       f"Passwords: {'Masked' if mask_passwords else 'Visible'}")
        
        except Exception as e:
            st.error(f"Export error: {str(e)}")
    
    def run(self):
        """Run the application."""
        self.configure_page()
        self.render_header()
        self.render_sidebar()
        self.render_main_content()


def main():
    """Main application entry point."""
    try:
        app = WiFiProfileApp()
        app.configure_page()
        app.render_header()
        app.render_sidebar()
        app.render_main_content()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.exception("Application startup error")


if __name__ == "__main__":
    main()