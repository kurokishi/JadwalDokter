"""
Tab untuk pengaturan preferensi
"""
import streamlit as st
import json
from datetime import time
from ..config import config

def render():
    """Render tab preferensi"""
    st.header("⚙️ Preferensi dan Pengaturan")
    
    # Tabs untuk berbagai jenis pengaturan
    tab1, tab2, tab3, tab4 = st.tabs([
        "🕐 Waktu Kerja",
        "📅 Hari Kerja", 
        "🎨 Tampilan",
        "🔧 Sistem"
    ])
    
    with tab1:
        _render_work_time_settings()
    
    with tab2:
        _render_work_day_settings()
    
    with tab3:
        _render_display_settings()
    
    with tab4:
        _render_system_settings()

def _render_work_time_settings():
    """Render pengaturan waktu kerja"""
    st.subheader("🕐 Pengaturan Waktu Kerja")
    
    # Current settings
    st.info(f"""
    **Pengaturan Saat Ini:**
    - Waktu Mulai: {config.WORK_START.strftime('%H:%M')}
    - Waktu Selesai: {config.WORK_END.strftime('%H:%M')}
    - Istirahat: {config.LUNCH_START.strftime('%H:%M')} - {config.LUNCH_END.strftime('%H:%M')}
    - Durasi Slot: {config.TIME_SLOT_DURATION} menit
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
            index=[15, 30, 45, 60, 90, 120].index(config.TIME_SLOT_DURATION) 
            if config.TIME_SLOT_DURATION in [15, 30, 45, 60, 90, 120] else 3,
            help="Durasi setiap slot penjadwalan dalam menit"
        )
        
        # Tombol submit
        if st.form_submit_button("💾 Simpan Pengaturan Waktu", type="primary"):
            # Update session state (in real app, would save to config file)
            st.session_state['pref_work_start'] = new_start
            st.session_state['pref_work_end'] = new_end
            st.session_state['pref_lunch_start'] = new_lunch_start
            st.session_state['pref_lunch_end'] = new_lunch_end
            st.session_state['pref_slot_duration'] = new_slot_duration
            
            st.success("✅ Pengaturan waktu berhasil disimpan!")
            st.rerun()

def _render_work_day_settings():
    """Render pengaturan hari kerja"""
    st.subheader("📅 Pengaturan Hari Kerja")
    
    # Current settings
    st.info(f"""
    **Hari Kerja Saat Ini:**
    - Hari Kerja: {', '.join(config.WORK_DAYS)}
    - Weekend: {', '.join(config.WEEKEND)}
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
        
        # Weekend handling
        weekend_days = st.multiselect(
            "Hari Weekend (Opsional)",
            days_of_week,
            default=config.WEEKEND,
            help="Hari yang dianggap sebagai weekend (biasanya Sabtu/Minggu)"
        )
        
        # Special day settings
        st.markdown("### 🎯 Hari Khusus")
        
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
            st.session_state['pref_weekend_days'] = weekend_days
            st.session_state['pref_max_work_days'] = max_work_days
            st.session_state['pref_min_work_days'] = min_work_days
            
            st.success("✅ Pengaturan hari berhasil disimpan!")
            st.rerun()

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
        
        success_color = st.color_picker(
            "Warna Success",
            value=config.COLORS['success'],
            help="Warna untuk indikator sukses"
        )
    
    with col2:
        secondary_color = st.color_picker(
            "Warna Sekunder",
            value=config.COLORS['secondary'],
            help="Warna kedua untuk aksen"
        )
        
        warning_color = st.color_picker(
            "Warna Warning",
            value=config.COLORS['warning'],
            help="Warna untuk peringatan"
        )
    
    # Specialization colors
    st.markdown("### 🏥 Warna Spesialisasi")
    
    # Display current specialization colors
    specializations = list(config.SPECIALIZATION_COLORS.keys())
    
    specialization_colors = {}
    for spec in specializations:
        current_color = config.SPECIALIZATION_COLORS.get(spec, "#CCCCCC")
        new_color = st.color_picker(
            f"Warna {spec}",
            value=current_color,
            key=f"color_{spec}"
        )
        specialization_colors[spec] = new_color
    
    # Layout settings
    st.markdown("### 📐 Layout")
    
    layout_option = st.radio(
        "Layout Halaman",
        ["Wide", "Centered", "Narrow"],
        horizontal=True,
        index=["Wide", "Centered", "Narrow"].index(config.LAYOUT.capitalize()) 
        if config.LAYOUT.capitalize() in ["Wide", "Centered", "Narrow"] else 0
    )
    
    # Save button
    if st.button("💾 Simpan Pengaturan Tampilan", type="primary"):
        # Update session state
        st.session_state['pref_primary_color'] = primary_color
        st.session_state['pref_secondary_color'] = secondary_color
        st.session_state['pref_success_color'] = success_color
        st.session_state['pref_warning_color'] = warning_color
        st.session_state['pref_specialization_colors'] = specialization_colors
        st.session_state['pref_layout'] = layout_option.lower()
        
        st.success("✅ Pengaturan tampilan berhasil disimpan!")
        st.rerun()

def _render_system_settings():
    """Render pengaturan sistem"""
    st.subheader("🔧 Pengaturan Sistem")
    
    # File settings
    st.markdown("### 📁 Pengaturan File")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_file_size = st.number_input(
            "Ukuran File Maksimum (MB)",
            min_value=1,
            max_value=100,
            value=config.MAX_FILE_SIZE_MB,
            help="Ukuran maksimum file yang bisa diupload"
        )
        
        default_encoding = st.selectbox(
            "Encoding Default",
            ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252'],
            index=0,
            help="Encoding default untuk file CSV"
        )
    
    with col2:
        allowed_extensions = st.multiselect(
            "Ekstensi File yang Diizinkan",
            ['.xlsx', '.xls', '.csv', '.xlsm', '.txt'],
            default=config.ALLOWED_EXTENSIONS,
            help="Jenis file yang bisa diupload"
        )
    
    # Validation settings
    st.markdown("### ✅ Pengaturan Validasi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_duration = st.number_input(
            "Durasi Minimum (jam)",
            min_value=0.1,
            max_value=8.0,
            value=0.5,
            step=0.1,
            help="Durasi minimum untuk satu jadwal"
        )
        
        validate_on_upload = st.checkbox(
            "Validasi Otomatis saat Upload",
            value=True,
            help="Validasi data secara otomatis saat file diupload"
        )
    
    with col2:
        max_duration = st.number_input(
            "Durasi Maksimum (jam)",
            min_value=1.0,
            max_value=24.0,
            value=12.0,
            step=0.5,
            help="Durasi maksimum untuk satu jadwal"
        )
        
        auto_clean_data = st.checkbox(
            "Bersihkan Data Otomatis",
            value=True,
            help="Bersihkan data secara otomatis setelah upload"
        )
    
    # Reset button
    st.markdown("---")
    st.markdown("### 🔄 Reset Pengaturan")
    
    if st.button("🔄 Reset ke Default", type="secondary"):
        # Reset logic here
        st.warning("""
        **Perhatian:** Ini akan mengembalikan semua pengaturan ke nilai default.
        Data yang sudah diupload tidak akan terpengaruh.
        """)
        
        if st.button("✅ Ya, Reset Sekarang", type="primary"):
            # Reset session state preferences
            for key in list(st.session_state.keys()):
                if key.startswith('pref_'):
                    del st.session_state[key]
            
            st.success("✅ Pengaturan berhasil direset ke default!")
            st.rerun()
    
    # Save all settings
    if st.button("💾 Simpan Semua Pengaturan", type="primary"):
        # Save all preferences
        preferences = {
            'file_settings': {
                'max_file_size': max_file_size,
                'allowed_extensions': allowed_extensions,
                'default_encoding': default_encoding
            },
            'validation_settings': {
                'min_duration': min_duration,
                'max_duration': max_duration,
                'validate_on_upload': validate_on_upload,
                'auto_clean_data': auto_clean_data
            }
        }
        
        st.session_state['preferences'] = preferences
        st.success("✅ Semua pengaturan berhasil disimpan!")
