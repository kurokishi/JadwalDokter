"""
Tab untuk menampilkan dan mengatur jadwal
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
import numpy as np
from ..config import config
from ..utils import show_message, format_time, get_unique_values
from ..core import ScheduleParser

def render():
    """Render tab jadwal"""
    st.header("📅 Jadwal Dokter")
    
    # Cek jika ada data
    if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
        st.warning("⚠️ Tidak ada data jadwal. Silakan upload data terlebih dahulu di tab **📤 Upload Data**")
        return
    
    df = st.session_state.uploaded_data
    
    # Parse data jika belum diparse
    if 'schedule_data' not in st.session_state or st.session_state.schedule_data is None:
        with st.spinner("Memproses data jadwal..."):
            parser = ScheduleParser()
            parsed_data = parser.parse_schedule_data(df)
            st.session_state.schedule_data = parsed_data
    
    parsed_data = st.session_state.schedule_data
    
    # Filter controls
    st.subheader("🔍 Filter Jadwal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        doctors = get_unique_values(df, 'nama_dokter')
        selected_doctor = st.selectbox(
            "Pilih Dokter",
            ["Semua"] + doctors,
            help="Filter berdasarkan dokter"
        )
    
    with col2:
        specializations = get_unique_values(df, 'spesialisasi')
        selected_specialization = st.selectbox(
            "Pilih Spesialisasi",
            ["Semua"] + specializations,
            help="Filter berdasarkan spesialisasi"
        )
    
    with col3:
        days = get_unique_values(df, 'hari')
        selected_day = st.selectbox(
            "Pilih Hari",
            ["Semua"] + days,
            help="Filter berdasarkan hari"
        )
    
    # Apply filters
    filtered_schedules = parsed_data['schedules']
    
    if selected_doctor != "Semua":
        filtered_schedules = [s for s in filtered_schedules if s['doctor'] == selected_doctor]
    
    if selected_specialization != "Semua":
        filtered_schedules = [s for s in filtered_schedules if s['specialization'] == selected_specialization]
    
    if selected_day != "Semua":
        filtered_schedules = [s for s in filtered_schedules if s['day'] == selected_day]
    
    # Tampilkan statistik
    st.markdown("---")
    st.subheader("📊 Statistik Jadwal")
    
    total_schedules = len(filtered_schedules)
    total_doctors = len(set(s['doctor'] for s in filtered_schedules))
    total_hours = sum(s['duration'] for s in filtered_schedules)
    avg_duration = total_hours / total_schedules if total_schedules > 0 else 0
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("Total Jadwal", total_schedules)
    
    with stat_col2:
        st.metric("Total Dokter", total_doctors)
    
    with stat_col3:
        st.metric("Total Jam", f"{total_hours:.1f}")
    
    with stat_col4:
        st.metric("Rata-rata Durasi", f"{avg_duration:.1f} jam")
    
    # Tampilan jadwal
    st.markdown("---")
    
    view_option = st.radio(
        "Tampilan Jadwal",
        ["Tabel", "Per Hari", "Per Dokter"],
        horizontal=True
    )
    
    if view_option == "Tabel":
        _render_table_view(filtered_schedules)
    elif view_option == "Per Hari":
        _render_day_view(filtered_schedules)
    elif view_option == "Per Dokter":
        _render_doctor_view(parsed_data, selected_doctor if selected_doctor != "Semua" else None)

def _render_table_view(schedules):
    """Render tampilan tabel"""
    if not schedules:
        st.info("Tidak ada jadwal yang sesuai dengan filter")
        return
    
    # Buat DataFrame untuk ditampilkan
    table_data = []
    for schedule in schedules:
        table_data.append({
            'Dokter': schedule['doctor'],
            'Spesialisasi': schedule['specialization'],
            'Hari': schedule['day'],
            'Mulai': schedule['start_str'],
            'Selesai': schedule['end_str'],
            'Durasi': f"{schedule['duration']:.1f} jam",
            'Ruangan': schedule.get('room', ''),
            'Poliklinik': schedule.get('clinic', '')
        })
    
    df_display = pd.DataFrame(table_data)
    
    # Tampilkan tabel
    st.dataframe(df_display, use_container_width=True)

def _render_day_view(schedules):
    """Render tampilan per hari"""
    if not schedules:
        st.info("Tidak ada jadwal yang sesuai dengan filter")
        return
    
    # Group by day
    days = sorted(set(s['day'] for s in schedules))
    
    for day in days:
        day_schedules = [s for s in schedules if s['day'] == day]
        
        with st.expander(f"📅 {day} ({len(day_schedules)} jadwal)", expanded=False):
            # Sort by start time
            day_schedules.sort(key=lambda x: x['start_time'])
            
            for schedule in day_schedules:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{schedule['doctor']}**")
                    st.caption(f"{schedule['specialization']}")
                
                with col2:
                    st.markdown(f"**{schedule['start_str']} - {schedule['end_str']}**")
                    st.caption(f"{schedule['duration']:.1f} jam")
                
                with col3:
                    if schedule.get('room'):
                        st.markdown(f"📍 {schedule['room']}")

def _render_doctor_view(parsed_data, selected_doctor=None):
    """Render tampilan per dokter"""
    doctors_data = parsed_data.get('doctors', {})
    
    if not doctors_data:
        st.info("Tidak ada data dokter")
        return
    
    if selected_doctor:
        # Tampilkan detail dokter yang dipilih
        if selected_doctor in doctors_data:
            doctor_info = doctors_data[selected_doctor]
            
            # Tampilkan info dokter
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"**Dokter:** {selected_doctor}")
                st.markdown(f"**Spesialisasi:** {doctor_info['specialization']}")
                st.markdown(f"**Total Jam:** {doctor_info['total_hours']:.1f} jam/minggu")
                st.markdown(f"**Hari Kerja:** {len(doctor_info['days'])} hari")
            
            with col2:
                # Jadwal per hari
                st.subheader("Jadwal per Hari")
                
                days = sorted(doctor_info['days'])
                for day in days:
                    day_schedules = [s for s in doctor_info['schedules'] if s['day'] == day]
                    
                    if day_schedules:
                        st.markdown(f"**{day}**")
                        
                        for schedule in day_schedules:
                            st.markdown(f"• {schedule['start_str']} - {schedule['end_str']} ({schedule['duration']:.1f} jam)")
    else:
        # Tampilkan semua dokter
        for doctor, doctor_info in doctors_data.items():
            with st.expander(f"👨‍⚕️ {doctor} ({doctor_info['specialization']})", expanded=False):
                st.markdown(f"**Total Jam:** {doctor_info['total_hours']:.1f} jam")
                st.markdown(f"**Hari Kerja:** {', '.join(sorted(doctor_info['days']))}")
                
                # Jadwal singkat
                day_schedules = {}
                for schedule in doctor_info['schedules']:
                    day = schedule['day']
                    if day not in day_schedules:
                        day_schedules[day] = []
                    day_schedules[day].append(schedule)
                
                for day, schedules in day_schedules.items():
                    st.markdown(f"**{day}:** {len(schedules)} jadwal")
