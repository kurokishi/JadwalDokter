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
        st.image("https://cdn-icons-png.flaticon.com/512/3059/3059520.png", width=150)
    
    with col2:
        st.markdown(f"""
            # {config.PAGE_TITLE}
            
            **Versi:** {config.__version__}
            
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
    
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("""
            **Frontend:**
            - Streamlit
            - Plotly
            - HTML/CSS
            
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
            
            **Deployment:**
            - Streamlit Cloud
            - Docker ready
            - CI/CD compatible
        """)
    
    with tech_col3:
        st.markdown("""
            **Features:**
            - Responsive design
            - Real-time updates
            - Session management
            - Error handling
        """)
    
    st.markdown("---")
    
    # Tim pengembang
    st.subheader("👥 Tim Pengembang")
    
    dev_col1, dev_col2, dev_col3 = st.columns(3)
    
    with dev_col1:
        st.markdown("""
            **Lead Developer**
            - Arsitektur sistem
            - Core logic
            - Deployment
        """)
    
    with dev_col2:
        st.markdown("""
            **UI/UX Designer**
            - User interface
            - User experience
            - Visual design
        """)
    
    with dev_col3:
        st.markdown("""
            **Data Analyst**
            - Data validation
            - Business logic
            - Analytics
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
        
        **Masalah Data:**
        - Validasi error akan ditampilkan
        - Perbaiki data di source
        - Gunakan template yang disediakan
        """)
    
    with st.expander("📞 Kontak & Support", expanded=False):
        st.markdown("""
        **Untuk bantuan dan support:**
        
        - **Email:** support@jadwaldokter.app
        - **Website:** www.jadwaldokter.app
        - **Documentation:** docs.jadwaldokter.app
        
        **Jam Operasional Support:**
        - Senin - Jumat: 08:00 - 17:00
        - Sabtu: 08:00 - 12:00
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; color: #666; padding: 20px;">
            <p>© 2024 {config.PAGE_TITLE}. Hak Cipta Dilindungi.</p>
            <p>Dikembangkan dengan ❤️ untuk dunia kesehatan Indonesia</p>
        </div>
    """, unsafe_allow_html=True)
