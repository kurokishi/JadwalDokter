"""
Home page UI
"""
import streamlit as st
from app.config import AppConfig


def show_home():
    """Display home page"""
    
    # Custom CSS for home page
    st.markdown("""
    <style>
    .home-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .home-subheader {
        font-size: 1.5rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 3rem;
    }
    .feature-card {
        background-color: #F9FAFB;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #4F46E5;
        margin-bottom: 1rem;
    }
    .step-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #E5E7EB;
        text-align: center;
        height: 100%;
    }
    .step-number {
        background-color: #4F46E5;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        font-weight: bold;
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="home-header">🏥 Jadwal Dokter Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="home-subheader">Konversi otomatis format jadwal dari jadwal_hafis.xlsx ke jadwal_hasil.xlsx</p>', unsafe_allow_html=True)
    
    # Features
    st.markdown("## ✨ Fitur Utama")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h3>📤 Upload Mudah</h3>
        <p>Upload file Excel dengan format jadwal_hafis.xlsx</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
        <h3>🔄 Konversi Otomatis</h3>
        <p>Konversi ke format grid time slot secara otomatis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
        <h3>💾 Export Profesional</h3>
        <p>Download hasil dengan formatting Excel yang rapi</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works
    st.markdown("## 🔧 Cara Kerja")
    
    cols = st.columns(4)
    
    with cols[0]:
        st.markdown("""
        <div class="step-card">
        <div class="step-number">1</div>
        <h4>Upload File</h4>
        <p>Upload jadwal_hafis.xlsx</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("""
        <div class="step-card">
        <div class="step-number">2</div>
        <h4>Parsing Data</h4>
        <p>Sistem parsing formula Excel</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown("""
        <div class="step-card">
        <div class="step-number">3</div>
        <h4>Konversi Grid</h4>
        <p>Generate time slot grid</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown("""
        <div class="step-card">
        <div class="step-number">4</div>
        <h4>Download Hasil</h4>
        <p>Export jadwal_hasil.xlsx</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Start
    st.markdown("---")
    st.markdown("## 🚀 Mulai Sekarang")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("""
        ### Siap mengkonversi jadwal Anda?
        Upload file Excel Anda dan dapatkan hasil dalam format grid yang rapi.
        """)
    
    with col2:
        if st.button("🔄 Mulai Konversi", use_container_width=True, type="primary"):
            st.session_state['current_page'] = 'upload'
            st.rerun()
    
    with col3:
        # Template download
        st.download_button(
            label="📥 Download Template",
            data="",  # Placeholder - actual template should be loaded from file
            file_name="jadwal_hafis_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # Format comparison
    st.markdown("---")
    st.markdown("## 📊 Perbandingan Format")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Format Input
        **jadwal_hafis.xlsx**
        ```
        | KSM | Dokter | POLI | SENIN | ... |
        |-----|--------|------|-------|-----|
        | Anak | dr. Debby... | JAM KERJA | 07:30-14:00 | ... |
        |     |        | REGULER | =[1]ANAK!T4 | ... |
        |     |        | EKSEKUTIF | 10.30-11.25 | ... |
        ```
        
        **Fitur:**
        • Baris terpisah per tipe
        • Formula Excel
        • Time range per hari
        • Format fleksibel
        """)
    
    with col2:
        st.markdown("""
        ### Format Output
        **jadwal_hasil.xlsx**
        ```
        | POLI | JENIS | HARI | DOKTER | JAM | 07:00 | 07:30 | ... |
        |------|-------|------|--------|-----|-------|-------|-----|
        | Anak | Reguler | Senin | dr. Debby... | 11:00-13:00 | | R | ... |
        ```
        
        **Fitur:**
        • Satu baris per kombinasi
        • Time slot grid (07:00-14:00)
        • R/E untuk Reguler/Eksekutif
        • Format standar
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #6B7280; margin-top: 3rem;'>
    <p><strong>Jadwal Dokter Converter v{AppConfig().VERSION}</strong></p>
    <p>© {st.session_state.get('current_year', 2024)} - Sistem konversi jadwal dokter otomatis</p>
    </div>
    """, unsafe_allow_html=True)
