"""
Schedule tab UI component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time
import numpy as np
from app.config import AppConfig
from app.utils import convert_to_indonesian_day, format_time_display

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
        ["📋 Tabel Lengkap", "👨‍⚕️ Per Dokter", "🏥 Per Spesialisasi", "🕒 Timeline Visual", "📊 Analytics"],
        horizontal=True
    )
    
    if view_option == "📋 Tabel Lengkap":
        display_hafis_full_table(df)
    
    elif view_option == "👨‍⚕️ Per Dokter":
        display_hafis_by_doctor(df)
    
    elif view_option == "🏥 Per Spesialisasi":
        display_hafis_by_specialty(df)
    
    elif view_option == "🕒 Timeline Visual":
        display_hafis_timeline(df)
    
    elif view_option == "📊 Analytics":
        display_hafis_analytics(df)

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
    
    # Display with styling
    def color_availability(val):
        if val == 1:
            return 'background-color: #d4edda; color: #155724; font-weight: bold;'
        else:
            return 'background-color: #f8d7da; color: #721c24;'
    
    styled_df = display_df.style.applymap(color_availability, subset=['available'])
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=600
    )
    
    # Export options
    st.download_button(
        label="📥 Download as CSV",
        data=display_df.to_csv(index=False),
        file_name=f"jadwal_dokter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### 👨‍⚕️ {selected_doctor}")
            st.markdown(f"**Spesialisasi:** {specialty}")
            if department:
                st.markdown(f"**Departemen:** {department}")
        
        with col2:
            available_days = doctor_df[doctor_df['available'] == 1].shape[0]
            st.metric("Hari Tersedia", available_days)
        
        with col3:
            total_days = len(doctor_df)
            st.metric("Total Hari", total_days)
        
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
        
        # Color coding
        def color_status(val):
            if 'Tersedia' in val:
                return 'background-color: #d4edda; color: #155724;'
            else:
                return 'background-color: #f8d7da; color: #721c24;'
        
        styled_schedule = schedule_df.style.applymap(color_status, subset=['Status'])
        
        st.dataframe(styled_schedule, use_container_width=True)
        
        # Visual timeline
        if st.checkbox("Show Timeline Visualization"):
            display_doctor_timeline(doctor_df)

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
        
        # Doctor list
        doctors = sorted(spec_df['doctor_name'].unique())
        
        # Use tabs for each doctor or grouped view
        view_option = st.radio(
            "Tampilan:",
            ["Grouped View", "Per Doctor"],
            horizontal=True
        )
        
        if view_option == "Grouped View":
            # Create a pivot table
            pivot_data = []
            
            for doctor in doctors:
                doctor_data = spec_df[spec_df['doctor_name'] == doctor]
                
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
                    day_data = doctor_data[doctor_data['day'] == day]
                    
                    if not day_data.empty:
                        row = day_data.iloc[0]
                        pivot_data.append({
                            'Dokter': doctor,
                            'Hari': convert_to_indonesian_day(day),
                            'Jam Kerja': format_time_display(row['working_hours']),
                            'Status': '✅' if row['available'] == 1 else '❌'
                        })
            
            pivot_df = pd.DataFrame(pivot_data)
            
            # Pivot for better visualization
            if not pivot_df.empty:
                pivot_table = pivot_df.pivot_table(
                    index='Dokter',
                    columns='Hari',
                    values='Jam Kerja',
                    aggfunc='first',
                    fill_value='-'
                )
                
                # Reorder columns
                hari_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
                pivot_table = pivot_table.reindex(columns=hari_order)
                
                st.dataframe(pivot_table, use_container_width=True)
        
        else:
            # Per doctor view
            selected_doctor = st.selectbox("Pilih Dokter:", doctors)
            
            if selected_doctor:
                doctor_df = spec_df[spec_df['doctor_name'] == selected_doctor].copy()
                
                # Display schedule
                schedule_data = []
                
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
                    day_data = doctor_df[doctor_df['day'] == day]
                    
                    if not day_data.empty:
                        row = day_data.iloc[0]
                        schedule_data.append({
                            'Hari': convert_to_indonesian_day(day),
                            'Jam Kerja': format_time_display(row['working_hours']),
                            'Reguler': format_time_display(row['regular_schedule']),
                            'Eksekutif': format_time_display(row['executive_schedule']),
                            'Status': 'Tersedia' if row['available'] == 1 else 'Tidak Tersedia'
                        })
                    else:
                        schedule_data.append({
                            'Hari': convert_to_indonesian_day(day),
                            'Jam Kerja': '-',
                            'Reguler': '-',
                            'Eksekutif': '-',
                            'Status': 'Libur'
                        })
                
                schedule_df = pd.DataFrame(schedule_data)
                st.dataframe(schedule_df, use_container_width=True)

def display_hafis_timeline(df: pd.DataFrame):
    """Display timeline visualization"""
    
    # Prepare data for timeline
    timeline_data = []
    
    for _, row in df.iterrows():
        if row['available'] == 1 and pd.notna(row['working_hours']) and row['working_hours'] != '':
            # Parse working hours
            if '-' in str(row['working_hours']):
                try:
                    start_str, end_str = str(row['working_hours']).split('-')
                    
                    # Convert to minutes from midnight
                    def time_to_minutes(t_str):
                        if ':' in t_str:
                            h, m = map(int, t_str.split(':'))
                            return h * 60 + m
                        return 0
                    
                    start_minutes = time_to_minutes(start_str.strip())
                    end_minutes = time_to_minutes(end_str.strip())
                    
                    if start_minutes < end_minutes:
                        timeline_data.append({
                            'Doctor': row['doctor_name'],
                            'Specialty': row['specialty'],
                            'Day': row['day'],
                            'Start': start_minutes,
                            'End': end_minutes,
                            'Duration': end_minutes - start_minutes
                        })
                except:
                    pass
    
    if timeline_data:
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create visualization
        fig = go.Figure()
        
        # Add bars for each doctor
        colors = px.colors.qualitative.Set3
        
        for idx, (doctor, data) in enumerate(timeline_df.groupby('Doctor')):
            fig.add_trace(go.Bar(
                x=data['Day'],
                y=data['Duration'] / 60,  # Convert to hours
                base=data['Start'] / 60,  # Convert to hours
                name=doctor,
                marker_color=colors[idx % len(colors)],
                hovertemplate=(
                    '<b>%{customdata[0]}</b><br>' +
                    'Day: %{x}<br>' +
                    'Time: %{customdata[1]} - %{customdata[2]}<br>' +
                    'Duration: %{y:.1f} hours<br>' +
                    '<extra></extra>'
                ),
                customdata=np.stack((
                    data['Doctor'],
                    data['Start'].apply(lambda x: f"{x//60:02d}:{x%60:02d}"),
                    data['End'].apply(lambda x: f"{x//60:02d}:{x%60:02d}")
                ), axis=-1)
            ))
        
        fig.update_layout(
            title='Doctor Schedule Timeline',
            xaxis_title='Day',
            yaxis_title='Time (Hours)',
            barmode='stack',
            yaxis=dict(
                tickformat='%H:%M',
                range=[6, 18]  # Show from 6 AM to 6 PM
            ),
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        with st.expander("View Timeline Data"):
            display_timeline_df = timeline_df.copy()
            display_timeline_df['Start Time'] = display_timeline_df['Start'].apply(
                lambda x: f"{x//60:02d}:{x%60:02d}"
            )
            display_timeline_df['End Time'] = display_timeline_df['End'].apply(
                lambda x: f"{x//60:02d}:{x%60:02d}"
            )
            display_timeline_df['Duration (hours)'] = display_timeline_df['Duration'] / 60
            
            st.dataframe(
                display_timeline_df[['Doctor', 'Specialty', 'Day', 'Start Time', 'End Time', 'Duration (hours)']],
                use_container_width=True
            )
    
    else:
        st.info("No timeline data available. Make sure 'working_hours' column contains time ranges.")

def display_hafis_analytics(df: pd.DataFrame):
    """Display analytics for hafis format"""
    
    # Create analytics dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        # Doctor count by specialty
        st.subheader("Doctors per Specialty")
        specialty_counts = df['specialty'].value_counts().reset_index()
        specialty_counts.columns = ['Specialty', 'Count']
        
        fig1 = px.bar(
            specialty_counts,
            x='Specialty',
            y='Count',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(height=300)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Schedule distribution by day
        st.subheader("Schedule Distribution by Day")
        day_counts = df['day'].value_counts().reset_index()
        day_counts.columns = ['Day', 'Count']
        
        # Convert to Indonesian
        day_counts['Day'] = day_counts['Day'].apply(convert_to_indonesian_day)
        
        fig2 = px.pie(
            day_counts,
            values='Count',
            names='Day',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Availability analysis
    st.subheader("Availability Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Availability rate
        total_slots = len(df)
        available_slots = df['available'].sum()
        availability_rate = (available_slots / total_slots * 100) if total_slots > 0 else 0
        
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=availability_rate,
            title={'text': "Overall Availability Rate"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1E88E5"},
                'steps': [
                    {'range': [0, 50], 'color': "#f8d7da"},
                    {'range': [50, 80], 'color': "#fff3cd"},
                    {'range': [80, 100], 'color': "#d4edda"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Availability by specialty
        st.subheader("Availability by Specialty")
        
        availability_by_spec = df.groupby('specialty').agg({
            'available': ['count', 'sum']
        }).reset_index()
        
        availability_by_spec.columns = ['Specialty', 'Total', 'Available']
        availability_by_spec['Rate'] = (availability_by_spec['Available'] / availability_by_spec['Total'] * 100).round(1)
        
        fig4 = px.bar(
            availability_by_spec,
            x='Specialty',
            y='Rate',
            color='Rate',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        fig4.update_layout(height=300, yaxis_title="Availability Rate (%)")
        st.plotly_chart(fig4, use_container_width=True)
    
    # Top doctors by availability
    st.subheader("Top Doctors by Availability")
    
    if 'doctor_name' in df.columns:
        doctor_stats = df.groupby('doctor_name').agg({
            'available': ['count', 'sum']
        }).reset_index()
        
        doctor_stats.columns = ['Doctor', 'Total Days', 'Available Days']
        doctor_stats['Availability Rate'] = (doctor_stats['Available Days'] / doctor_stats['Total Days'] * 100).round(1)
        doctor_stats = doctor_stats.sort_values('Availability Rate', ascending=False)
        
        st.dataframe(
            doctor_stats.head(10),
            use_container_width=True
        )

def display_standard_schedule(df: pd.DataFrame):
    """Display schedule for standard format"""
    
    st.info("Standard schedule format detected.")
    
    # Show available columns
    st.write("Available columns:", list(df.columns))
    
    # Simple table view
    st.dataframe(df, use_container_width=True)
    
    # Basic filters
    if 'day' in df.columns:
        days = ['All'] + sorted(df['day'].unique().tolist())
        selected_day = st.selectbox("Filter by Day:", days)
        
        if selected_day != 'All':
            filtered_df = df[df['day'] == selected_day]
            st.dataframe(filtered_df, use_container_width=True)

def display_doctor_timeline(doctor_df: pd.DataFrame):
    """Display timeline for a specific doctor"""
    
    # Prepare data
    timeline_data = []
    
    for _, row in doctor_df.iterrows():
        if row['available'] == 1 and pd.notna(row['working_hours']):
            try:
                # Parse working hours
                if '-' in str(row['working_hours']):
                    start_str, end_str = str(row['working_hours']).split('-')
                    
                    # Convert to datetime
                    start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                    end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                    
                    timeline_data.append({
                        'Day': row['day'],
                        'Start': start_time,
                        'End': end_time,
                        'Activity': 'Working Hours'
                    })
                
                # Parse regular schedule
                if pd.notna(row['regular_schedule']) and row['regular_schedule'] not in ['', '[Reference]']:
                    if '-' in str(row['regular_schedule']):
                        start_str, end_str = str(row['regular_schedule']).split('-')
                        start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                        end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                        
                        timeline_data.append({
                            'Day': row['day'],
                            'Start': start_time,
                            'End': end_time,
                            'Activity': 'Regular Schedule'
                        })
                
                # Parse executive schedule
                if pd.notna(row['executive_schedule']) and row['executive_schedule'] not in ['', '[Reference]']:
                    if '-' in str(row['executive_schedule']):
                        start_str, end_str = str(row['executive_schedule']).split('-')
                        start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                        end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                        
                        timeline_data.append({
                            'Day': row['day'],
                            'Start': start_time,
                            'End': end_time,
                            'Activity': 'Executive Schedule'
                        })
            
            except:
                continue
    
    if timeline_data:
        # Create timeline visualization
        fig = go.Figure()
        
        colors = {
            'Working Hours': '#1E88E5',
            'Regular Schedule': '#4CAF50',
            'Executive Schedule': '#FF9800'
        }
        
        # Order days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for activity, color in colors.items():
            activity_data = [d for d in timeline_data if d['Activity'] == activity]
            
            if activity_data:
                x_data = []
                y_data = []
                
                for data in activity_data:
                    x_data.append(data['Day'])
                    y_data.append(data['Start'])
                
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers+lines',
                    name=activity,
                    marker=dict(color=color, size=10),
                    line=dict(color=color, width=2)
                ))
        
        fig.update_layout(
            title='Doctor Schedule Timeline',
            xaxis_title='Day',
            yaxis_title='Time',
            yaxis=dict(
                tickformat='%H:%M',
                range=['06:00', '18:00']
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
