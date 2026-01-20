"""
Home tab UI component
"""
import streamlit as st
import pandas as pd
from app.config import AppConfig

def display_home_tab():
    """Display home tab content"""
    
    # Hero section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; color: white; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">🏥 Jadwal Dokter RS</h1>
            <p style="font-size: 1.2rem;">Aplikasi Manajemen Jadwal Dokter Rumah Sakit</p>
            <p style="font-size: 1rem; opacity: 0.9;">Versi {}</p>
        </div>
        """.format(AppConfig.APP_VERSION), unsafe_allow_html=True)
    
    # Features
    st.subheader("✨ Fitur Utama")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="padding: 1.5rem; background-color: #f8f9fa; border-radius: 10px; height: 200px;">
            <h3>📤 Upload Data</h3>
            <p>Unggah file Excel/CSV termasuk format <strong>jadwal_hafis.xlsx</strong></p>
            <ul>
                <li>Support format khusus RS</li>
                <li>Validasi otomatis</li>
                <li>Preview data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 1.5rem; background-color: #f8f9fa; border-radius: 10px; height: 200px;">
            <h3>📅 Jadwal Dokter</h3>
            <p>Lihat dan kelola jadwal dokter</p>
            <ul>
                <li>Tampilan tabel</li>
                <li>Filter per hari/spesialis</li>
                <li>Visualisasi timeline</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="padding: 1.5rem; background-color: #f8f9fa; border-radius: 10px; height: 200px;">
            <h3>🧩 Kanban Drag</h3>
            <p>Sistem penjadwalan drag & drop</p>
            <ul>
                <li>Antarmuka visual</li>
                <li>Drag dokter ke timeslot</li>
                <li>Simpan perubahan</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide
    st.subheader("🚀 Mulai Cepat")
    
    with st.expander("Panduan Penggunaan", expanded=True):
        st.markdown("""
        ### Langkah 1: Upload Data
        1. Pergi ke tab **"Upload Data"**
        2. Unggah file Excel/CSV
        3. Untuk file **jadwal_hafis.xlsx**, system akan otomatis mengenali format
        
        ### Langkah 2: Lihat Jadwal
        1. Pergi ke tab **"Jadwal Dokter"**
        2. Pilih view yang diinginkan
        3. Filter berdasarkan hari/spesialisasi
        
        ### Langkah 3: Kelola Jadwal
        1. Gunakan **"Kanban Drag"** untuk penjadwalan visual
        2. Atur preferensi di **"Preferences"**
        3. Export data jika diperlukan
        """)
    
    # File format support
    st.subheader("📁 Format File yang Didukung")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Format Standar
        ```
        doctor_name,specialty,day,working_hours
        Dr. John Doe,Cardiology,Monday,08:00-16:00
        Dr. Jane Smith,Pediatrics,Tuesday,09:00-17:00
        ```
        """)
    
    with col2:
        st.markdown("""
        ### Format jadwal_hafis.xlsx
        ```
        KSM | Nama dokter | POLI | SENIN | SELASA | ...
        Anak | dr. Debby | JAM KERJA | 07:30-14:00 | 07:30-14:00
          |   | REGULER | [Reference] | [Reference]
          |   | EKSEKUTIF | 10:30-11:25 | 10:35-11:30
        ```
        """)
    
    # Stats if data loaded
    if 'data' in st.session_state and st.session_state.data_loaded:
        st.subheader("📊 Data Saat Ini")
        
        df = st.session_state.data
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Data", len(df))
        with col2:
            st.metric("Jumlah Dokter", len(df['doctor_name'].unique()))
        with col3:
            st.metric("Spesialisasi", len(df['specialty'].unique()))
        with col4:
            days = len(df['day'].unique()) if 'day' in df.columns else 0
            st.metric("Hari", days)
    
    # Quick actions
    st.subheader("⚡ Aksi Cepat")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload Data", use_container_width=True):
            st.switch_page("run.py")  # This will need adjustment based on navigation
    
    with col2:
        if st.button("📅 Lihat Jadwal", use_container_width=True) and st.session_state.data_loaded:
            st.switch_page("run.py")
    
    with col3:
        if st.button("⚙️ Pengaturan", use_container_width=True):
            st.switch_page("run.py")
