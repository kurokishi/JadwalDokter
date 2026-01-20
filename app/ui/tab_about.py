"""
Tab tentang aplikasi
"""
import streamlit as st
from ..config import config

def render():
    """Render tab tentang"""
    st.header("ℹ️ Tentang Aplikasi")
    
    # Header dengan logo
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size: 60px; color: {config.COLORS['primary']}; margin: 0;">🏥</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            # {config.PAGE_TITLE}
            
            **Versi:** 1.0.0
            
            Sistem Manajemen Jadwal Dokter Terintegrasi
        """)
    
    st.markdown("---")
    
    # Deskripsi aplikasi
    st.subheader("🎯 Tujuan Aplikasi")
    
    st.markdown("""
    Aplikasi **Sistem Penjadwalan Dokter** dirancang untuk membantu rumah sakit, 
    klinik, dan fasilitas kesehatan lainnya dalam mengelola jadwal praktik dokter 
    secara efisien dan efektif.
    
    ### ✨ Fitur Utama:
    
    1. **📤 Upload Data Fleksibel**
       - Support Excel, CSV berbagai format
       - Validasi otomatis
       - Pembersihan data
    
    2. **📅 Manajemen Jadwal**
       - Visualisasi jadwal interaktif
       - Deteksi konflik otomatis
       - Filter dan pencarian
    
    3. **🧩 Penjadwalan Interaktif**
       - Drag & drop interface
       - Auto scheduling
       - Custom rules
    
    4. **📊 Analytics & Reporting**
       - Statistik lengkap
       - Chart interaktif
       - Export berbagai format
    
    5. **⚙️ Konfigurasi Lengkap**
       - Custom working hours
       - Specialization management
       - Theme customization
    """)
    
    st.markdown("---")
    
    # Teknologi yang digunakan
    st.subheader("🛠️ Teknologi")
    
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        st.markdown("""
            **Frontend:**
            - Streamlit
            - Plotly
            
            **Backend:**
            - Python 3.11
            - Pandas
            - NumPy
        """)
    
    with tech_col2:
        st.markdown("""
            **Data Processing:**
            - Pandas DataFrame
            - Custom parsers
            - Data validation
        """)
    
    st.markdown("---")
    
    # Panduan penggunaan
    st.subheader("📖 Panduan Cepat")
    
    with st.expander("🚀 Memulai", expanded=False):
        st.markdown("""
        1. **Upload Data** di tab Upload
        2. **Validasi** dan bersihkan data
        3. **Lihat Jadwal** di tab Jadwal
        4. **Atur Preferensi** jika perlu
        5. **Export** hasil jika sudah sesuai
        """)
    
    with st.expander("🔧 Troubleshooting", expanded=False):
        st.markdown("""
        **Masalah Upload:**
        - Pastikan format file sesuai
        - Cek ukuran file (max 20MB)
        - Pastikan kolom wajib ada
        
        **Masalah Tampilan:**
        - Refresh browser
        - Clear cache
        - Cek koneksi internet
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 20px;">
            <p>© 2024 Sistem Penjadwalan Dokter. Hak Cipta Dilindungi.</p>
            <p>Dikembangkan dengan ❤️ untuk dunia kesehatan Indonesia</p>
        </div>
    """, unsafe_allow_html=True)
