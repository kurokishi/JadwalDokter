"""
Main Streamlit App for Jadwal Dokter
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import AppConfig
from app.utils.parser import JadwalHafisParser

# Import UI components
from app.ui.home import display_home_tab
from app.ui.tab_upload import display_upload_tab
from app.ui.tab_schedule import display_schedule_tab
from app.ui.tab_kanban_drag import display_kanban_tab
from app.ui.tab_preferences import display_preferences_tab
from app.ui.tab_about import display_about_tab

def init_session_state():
    """Initialize session state variables"""
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {
            'working_hours_start': '08:00',
            'working_hours_end': '16:00',
            'days_to_show': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'view_mode': 'table',
            'time_format': '24h'
        }
    if 'hafis_parsed' not in st.session_state:
        st.session_state.hafis_parsed = False

def setup_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=AppConfig.PAGE_TITLE,
        page_icon=AppConfig.PAGE_ICON,
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def show_data_info(df):
    """Display data information"""
    if df is not None:
        with st.expander("📊 Data Information", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Unique Doctors", len(df['doctor_name'].unique()))
            with col3:
                st.metric("Specialties", len(df['specialty'].unique()))
            with col4:
                st.metric("Days Coverage", len(df['day'].unique()))
            
            # Data types
            st.write("**Column Information:**")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Non-Null Count': df.notna().sum(),
                'Null Count': df.isna().sum()
            })
            st.dataframe(col_info, use_container_width=True)

def main():
    """Main application function"""
    # Setup
    setup_page()
    init_session_state()
    
    # Header
    st.markdown(f"<h1 class='main-header'>{AppConfig.APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>Versi {AppConfig.APP_VERSION} - Aplikasi Penjadwalan Dokter Rumah Sakit</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("🏥", width=100)
        st.title("Navigasi")
        
        # File info
        if st.session_state.data_loaded:
            st.success(f"✅ File Loaded: {st.session_state.current_file}")
            st.info(f"📊 {len(st.session_state.data)} records")
        
        # Navigation tabs
        selected_tab = st.radio(
            "Menu Utama:",
            ["🏠 Home", "📤 Upload Data", "📅 Jadwal Dokter", "🧩 Kanban Drag", "⚙️ Preferences", "ℹ️ About"],
            index=0 if not st.session_state.data_loaded else 2
        )
        
        # Quick stats if data loaded
        if st.session_state.data_loaded:
            st.divider()
            st.subheader("Quick Stats")
            df = st.session_state.data
            
            if 'specialty' in df.columns:
                top_specialties = df['specialty'].value_counts().head(5)
                for spec, count in top_specialties.items():
                    st.write(f"• {spec}: {count} jadwal")
    
    # Main content based on selected tab
    if selected_tab == "🏠 Home":
        display_home_tab()
    
    elif selected_tab == "📤 Upload Data":
        display_upload_tab()
        
        # Custom handling for jadwal_hafis.xlsx
        uploaded_file = st.session_state.get('uploaded_file', None)
        if uploaded_file and 'hafis' in uploaded_file.name.lower():
            st.info("🎯 **File jadwal_hafis.xlsx terdeteksi!** Gunakan parser khusus untuk format ini.")
    
    elif selected_tab == "📅 Jadwal Dokter":
        if st.session_state.data_loaded:
            display_schedule_tab()
        else:
            st.warning("⚠️ Silakan upload data terlebih dahulu di tab 'Upload Data'")
            st.info("Format yang didukung: Excel (.xlsx, .xls) atau CSV")
    
    elif selected_tab == "🧩 Kanban Drag":
        if st.session_state.data_loaded:
            display_kanban_tab()
        else:
            st.warning("⚠️ Silakan upload data terlebih dahulu di tab 'Upload Data'")
    
    elif selected_tab == "⚙️ Preferences":
        display_preferences_tab()
    
    elif selected_tab == "ℹ️ About":
        display_about_tab()
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.caption(f"© 2024 {AppConfig.APP_NAME} | Version {AppConfig.APP_VERSION}")

if __name__ == "__main__":
    main()
