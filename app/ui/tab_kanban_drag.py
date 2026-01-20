"""
Tab untuk drag & drop scheduling (simplified version)
"""
import streamlit as st
import pandas as pd
from datetime import datetime, time
import random
from ..config import config

def render():
    """Render tab kanban drag (simplified)"""
    st.header("🧩 Kanban Drag & Drop")
    
    # Informasi bahwa ini adalah versi simplified
    st.info("""
    **⚠️ Note:** Ini adalah versi simplified dari fitur Kanban Drag & Drop.
    Fitur lengkap membutuhkan library tambahan untuk drag & drop interaktif.
    """)
    
    # Cek jika ada data
    if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
        st.warning("⚠️ Tidak ada data jadwal. Silakan upload data terlebih dahulu di tab **📤 Upload Data**")
        return
    
    # Pilih mode
    mode = st.radio(
        "Mode Penjadwalan",
        ["👀 View Only", "✏️ Edit Manual"],
        horizontal=True
    )
    
    if mode == "👀 View Only":
        _render_view_mode()
    elif mode == "✏️ Edit Manual":
        _render_edit_mode()

def _render_view_mode():
    """Render view mode"""
    df = st.session_state.uploaded_data
    
    # Pilih dokter untuk dilihat
    doctors = sorted(df['nama_dokter'].unique()) if 'nama_dokter' in df.columns else []
    
    if not doctors:
        st.error("Tidak ada data dokter")
        return
    
    selected_doctor = st.selectbox("Pilih Dokter", doctors)
    
    if selected_doctor:
        # Filter data untuk dokter yang dipilih
        doctor_data = df[df['nama_dokter'] == selected_doctor]
        
        # Tampilkan dalam format kanban sederhana
        st.subheader(f"📋 Jadwal Dr. {selected_doctor}")
        
        # Group by hari
        days = config.WORK_DAYS
        
        cols = st.columns(len(days))
        
        for idx, day in enumerate(days):
            with cols[idx]:
                st.markdown(f"**{day}**")
                
                # Filter jadwal untuk hari ini
                day_schedules = doctor_data[doctor_data['hari'] == day]
                
                if day_schedules.empty:
                    st.markdown("""
                        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; text-align: center; color: #999; min-height: 100px;">
                            Tidak ada jadwal
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    for _, schedule in day_schedules.iterrows():
                        start_time = str(schedule.get('jam_mulai', ''))
                        end_time = str(schedule.get('jam_selesai', ''))
                        room = str(schedule.get('ruangan', ''))
                        
                        st.markdown(f"""
                            <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid {config.COLORS['primary']};">
                                <strong>{start_time} - {end_time}</strong><br>
                                {f"<small>📍 {room}</small>" if room else ''}
                            </div>
                        """, unsafe_allow_html=True)

def _render_edit_mode():
    """Render edit mode manual"""
    st.subheader("✏️ Edit Jadwal Manual")
    
    df = st.session_state.uploaded_data
    
    # Pilih dokter untuk diedit
    doctors = sorted(df['nama_dokter'].unique()) if 'nama_dokter' in df.columns else []
    
    if not doctors:
        st.error("Tidak ada data dokter")
        return
    
    selected_doctor = st.selectbox("Pilih Dokter untuk Diedit", doctors, key="edit_doctor")
    
    if selected_doctor:
        # Tampilkan form sederhana untuk edit
        st.markdown(f"### Edit Jadwal untuk {selected_doctor}")
        
        # Form untuk menambah jadwal baru
        with st.form("add_schedule_form
