"""
About page UI
"""
import streamlit as st
from app.config import AppConfig


def show_about():
    """Display about page"""
    
    st.title("ℹ️ Tentang Aplikasi")
    
    # App info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        ### {AppConfig().APP_NAME} v{AppConfig().VERSION}
        
        Aplikasi untuk mengkonversi format jadwal dokter dari `jadwal_hafis.xlsx` 
        ke format grid `jadwal_hasil.xlsx`.
        
        **Fitur Utama:**
        • Parsing file Excel dengan formula complex
        • Konversi otomatis ke format time slot grid
        • Export dengan formatting profesional
        • Filtering dan searching data
        • Visualisasi data jadwal
        
        **Teknologi:**
        • Python 3.11+
        • Streamlit untuk UI
        • Pandas untuk data processing
        • Openpyxl untuk Excel generation
        """)
    
    with col2:
        st.image("https://via.placeholder.com/300x200/4F46E5/FFFFFF?text=Jadwal+Dokter", 
                caption=AppConfig().APP_NAME)
    
    # How to use
    st.markdown("## 📖 Cara Penggunaan")
    
    steps = [
        {
            "title": "1. Upload File",
            "description": "Upload file Excel dengan format jadwal_hafis.xlsx"
        },
        {
            "title": "2. Parsing Data", 
            "description": "Sistem akan parsing data termasuk formula Excel"
        },
        {
            "title": "3. Konversi Grid",
            "description": "Data dikonversi ke format time slot grid"
        },
        {
            "title": "4. Download Hasil",
            "description": "Download file hasil dalam format Excel yang rapi"
        }
    ]
    
    for step in steps:
        with st.expander(step["title"], expanded=True):
            st.write(step["description"])
    
    # Contact & Support
    st.markdown("## 📞 Kontak & Support")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Untuk bantuan:**
        - Email: support@jadwaldokter.com
        - Telepon: 021-12345678
        - Jam kerja: Senin-Jumat, 08:00-17:00
        
        **Laporan Bug:**
        Jika menemukan bug atau masalah, silakan laporkan melalui email.
        """)
    
    with col2:
        st.markdown("""
        **Update & Versi:**
        - Versi saat ini: v{AppConfig().VERSION}
        - Terakhir update: {st.session_state.get('last_update', '2024-01-01')}
        
        **Lisensi:**
        Aplikasi ini dikembangkan untuk penggunaan internal.
        """)
    
    # System requirements
    st.markdown("## ⚙️ System Requirements")
    
    st.markdown("""
    **Minimum:**
    - Python 3.11+
    - RAM: 4GB
    - Storage: 500MB
    
    **Recommended:**
    - Python 3.12+
    - RAM: 8GB
    - Storage: 1GB
    """)
    
    # Credits
    st.markdown("## 👥 Credits")
    
    st.markdown("""
    **Developer Team:**
    - Project Manager: [Nama PM]
    - Lead Developer: [Nama Developer]
    - UI/UX Designer: [Nama Designer]
    - QA Tester: [Nama Tester]
    
    **Teknologi:**
    - Streamlit: Untuk web interface
    - Pandas: Untuk data processing
    - Openpyxl: Untuk Excel operations
    - Plotly: Untuk visualisasi data
    """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #6B7280;'>
    <p>© 2024 {AppConfig().APP_NAME}. Hak cipta dilindungi undang-undang.</p>
    <p>Versi: {AppConfig().VERSION} | Build: {st.session_state.get('build_date', '2024-01-01')}</p>
    </div>
    """, unsafe_allow_html=True)
