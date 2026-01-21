"""
Schedule tab UI component - SIMPLIFIED VERSION
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time
import numpy as np

def convert_to_indonesian_day(day_english: str) -> str:
    """Convert English day name to Indonesian"""
    day_map = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa',
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }
    return day_map.get(day_english, day_english)

def format_time_display(time_str: str) -> str:
    """Format time for display"""
    if not time_str or pd.isna(time_str) or str(time_str).strip() in ['', '-', '[Reference]']:
        return "-"
    
    time_str = str(time_str).strip()
    return time_str

def display_schedule_tab():
    """Display schedule tab content"""
    
    st.header("📅 Jadwal Dokter")
    
    if 'data' not in st.session_state or not st.session_state.data_loaded:
        st.warning("⚠️ Silakan upload data terlebih dahulu di tab 'Upload Data'")
        return
    
    df = st.session_state.data
    
    # Check if it's hafis format
    is_hafis_format = all(col in df.columns for col in ['working_hours', 'regular_schedule', 'executive_schedule'])
    
    if is_hafis_format:
        display_hafis_schedule(df)
    else:
        display_standard_schedule(df)

def display_hafis_schedule(df: pd.DataFrame):
    """Display schedule for hafis format"""
    
    # View selector
    view_option = st.radio(
        "Pilih Tampilan:",
        ["📋 Tabel Lengkap", "👨‍⚕️ Per Dokter", "🏥 Per Spesialisasi"],
        horizontal=True
    )
    
    if view_option == "📋 Tabel Lengkap":
        display_hafis_full_table(df)
    
    elif view_option == "👨‍⚕️ Per Dokter":
        display_hafis_by_doctor(df)
    
    elif view_option == "🏥 Per Spesialisasi":
        display_hafis_by_specialty(df)

def display_hafis_full_table(df: pd.DataFrame):
    """Display full table for hafis format"""
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        specialties = ['All'] + sorted(df['specialty'].unique().tolist())
        selected_specialty = st.selectbox("Filter Spesialisasi:", specialties)
    
    with col2:
        days = ['All'] + sorted(df['day'].unique().tolist())
        selected_day = st.selectbox("Filter Hari:", days)
    
    with col3:
        availability = ['All', 'Available', 'Not Available']
        selected_availability = st.selectbox("Filter Ketersediaan:", availability)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_specialty != 'All':
        filtered_df = filtered_df[filtered_df['specialty'] == selected_specialty]
    
    if selected_day != 'All':
        filtered_df = filtered_df[filtered_df['day'] == selected_day]
    
    if selected_availability == 'Available':
        filtered_df = filtered_df[filtered_df['available'] == 1]
    elif selected_availability == 'Not Available':
        filtered_df = filtered_df[filtered_df['available'] == 0]
    
    # Display table
    st.write(f"**Showing {len(filtered_df)} records**")
    
    # Select columns to show
    columns_to_show = [
        'doctor_name', 'specialty', 'day',
        'working_hours', 'regular_schedule', 'executive_schedule', 'available'
    ]
    
    # Filter columns that exist
    available_cols = [col for col in columns_to_show if col in filtered_df.columns]
    display_df = filtered_df[available_cols].copy()
    
    # Format for display
    display_df['day'] = display_df['day'].apply(convert_to_indonesian_day)
    
    # Sort
    display_df = display_df.sort_values(['specialty', 'doctor_name', 'day'])
    
    # Display
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Export options
    csv_data = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv_data,
        file_name="jadwal_dokter.csv",
        mime="text/csv",
        use_container_width=True
    )

def display_hafis_by_doctor(df: pd.DataFrame):
    """Display schedule by doctor"""
    
    # Doctor selector
    doctors = sorted(df['doctor_name'].unique().tolist())
    selected_doctor = st.selectbox("Pilih Dokter:", doctors)
    
    if selected_doctor:
        doctor_df = df[df['doctor_name'] == selected_doctor].copy()
        
        # Doctor info
        specialty = doctor_df['specialty'].iloc[0] if len(doctor_df) > 0 else "N/A"
        department = doctor_df['department'].iloc[0] if 'department' in doctor_df.columns and len(doctor_df) > 0 else "N/A"
        
        # Display doctor info
        st.markdown(f"### 👨‍⚕️ {selected_doctor}")
        st.markdown(f"**Spesialisasi:** {specialty}")
        if department:
            st.markdown(f"**Departemen:** {department}")
        
        # Schedule table
        st.subheader("📅 Jadwal Mingguan")
        
        # Order days properly
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        doctor_df['day'] = pd.Categorical(doctor_df['day'], categories=days_order, ordered=True)
        doctor_df = doctor_df.sort_values('day')
        
        # Create display table
        schedule_data = []
        
        for _, row in doctor_df.iterrows():
            schedule_data.append({
                'Hari': convert_to_indonesian_day(row['day']),
                'Jam Kerja': format_time_display(row['working_hours']),
                'Reguler': format_time_display(row['regular_schedule']),
                'Eksekutif': format_time_display(row['executive_schedule']),
                'Status': '✅ Tersedia' if row['available'] == 1 else '❌ Tidak Tersedia'
            })
        
        schedule_df = pd.DataFrame(schedule_data)
        
        st.dataframe(schedule_df, use_container_width=True)

def display_hafis_by_specialty(df: pd.DataFrame):
    """Display schedule by specialty"""
    
    # Specialty selector
    specialties = sorted(df['specialty'].unique().tolist())
    selected_specialty = st.selectbox("Pilih Spesialisasi:", specialties)
    
    if selected_specialty:
        spec_df = df[df['specialty'] == selected_specialty].copy()
        
        # Stats
        doctors_count = len(spec_df['doctor_name'].unique())
        total_slots = len(spec_df)
        available_slots = spec_df['available'].sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Jumlah Dokter", doctors_count)
        
        with col2:
            st.metric("Total Slot", total_slots)
        
        with col3:
            st.metric("Slot Tersedia", available_slots)
        
        # Create pivot table view
        st.subheader("📊 Jadwal per Dokter")
        
        # Create simplified pivot
        pivot_data = []
        doctors = sorted(spec_df['doctor_name'].unique())
        
        for doctor in doctors:
            doctor_data = spec_df[spec_df['doctor_name'] == doctor]
            doctor_schedule = {}
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
                day_schedule = doctor_data[doctor_data['day'] == day]
                if not day_schedule.empty:
                    schedule = day_schedule.iloc[0]
                    doctor_schedule[convert_to_indonesian_day(day)] = format_time_display(schedule['working_hours'])
                else:
                    doctor_schedule[convert_to_indonesian_day(day)] = "-"
            
            pivot_data.append({
                'Dokter': doctor,
                **doctor_schedule
            })
        
        if pivot_data:
            pivot_df = pd.DataFrame(pivot_data)
            st.dataframe(pivot_df, use_container_width=True)

def display_standard_schedule(df: pd.DataFrame):
    """Display schedule for standard format"""
    
    st.info("Standard schedule format detected.")
    
    # Show available columns
    st.write("Available columns:", list(df.columns))
    
    # Simple table view
    st.dataframe(df, use_container_width=True)
