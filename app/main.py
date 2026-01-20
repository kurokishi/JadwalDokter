"""
Main module untuk aplikasi Streamlit
"""
import streamlit as st
from app.utils.parser import JadwalHafisParser
from .config import config

# Import UI functions
from .ui.home import render as render_home
from .ui.tab_upload import render as render_upload
from .ui.tab_schedule import render as render_schedule
from .ui.tab_kanban_drag import render as render_kanban
from .ui.tab_preferences import render as render_preferences
from .ui.tab_about import render as render_about

def initialize_session_state():
    """Initialize semua session state yang diperlukan"""
    default_states = {
        'uploaded_data': None,
        'file_name': None,
        'upload_time': None,
        'schedule_data': None,
        'validation_errors': [],
        'doctors_list': [],
        'specializations': [],
        'preferences': {},
        'current_view': 'home',
        'notification': None,
        'total_doctors': 0,
        'total_schedules': 0,
        'total_hours': 0,
        'conflicts': []
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def setup_page():
    """Setup halaman Streamlit"""
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown(f"""
        <style>
        .main {{
            padding: 1rem 2rem;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: #f0f2f6;
            padding: 8px;
            border-radius: 10px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            padding: 0 20px;
            background-color: white;
            border-radius: 5px;
            color: {config.COLORS['primary']};
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {config.COLORS['primary']} !important;
            color: white !important;
        }}
        
        .schedule-card {{
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
            border-left: 5px solid {config.COLORS['primary']};
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .metric-card {{
            padding: 15px;
            border-radius: 10px;
            background: linear-gradient(135deg, {config.COLORS['primary']}, {config.COLORS['info']});
            color: white;
            text-align: center;
        }}
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar dengan navigasi dan info"""
    with st.sidebar:
        # Logo dan judul
        st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="color: {config.COLORS['primary']}; margin-bottom: 5px;">🏥</h1>
                <h3 style="color: {config.COLORS['primary']}; margin-top: 0;">{config.PAGE_TITLE}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Status aplikasi
        st.markdown("### 📊 Status Aplikasi")
        
        # Cek data yang diupload
        if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
            data_status = "✅ Data Tersedia"
            data_color = config.COLORS['success']
        else:
            data_status = "⚠️ Belum Ada Data"
            data_color = config.COLORS['warning']
        
        st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 4px solid {data_color}; margin: 10px 0;">
                <strong>{data_status}</strong>
            </div>
        """, unsafe_allow_html=True)
        
        # Info versi
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; color: #666; font-size: 12px; padding: 10px;">
                <strong>v1.0.0</strong><br>
                © 2024 Tim Pengembang
            </div>
        """, unsafe_allow_html=True)

def main():
    """Fungsi utama aplikasi"""
    # Setup halaman
    setup_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Header utama
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <h1 style="text-align: center; color: {config.COLORS['primary']};">
                🏥 {config.PAGE_TITLE}
            </h1>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tab navigasi
    tab_titles = [
        "🏠 Beranda",
        "📤 Upload Data", 
        "📅 Jadwal",
        "🧩 Kanban Drag",
        "⚙️ Preferensi",
        "ℹ️ Tentang"
    ]
    
    tabs = st.tabs(tab_titles)
    
    # Render masing-masing tab
    with tabs[0]:
        render_home()
    
    with tabs[1]:
        render_upload()
    
    with tabs[2]:
        render_schedule()
    
    with tabs[3]:
        render_kanban()
    
    with tabs[4]:
        render_preferences()
    
    with tabs[5]:
        render_about()
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
            <strong>{config.PAGE_TITLE}</strong> | 
            Sistem Manajemen Jadwal Dokter Terintegrasi
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
