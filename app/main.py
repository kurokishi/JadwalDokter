"""
Main Streamlit application for Jadwal Dokter Converter
"""
import streamlit as st
import sys
import os
from datetime import datetime

# Add the app directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app.ui.home import show_home
from app.ui.upload_converter import show_upload_converter
from app.ui.schedule_viewer import show_schedule_viewer
from app.ui.export_manager import show_export_manager
from app.ui.about import show_about
from app.utils import init_session_state
from app.config import AppConfig


def main():
    """Main application entry point"""
    
    # Page configuration - NO EMOJI in page_title to avoid encoding issues
    st.set_page_config(
        page_title="Jadwal Dokter Converter",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo/jadwal-dokter',
            'Report a bug': 'https://github.com/your-repo/jadwal-dokter/issues',
            'About': f"Jadwal Dokter Converter v{AppConfig().VERSION}"
        }
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding: 0 1rem;
    }
    
    /* Header styling */
    .st-emotion-cache-1y4p8pa {
        padding-top: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    /* Metric card styling */
    .stMetric {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    /* Sidebar styling */
    .st-emotion-cache-16txtl3 {
        padding: 2rem 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Initialize navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏥 Jadwal Dokter")
        st.markdown(f"*v{AppConfig().VERSION}*")
        
        st.markdown("---")
        
        # Navigation menu
        menu_items = {
            "🏠 Home": "home",
            "🔄 Upload & Konversi": "upload",
            "📅 View Jadwal": "view",
            "💾 Export Data": "export",
            "ℹ️ Tentang": "about"
        }
        
        selected = st.selectbox(
            "Navigasi",
            options=list(menu_items.keys()),
            index=list(menu_items.values()).index(st.session_state.current_page) 
            if st.session_state.current_page in menu_items.values() else 0
        )
        
        # Update current page based on selection
        if selected in menu_items:
            st.session_state.current_page = menu_items[selected]
        
        st.markdown("---")
        
        # Quick stats if data exists
        if st.session_state.get('grid_data') is not None:
            grid_df = st.session_state.grid_data
            st.markdown("**📊 Quick Stats:**")
            st.markdown(f"• Jadwal: {len(grid_df)}")
            st.markdown(f"• Dokter: {grid_df['DOKTER'].nunique()}")
            st.markdown(f"• Poli: {grid_df['POLI'].nunique()}")
        
        # Footer in sidebar
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: #6b7280; font-size: 0.8rem;'>
        <p>© 2024 Jadwal Dokter</p>
        <p>{datetime.now().strftime('%d %B %Y')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    st.container()
    
    # Page routing based on current_page
    if st.session_state.current_page == 'home':
        show_home()
    elif st.session_state.current_page == 'upload':
        show_upload_converter()
    elif st.session_state.current_page == 'view':
        show_schedule_viewer()
    elif st.session_state.current_page == 'export':
        show_export_manager()
    elif st.session_state.current_page == 'about':
        show_about()
    else:
        show_home()


if __name__ == "__main__":
    main()
