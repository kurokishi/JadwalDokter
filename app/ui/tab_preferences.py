"""
Tab untuk pengaturan preferensi
"""
import streamlit as st
from datetime import time
from ..config import config

def render():
    """Render tab preferensi"""
    st.header("⚙️ Preferensi dan Pengaturan")
    
    # Tabs untuk berbagai jenis pengaturan
    tab1, tab2, tab3 = st.tabs([
        "🕐 Waktu Kerja",
        "📅 Hari Kerja", 
        "🎨 Tampilan"
    ])
    
    with tab1:
        _render_work_time_settings()
    
    with tab2:
        _render_work_day_settings()
    
    with tab3:
        _render_display_settings()

def _render_work_time_settings():
    """Render pengaturan waktu kerja"""
    st.subheader("🕐 Pengaturan Waktu Kerja")
    
    # Current settings
    st.info(f"""
    **Pengaturan Saat Ini:**
    - Waktu Mulai: {config.WORK_START.strftime('%H:%M')}
    - Waktu Selesai: {config.WORK_END.strftime('%H:%M')}
    - Istirahat: {config.LUNCH_START.strftime('%H:%M')} - {config.LUNCH_END.strftime('%H:%M')}
    """)
    
    # Form untuk mengubah pengaturan
    with st.form("work_time_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_start = st.time_input(
                "Waktu Mulai Kerja",
                value=config.WORK_START,
                help="Waktu mulai praktik dokter"
            )
            
            new_lunch_start = st.time_input(
                "Waktu Mulai Istirahat",
                value=config.LUNCH_START,
                help="Waktu mulai istirahat siang"
            )
        
        with col2:
            new_end = st.time_input(
                "Waktu Selesai Kerja",
                value=config.WORK_END,
                help="Waktu selesai praktik dokter"
            )
            
            new_lunch_end = st.time_input(
                "Waktu Selesai Istirahat",
                value=config.LUNCH_END,
                help="Waktu selesai istirahat siang"
            )
        
        # Slot duration
        new_slot_duration = st.selectbox(
            "Durasi Slot Waktu",
            [15, 30, 45, 60, 90, 120],
            index=3,  # 60 minutes
            help="Durasi setiap slot penjadwalan dalam menit"
        )
        
        # Tombol submit
        if st.form_submit_button("💾 Simpan Pengaturan Waktu", type="primary"):
            # Update session state
            st.session_state['pref_work_start'] = new_start
            st.session_state['pref_work_end'] = new_end
            st.session_state['pref_lunch_start'] = new_lunch_start
            st.session_state['pref_lunch_end'] = new_lunch_end
            st.session_state['pref_slot_duration'] = new_slot_duration
            
            st.success("✅ Pengaturan waktu berhasil disimpan!")

def _render_work_day_settings():
    """Render pengaturan hari kerja"""
    st.subheader("📅 Pengaturan Hari Kerja")
    
    # Current settings
    st.info(f"""
    **Hari Kerja Saat Ini:**
    - Hari Kerja: {', '.join(config.WORK_DAYS)}
    """)
    
    # Form untuk mengubah hari kerja
    with st.form("work_day_form"):
        # Pilih hari kerja
        days_of_week = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        
        work_days = st.multiselect(
            "Pilih Hari Kerja",
            days_of_week,
            default=config.WORK_DAYS,
            help="Pilih hari dimana dokter tersedia untuk praktik"
        )
        
        # Special day settings
        st.markdown("### 🎯 Aturan Hari Kerja")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_work_days = st.slider(
                "Maksimal Hari Kerja per Dokter",
                min_value=1,
                max_value=7,
                value=6,
                help="Maksimal jumlah hari kerja dalam seminggu untuk satu dokter"
            )
        
        with col2:
            min_work_days = st.slider(
                "Minimal Hari Kerja per Dokter",
                min_value=1,
                max_value=5,
                value=1,
                help="Minimal jumlah hari kerja dalam seminggu untuk satu dokter"
            )
        
        # Tombol submit
        if st.form_submit_button("💾 Simpan Pengaturan Hari", type="primary"):
            # Update session state
            st.session_state['pref_work_days'] = work_days
            st.session_state['pref_max_work_days'] = max_work_days
            st.session_state['pref_min_work_days'] = min_work_days
            
            st.success("✅ Pengaturan hari berhasil disimpan!")

def _render_display_settings():
    """Render pengaturan tampilan"""
    st.subheader("🎨 Pengaturan Tampilan")
    
    # Theme settings
    st.markdown("### 🎨 Tema dan Warna")
    
    col1, col2 = st.columns(2)
    
    with col1:
        primary_color = st.color_picker(
            "Warna Primer",
            value=config.COLORS['primary'],
            help="Warna utama untuk tombol dan header"
        )
    
    with col2:
        secondary_color = st.color_picker(
            "Warna Sekunder",
            value=config.COLORS['secondary'],
            help="Warna kedua untuk aksen"
        )
    
    # Layout settings
    st.markdown("### 📐 Layout")
    
    layout_option = st.radio(
        "Layout Halaman",
        ["Wide", "Centered"],
        horizontal=True,
        index=0 if config.LAYOUT == "wide" else 1
    )
    
    # Save button
    if st.button("💾 Simpan Pengaturan Tampilan", type="primary"):
        # Update session state
        st.session_state['pref_primary_color'] = primary_color
        st.session_state['pref_secondary_color'] = secondary_color
        st.session_state['pref_layout'] = layout_option.lower()
        
        st.success("✅ Pengaturan tampilan berhasil disimpan!")
