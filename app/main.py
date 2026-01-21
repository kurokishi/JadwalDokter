"""
Main Streamlit App for Jadwal Dokter
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import AppConfig

def init_session_state():
    """Initialize session state variables"""
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None

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
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Setup
    setup_page()
    init_session_state()
    
    # Header
    st.markdown(f"<h1 class='main-header'>{AppConfig.APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>Versi {AppConfig.APP_VERSION}</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        #st.image("🏥", width=100)
        st.title("Navigasi")
        
        # File info
        if st.session_state.data_loaded:
            st.success(f"✅ File Loaded: {st.session_state.current_file}")
        
        # Navigation
        menu_options = ["🏠 Home", "📤 Upload Data", "📅 Jadwal Dokter", "🧩 Kanban Drag", "ℹ️ About"]
        selected_menu = st.radio("Menu:", menu_options)
    
    # Import UI components based on selection
    try:
        if selected_menu == "🏠 Home":
            from app.ui.home import display_home_tab
            display_home_tab()
        
        elif selected_menu == "📤 Upload Data":
            from app.ui.tab_upload import display_upload_tab
            display_upload_tab()
        
        elif selected_menu == "📅 Jadwal Dokter":
            if st.session_state.data_loaded:
                from app.ui.tab_schedule import display_schedule_tab
                display_schedule_tab()
            else:
                st.warning("⚠️ Silakan upload data terlebih dahulu di tab 'Upload Data'")
        
        elif selected_menu == "🧩 Kanban Drag":
            if st.session_state.data_loaded:
                from app.ui.tab_kanban_drag import display_kanban_tab
                display_kanban_tab()
            else:
                st.warning("⚠️ Silakan upload data terlebih dahulu di tab 'Upload Data'")
        
        elif selected_menu == "ℹ️ About":
            from app.ui.tab_about import display_about_tab
            display_about_tab()
    
    except Exception as e:
        st.error(f"Error loading tab: {str(e)}")
    
    # Footer
    st.divider()
    st.caption(f"© 2024 {AppConfig.APP_NAME}")

if __name__ == "__main__":
    main()
