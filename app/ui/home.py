"""
Halaman beranda aplikasi
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from ..config import config
from ..utils import show_message, calculate_statistics
from ..core import DataCleaner, ScheduleParser

def render():
    """Render halaman beranda"""
    st.header("🏠 Beranda")
    st.markdown("Selamat datang di Sistem Penjadwalan Dokter")
    
    # Card utama
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Dokter",
            st.session_state.get('total_doctors', 0)
        )
    
    with col2:
        st.metric(
            "Total Jadwal",
            st.session_state.get('total_schedules', 0)
        )
    
    with col3:
        st.metric(
            "Jam Kerja",
            f"{st.session_state.get('total_hours', 0):.1f} jam"
        )
    
    with col4:
        conflict_count = len(st.session_state.get('conflicts', []))
        st.metric(
            "Konflik",
            conflict_count,
            delta="Perlu diperbaiki" if conflict_count > 0 else None,
            delta_color="inverse" if conflict_count > 0 else "normal"
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
            
            st.success("✅ Data Tersedia")
            st.write(f"**File:** {st.session_state.get('file_name', 'N/A')}")
            st.write(f"**Waktu Upload:** {st.session_state.get('upload_time', 'N/A')}")
            st.write(f"**Ukuran Data:** {len(df)} baris × {len(df.columns)} kolom")
            
            # Tampilkan preview
            with st.expander("🔍 Preview Data", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
        
        else:
            st.warning("⚠️ Belum Ada Data")
            st.write("Silakan upload data jadwal dokter terlebih dahulu di tab **📤 Upload Data**")
            
            # Quick upload button
            if st.button("📥 Upload Data Sekarang", type="primary", use_container_width=True):
                # Switch to upload tab
                st.session_state.current_view = 'upload'
                st.rerun()
    
    with col2:
        # Quick actions
        st.subheader("🚀 Aksi Cepat")
        
        # Action buttons
        if st.button("📋 Lihat Jadwal", use_container_width=True):
            st.session_state.current_view = 'schedule'
            st.rerun()
        
        if st.button("🔄 Proses Data", use_container_width=True):
            if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
                with st.spinner("Memproses data..."):
                    try:
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
                    except Exception as e:
                        show_message(f"Error processing data: {str(e)}", "error")
            else:
                show_message("Tidak ada data untuk diproses", "error")
        
        if st.button("⚙️ Pengaturan", use_container_width=True):
            st.session_state.current_view = 'preferences'
            st.rerun()
        
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
                st.write(f"• {activity}")
        else:
            st.write("Belum ada aktivitas")
