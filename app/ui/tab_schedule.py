"""
Tab untuk menampilkan dan mengatur jadwal
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, time
import numpy as np
from ..config import config, TimeSlot
from ..utils import show_message, format_time, get_unique_values
from ..core import ScheduleParser, DataCleaner

def render():
    """Render tab jadwal"""
    st.header("📅 Jadwal Dokter")
    
    # Cek jika ada data
    if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
        st.warning("⚠️ Tidak ada data jadwal. Silakan upload data terlebih dahulu di tab **📤 Upload Data**")
        
        if st.button("📤 Ke Tab Upload", type="primary"):
            st.switch_page("?tab=Upload%20Data")
        return
    
    df = st.session_state.uploaded_data
    
    # Parse data jika belum diparse
    if 'schedule_data' not in st.session_state or st.session_state.schedule_data is None:
        with st.spinner("Memproses data jadwal..."):
            parser = ScheduleParser()
            parsed_data = parser.parse_schedule_data(df)
            st.session_state.schedule_data = parsed_data
            st.rerun()
    
    parsed_data = st.session_state.schedule_data
    
    # Filter controls
    st.subheader("🔍 Filter Jadwal")
    
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col4:
        time_range = st.selectbox(
            "Rentang Waktu",
            ["Semua", "Pagi (06:00-12:00)", "Siang (12:00-16:00)", "Sore (16:00-20:00)", "Malam (20:00-24:00)"],
            help="Filter berdasarkan waktu"
        )
    
    # Apply filters
    filtered_schedules = parsed_data['schedules']
    
    if selected_doctor != "Semua":
        filtered_schedules = [s for s in filtered_schedules if s['doctor'] == selected_doctor]
    
    if selected_specialization != "Semua":
        filtered_schedules = [s for s in filtered_schedules if s['specialization'] == selected_specialization]
    
    if selected_day != "Semua":
        filtered_schedules = [s for s in filtered_schedules if s['day'] == selected_day]
    
    if time_range != "Semua":
        time_map = {
            "Pagi (06:00-12:00)": (time(6, 0), time(12, 0)),
            "Siang (12:00-16:00)": (time(12, 0), time(16, 0)),
            "Sore (16:00-20:00)": (time(16, 0), time(20, 0)),
            "Malam (20:00-24:00)": (time(20, 0), time(23, 59))
        }
        
        if time_range in time_map:
            start_filter, end_filter = time_map[time_range]
            filtered_schedules = [
                s for s in filtered_schedules 
                if s['start_time'] >= start_filter and s['start_time'] <= end_filter
            ]
    
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
        ["Tabel", "Kalender", "Grafik", "Per Dokter"],
        horizontal=True
    )
    
    if view_option == "Tabel":
        _render_table_view(filtered_schedules)
    elif view_option == "Kalender":
        _render_calendar_view(filtered_schedules)
    elif view_option == "Grafik":
        _render_chart_view(filtered_schedules, parsed_data)
    elif view_option == "Per Dokter":
        _render_doctor_view(parsed_data)
    
    # Export options
    st.markdown("---")
    st.subheader("📤 Export Jadwal")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📄 Export ke CSV", use_container_width=True):
            parser = ScheduleParser()
            schedule_df = parser.create_schedule_table({'schedules': filtered_schedules})
            csv = schedule_df.to_csv(index=False)
            
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name="jadwal_dokter_filtered.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with export_col2:
        if st.button("📊 Export ke Excel", use_container_width=True):
            parser = ScheduleParser()
            schedule_df = parser.create_schedule_table({'schedules': filtered_schedules})
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                schedule_df.to_excel(writer, index=False, sheet_name='Jadwal')
            
            st.download_button(
                label="💾 Download Excel",
                data=output.getvalue(),
                file_name="jadwal_dokter.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with export_col3:
        if st.button("🖨️ Cetak Jadwal", use_container_width=True):
            st.info("Fitur cetak akan membuka preview cetak di browser")

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
    
    # Tampilkan tabel dengan styling
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        column_config={
            "Durasi": st.column_config.ProgressColumn(
                "Durasi",
                help="Durasi dalam jam",
                format="%.1f jam",
                min_value=0,
                max_value=8
            )
        }
    )

def _render_calendar_view(schedules):
    """Render tampilan kalender"""
    if not schedules:
        st.info("Tidak ada jadwal yang sesuai dengan filter")
        return
    
    # Group by day
    days = sorted(set(s['day'] for s in schedules))
    
    for day in days:
        day_schedules = [s for s in schedules if s['day'] == day]
        
        with st.expander(f"📅 {day} ({len(day_schedules)} jadwal)", expanded=True):
            # Sort by start time
            day_schedules.sort(key=lambda x: x['start_time'])
            
            for schedule in day_schedules:
                # Calculate color based on specialization
                specialization = schedule['specialization']
                color = config.SPECIALIZATION_COLORS.get(specialization, config.COLORS['primary'])
                
                # Create schedule card
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
                    if schedule.get('clinic'):
                        st.caption(schedule['clinic'])
                
                st.markdown("---")

def _render_chart_view(schedules, parsed_data):
    """Render tampilan grafik"""
    if not schedules:
        st.info("Tidak ada jadwal yang sesuai dengan filter")
        return
    
    tab1, tab2, tab3 = st.tabs(["📈 Per Hari", "👨‍⚕️ Per Dokter", "🏥 Per Spesialisasi"])
    
    with tab1:
        # Chart per hari
        days_data = {}
        for schedule in schedules:
            day = schedule['day']
            if day not in days_data:
                days_data[day] = {'count': 0, 'hours': 0}
            days_data[day]['count'] += 1
            days_data[day]['hours'] += schedule['duration']
        
        # Buat DataFrame untuk chart
        days_df = pd.DataFrame([
            {'Hari': day, 'Jumlah Jadwal': data['count'], 'Total Jam': data['hours']}
            for day, data in days_data.items()
        ])
        
        if not days_df.empty:
            # Sort by predefined day order
            day_order = config.WORK_DAYS + config.WEEKEND
            days_df['Hari'] = pd.Categorical(days_df['Hari'], categories=day_order, ordered=True)
            days_df = days_df.sort_values('Hari')
            
            # Create bar chart
            fig = px.bar(
                days_df,
                x='Hari',
                y='Jumlah Jadwal',
                color='Total Jam',
                title='Jadwal per Hari',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Chart per dokter
        doctors_data = {}
        for schedule in schedules:
            doctor = schedule['doctor']
            if doctor not in doctors_data:
                doctors_data[doctor] = {'count': 0, 'hours': 0}
            doctors_data[doctor]['count'] += 1
            doctors_data[doctor]['hours'] += schedule['duration']
        
        # Buat DataFrame untuk chart
        doctors_df = pd.DataFrame([
            {'Dokter': doctor, 'Jumlah Jadwal': data['count'], 'Total Jam': data['hours']}
            for doctor, data in doctors_data.items()
        ])
        
        if not doctors_df.empty:
            doctors_df = doctors_df.sort_values('Total Jam', ascending=False)
            
            # Create bar chart
            fig = px.bar(
                doctors_df.head(10),  # Tampilkan top 10
                x='Dokter',
                y='Total Jam',
                color='Jumlah Jadwal',
                title='Top 10 Dokter berdasarkan Jam Kerja',
                color_continuous_scale='Viridis'
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Chart per spesialisasi
        specializations_data = {}
        for schedule in schedules:
            spec = schedule['specialization']
            if spec not in specializations_data:
                specializations_data[spec] = {'count': 0, 'hours': 0}
            specializations_data[spec]['count'] += 1
            specializations_data[spec]['hours'] += schedule['duration']
        
        # Buat DataFrame untuk chart
        spec_df = pd.DataFrame([
            {'Spesialisasi': spec, 'Jumlah Jadwal': data['count'], 'Total Jam': data['hours']}
            for spec, data in specializations_data.items()
        ])
        
        if not spec_df.empty:
            # Create pie chart
            fig = px.pie(
                spec_df,
                values='Total Jam',
                names='Spesialisasi',
                title='Distribusi Jam Kerja per Spesialisasi',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)

def _render_doctor_view(parsed_data):
    """Render tampilan per dokter"""
    doctors_data = parsed_data.get('doctors', {})
    
    if not doctors_data:
        st.info("Tidak ada data dokter")
        return
    
    # Pilih dokter
    doctors = list(doctors_data.keys())
    selected_doctor = st.selectbox("Pilih Dokter untuk Detail", doctors)
    
    if selected_doctor:
        doctor_info = doctors_data[selected_doctor]
        
        # Tampilkan info dokter
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: #f0f7ff; border-radius: 10px;">
                    <h3>{selected_doctor}</h3>
                    <p style="color: {config.COLORS['primary']}; font-weight: bold;">
                        {doctor_info['specialization']}
                    </p>
                    <p>📅 {len(doctor_info['days'])} hari kerja</p>
                    <p>⏱️ {doctor_info['total_hours']:.1f} jam/minggu</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Jadwal per hari
            st.subheader("📅 Jadwal per Hari")
            
            days = sorted(doctor_info['days'])
            for day in days:
                # Cari jadwal untuk hari ini
                day_schedules = [s for s in doctor_info['schedules'] if s['day'] == day]
                
                if day_schedules:
                    st.markdown(f"**{day}**")
                    
                    for schedule in day_schedules:
                        st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid {config.COLORS['primary']};">
                                <strong>{schedule['start_str']} - {schedule['end_str']}</strong> 
                                ({schedule['duration']:.1f} jam)
                                {f"| 📍 {schedule.get('room', '')}" if schedule.get('room') else ''}
                                {f"| 🏥 {schedule.get('clinic', '')}" if schedule.get('clinic') else ''}
                            </div>
                        """, unsafe_allow_html=True)
            
            # Summary
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Jadwal", len(doctor_info['schedules']))
            with col2:
                st.metric("Hari Kerja", len(doctor_info['days']))
            with col3:
                st.metric("Jam/Minggu", f"{doctor_info['total_hours']:.1f}")
