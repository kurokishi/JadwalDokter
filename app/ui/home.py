"""
Halaman beranda aplikasi
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from ..config import config
from ..utils import show_message, create_metrics_card, calculate_statistics
from ..core import DataCleaner, ScheduleParser

def render():
    """Render halaman beranda"""
    st.header("🏠 Beranda")
    st.markdown("Selamat datang di Sistem Penjadwalan Dokter")
    
    # Card utama
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metrics_card(
            title="Total Dokter",
            value=st.session_state.get('total_doctors', 0),
            color=config.COLORS['primary']
        )
    
    with col2:
        create_metrics_card(
            title="Total Jadwal",
            value=st.session_state.get('total_schedules', 0),
            color=config.COLORS['success']
        )
    
    with col3:
        create_metrics_card(
            title="Jam Kerja",
            value=f"{st.session_state.get('total_hours', 0):.1f} jam",
            color=config.COLORS['warning']
        )
    
    with col4:
        conflict_count = len(st.session_state.get('conflicts', []))
        create_metrics_card(
            title="Konflik",
            value=conflict_count,
            color=config.COLORS['error'] if conflict_count > 0 else config.COLORS['success']
        )
    
    st.markdown("---")
    
    # Dua kolom utama
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Status data
        st.subheader("📊 Status Data")
        
        if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
            df = st.session_state.uploaded_data
            
            # Tampilkan statistik
            stats = calculate_statistics(df)
            
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid {config.COLORS['success']};">
                    <h4 style="margin-top: 0;">✅ Data Tersedia</h4>
                    <p><strong>File:</strong> {st.session_state.get('file_name', 'N/A')}</p>
                    <p><strong>Waktu Upload:</strong> {st.session_state.get('upload_time', 'N/A')}</p>
                    <p><strong>Ukuran Data:</strong> {len(df)} baris × {len(df.columns)} kolom</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan preview
            with st.expander("🔍 Preview Data", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
        
        else:
            st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 20px; border-radius: 10px; border-left: 4px solid {config.COLORS['warning']};">
                    <h4 style="margin-top: 0;">⚠️ Belum Ada Data</h4>
                    <p>Silakan upload data jadwal dokter terlebih dahulu di tab <strong>📤 Upload Data</strong></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Quick upload button
            if st.button("📥 Upload Data Sekarang", type="primary", use_container_width=True):
                st.switch_page("?tab=Upload%20Data")
    
    with col2:
        # Quick actions
        st.subheader("🚀 Aksi Cepat")
        
        # Action buttons
        if st.button("📋 Lihat Jadwal", use_container_width=True):
            st.switch_page("?tab=Jadwal")
        
        if st.button("🔄 Proses Data", use_container_width=True):
            if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
                with st.spinner("Memproses data..."):
                    # Process data
                    cleaner = DataCleaner()
                    df_clean = cleaner.clean_dataframe(st.session_state.uploaded_data)
                    
                    parser = ScheduleParser()
                    parsed_data = parser.parse_schedule_data(df_clean)
                    
                    # Update session state
                    st.session_state.schedule_data = parsed_data
                    st.session_state.total_doctors = parsed_data['statistics']['total_doctors']
                    st.session_state.total_schedules = parsed_data['statistics']['total_schedules']
                    st.session_state.total_hours = parsed_data['statistics']['total_hours']
                    st.session_state.conflicts = parsed_data['conflicts']
                    
                    show_message("Data berhasil diproses!", "success")
                    st.rerun()
            else:
                show_message("Tidak ada data untuk diproses", "error")
        
        if st.button("⚙️ Pengaturan", use_container_width=True):
            st.switch_page("?tab=Preferensi")
        
        if st.button("🆘 Bantuan", use_container_width=True):
            st.switch_page("?tab=Tentang")
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("📝 Aktivitas Terbaru")
        
        activities = []
        if st.session_state.get('upload_time'):
            activities.append(f"📤 Upload data: {st.session_state.upload_time}")
        
        if st.session_state.get('conflicts'):
            activities.append(f"⚠️ {len(st.session_state.conflicts)} konflik terdeteksi")
        
        if st.session_state.get('total_schedules', 0) > 0:
            activities.append(f"📅 {st.session_state.total_schedules} jadwal diproses")
        
        if activities:
            for activity in activities[:3]:  # Tampilkan 3 terakhir
                st.markdown(f"• {activity}")
        else:
            st.markdown("Belum ada aktivitas")
    
    # Informasi sistem
    st.markdown("---")
    st.subheader("ℹ️ Informasi Sistem")
    
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.markdown("**🕐 Waktu Kerja**")
        st.markdown(f"""
            - Mulai: {config.WORK_START.strftime('%H:%M')}
            - Selesai: {config.WORK_END.strftime('%H:%M')}
            - Istirahat: {config.LUNCH_START.strftime('%H:%M')} - {config.LUNCH_END.strftime('%H:%M')}
        """)
    
    with info_col2:
        st.markdown("**📅 Hari Kerja**")
        st.markdown(f"""
            - Senin - Jumat
            - Sabtu (opsional)
            - Minggu (libur)
        """)
    
    with info_col3:
        st.markdown("**📋 Fitur**")
        st.markdown("""
            - Upload Excel/CSV
            - Validasi otomatis
            - Deteksi konflik
            - Drag & drop scheduling
            - Export berbagai format
        """)
