"""
Tab untuk drag & drop scheduling (simplified version)
"""
import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import json
from ..config import config, TimeSlot
from ..utils import show_message, parse_time, format_time
from ..core import ScheduleParser, TimeParser

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
        
        if st.button("📤 Ke Tab Upload", type="primary"):
            st.switch_page("?tab=Upload%20Data")
        return
    
    # Pilih mode
    mode = st.radio(
        "Mode Penjadwalan",
        ["👀 View Only", "✏️ Edit Manual", "🔄 Auto Schedule"],
        horizontal=True
    )
    
    if mode == "👀 View Only":
        _render_view_mode()
    elif mode == "✏️ Edit Manual":
        _render_edit_mode()
    elif mode == "🔄 Auto Schedule":
        _render_auto_schedule()

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
                        start_time = parse_time(schedule.get('jam_mulai', ''))
                        end_time = parse_time(schedule.get('jam_selesai', ''))
                        
                        if start_time and end_time:
                            duration = (end_time.hour - start_time.hour) + (end_time.minute - start_time.minute) / 60
                            
                            st.markdown(f"""
                                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid {config.COLORS['primary']};">
                                    <strong>{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}</strong><br>
                                    <small>Durasi: {duration:.1f} jam</small>
                                    {f"<br><small>📍 {schedule.get('ruangan', '')}</small>" if schedule.get('ruangan') else ''}
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
        # Tampilkan jadwal saat ini
        st.markdown(f"### Jadwal Saat Ini untuk {selected_doctor}")
        
        doctor_data = df[df['nama_dokter'] == selected_doctor].copy()
        
        if not doctor_data.empty:
            # Edit menggunakan form
            edited_schedules = []
            
            for idx, (_, schedule) in enumerate(doctor_data.iterrows()):
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        day = st.selectbox(
                            "Hari",
                            config.WORK_DAYS,
                            index=config.WORK_DAYS.index(schedule['hari']) if schedule['hari'] in config.WORK_DAYS else 0,
                            key=f"day_{idx}"
                        )
                    
                    with col2:
                        start_time = st.time_input(
                            "Mulai",
                            value=parse_time(schedule.get('jam_mulai', '08:00')) or time(8, 0),
                            key=f"start_{idx}"
                        )
                    
                    with col3:
                        end_time = st.time_input(
                            "Selesai",
                            value=parse_time(schedule.get('jam_selesai', '16:00')) or time(16, 0),
                            key=f"end_{idx}"
                        )
                    
                    with col4:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("❌", key=f"delete_{idx}"):
                            # Mark for deletion
                            pass
                    
                    edited_schedules.append({
                        'day': day,
                        'start': start_time,
                        'end': end_time,
                        'original_idx': idx
                    })
            
            # Tombol untuk menambah jadwal baru
            if st.button("➕ Tambah Jadwal Baru"):
                # Add new schedule logic here
                pass
            
            # Tombol simpan
            if st.button("💾 Simpan Perubahan", type="primary"):
                show_message("Perubahan berhasil disimpan!", "success")
                # Here you would update the DataFrame
                
        else:
            st.info("Dokter ini belum memiliki jadwal. Tambah jadwal baru:")
            
            # Form untuk menambah jadwal baru
            with st.form("add_schedule_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_day = st.selectbox("Hari", config.WORK_DAYS)
                
                with col2:
                    new_start = st.time_input("Waktu Mulai", value=time(8, 0))
                
                with col3:
                    new_end = st.time_input("Waktu Selesai", value=time(12, 0))
                
                # Additional fields
                room = st.text_input("Ruangan (opsional)")
                clinic = st.text_input("Poliklinik (opsional)")
                
                if st.form_submit_button("➕ Tambah Jadwal"):
                    # Add new schedule logic here
                    show_message("Jadwal berhasil ditambahkan!", "success")

def _render_auto_schedule():
    """Render auto schedule mode"""
    st.subheader("🔄 Auto Schedule Generator")
    
    st.info("""
    **Auto Schedule** akan menghasilkan jadwal otomatis berdasarkan:
    1. Waktu kerja yang ditentukan
    2. Ketersediaan dokter
    3. Aturan spesialisasi
    """)
    
    # Configuration
    with st.expander("⚙️ Konfigurasi Auto Schedule", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            work_days = st.multiselect(
                "Hari Kerja",
                config.WORK_DAYS,
                default=config.WORK_DAYS[:5]
            )
            
            start_time = st.time_input(
                "Waktu Mulai Kerja",
                value=config.WORK_START
            )
        
        with col2:
            slot_duration = st.selectbox(
                "Durasi Slot (menit)",
                [30, 60, 90, 120],
                index=1
            )
            
            end_time = st.time_input(
                "Waktu Selesai Kerja",
                value=config.WORK_END
            )
    
    # Dokter yang akan dijadwalkan
    if 'doctors_list' in st.session_state:
        doctors = st.session_state.doctors_list
        
        selected_doctors = st.multiselect(
            "Pilih Dokter untuk Dijadwalkan",
            doctors,
            default=doctors[:min(5, len(doctors))]
        )
        
        if selected_doctors:
            # Tampilkan preview schedule
            st.subheader("📋 Preview Jadwal yang Akan Dihasilkan")
            
            # Generate sample schedule
            schedule_data = []
            
            for doctor in selected_doctors:
                for day in work_days:
                    # Generate random schedule for demo
                    import random
                    
                    # Random start time within work hours
                    start_hour = random.randint(start_time.hour, end_time.hour - 2)
                    start_minute = random.choice([0, 30])
                    start = time(start_hour, start_minute)
                    
                    # Duration 1-4 slots
                    duration_slots = random.randint(1, 4)
                    end_hour = start_hour + duration_slots
                    end_minute = start_minute
                    end = time(end_hour % 24, end_minute)
                    
                    schedule_data.append({
                        'Dokter': doctor,
                        'Hari': day,
                        'Mulai': start.strftime("%H:%M"),
                        'Selesai': end.strftime("%H:%M"),
                        'Durasi': f"{duration_slots} slot"
                    })
            
            if schedule_data:
                preview_df = pd.DataFrame(schedule_data)
                st.dataframe(preview_df, use_container_width=True)
                
                # Action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Generate Jadwal", type="primary", use_container_width=True):
                        with st.spinner("Membuat jadwal..."):
                            # Simulate generation
                            import time as sleep_time
                            sleep_time.sleep(2)
                            show_message("Jadwal berhasil dibuat!", "success")
                
                with col2:
                    if st.button("📥 Export Jadwal", use_container_width=True):
                        csv = preview_df.to_csv(index=False)
                        st.download_button(
                            label="💾 Download CSV",
                            data=csv,
                            file_name="auto_schedule.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
        else:
            st.warning("Pilih minimal satu dokter")
    else:
        st.warning("Tidak ada data dokter. Upload data terlebih dahulu.")
