"""
Kanban drag tab UI component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
from app.config import AppConfig

def display_kanban_tab():
    """Display kanban drag tab content"""
    
    st.header("🧩 Kanban Drag Schedule")
    
    if 'data' not in st.session_state or not st.session_state.data_loaded:
        st.warning("⚠️ Silakan upload data terlebih dahulu di tab 'Upload Data'")
        return
    
    df = st.session_state.data
    
    # Simplified kanban interface
    st.info("""
    **Simple Kanban Interface** - Drag and drop functionality simulation.
    Select doctors and assign them to time slots.
    """)
    
    # Create columns for days
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Time slots
    time_slots = [
        '08:00-09:00', '09:00-10:00', '10:00-11:00', 
        '11:00-12:00', '13:00-14:00', '14:00-15:00', '15:00-16:00'
    ]
    
    # Initialize session state for kanban
    if 'kanban_data' not in st.session_state:
        st.session_state.kanban_data = {}
        for day in days:
            st.session_state.kanban_data[day] = {}
            for slot in time_slots:
                st.session_state.kanban_data[day][slot] = []
    
    # Doctor selection
    available_doctors = sorted(df['doctor_name'].unique().tolist())
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Available Doctors")
        selected_doctors = st.multiselect(
            "Select doctors to schedule:",
            available_doctors,
            default=available_doctors[:5] if len(available_doctors) > 5 else available_doctors
        )
    
    with col2:
        st.subheader("Settings")
        max_doctors_per_slot = st.slider("Max doctors per time slot:", 1, 5, 2)
        show_specialty = st.checkbox("Show specialty", True)
    
    # Kanban board
    st.subheader("Schedule Board")
    
    # Create columns for each day
    day_cols = st.columns(len(days))
    
    for idx, day in enumerate(days):
        with day_cols[idx]:
            st.markdown(f"### {AppConfig.DAYS_INDONESIA[day]}")
            
            # Display each time slot
            for slot in time_slots:
                with st.container():
                    st.markdown(f"**{slot}**")
                    
                    # Current doctors in this slot
                    current_doctors = st.session_state.kanban_data[day][slot]
                    
                    if current_doctors:
                        for doctor in current_doctors:
                            # Get doctor info
                            doctor_info = df[df['doctor_name'] == doctor].iloc[0] if not df[df['doctor_name'] == doctor].empty else {}
                            
                            # Display doctor card
                            card_content = f"👨‍⚕️ {doctor}"
                            if show_specialty and 'specialty' in doctor_info:
                                card_content += f"<br><small>{doctor_info['specialty']}</small>"
                            
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: #e3f2fd;
                                    border: 1px solid #bbdefb;
                                    border-radius: 5px;
                                    padding: 8px;
                                    margin: 4px 0;
                                    font-size: 0.9em;
                                ">
                                    {card_content}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    # Add doctor dropdown
                    available_for_slot = [d for d in selected_doctors if d not in current_doctors]
                    
                    if available_for_slot and len(current_doctors) < max_doctors_per_slot:
                        new_doctor = st.selectbox(
                            f"Add doctor to {slot}",
                            [""] + available_for_slot,
                            key=f"add_{day}_{slot}"
                        )
                        
                        if new_doctor:
                            if new_doctor not in st.session_state.kanban_data[day][slot]:
                                st.session_state.kanban_data[day][slot].append(new_doctor)
                                st.rerun()
                    
                    # Remove doctor buttons
                    if current_doctors:
                        for doctor in current_doctors:
                            col_a, col_b = st.columns([3, 1])
                            with col_b:
                                if st.button("❌", key=f"remove_{day}_{slot}_{doctor}"):
                                    st.session_state.kanban_data[day][slot].remove(doctor)
                                    st.rerun()
    
    # Schedule summary
    st.divider()
    st.subheader("📊 Schedule Summary")
    
    # Calculate statistics
    total_slots = len(days) * len(time_slots)
    filled_slots = 0
    doctor_assignments = {}
    
    for day in days:
        for slot in time_slots:
            doctors_in_slot = st.session_state.kanban_data[day][slot]
            if doctors_in_slot:
                filled_slots += 1
                for doctor in doctors_in_slot:
                    if doctor not in doctor_assignments:
                        doctor_assignments[doctor] = 0
                    doctor_assignments[doctor] += 1
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Time Slots", total_slots)
    
    with col2:
        st.metric("Filled Slots", filled_slots)
    
    with col3:
        utilization = (filled_slots / total_slots * 100) if total_slots > 0 else 0
        st.metric("Utilization Rate", f"{utilization:.1f}%")
    
    # Doctor assignment summary
    if doctor_assignments:
        st.write("**Doctor Assignments:**")
        
        assignment_data = []
        for doctor, count in doctor_assignments.items():
            assignment_data.append({
                'Doctor': doctor,
                'Assignments': count
            })
        
        assignment_df = pd.DataFrame(assignment_data)
        assignment_df = assignment_df.sort_values('Assignments', ascending=False)
        
        st.dataframe(assignment_df, use_container_width=True)
        
        # Visualize assignments
        fig = px.bar(
            assignment_df,
            x='Doctor',
            y='Assignments',
            color='Assignments',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Export options
    st.divider()
    st.subheader("📤 Export Schedule")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as CSV
        export_data = []
        
        for day in days:
            for slot in time_slots:
                doctors_in_slot = st.session_state.kanban_data[day][slot]
                if doctors_in_slot:
                    for doctor in doctors_in_slot:
                        export_data.append({
                            'Day': day,
                            'Time Slot': slot,
                            'Doctor': doctor
                        })
        
        if export_data:
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="kanban_schedule.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        # Reset button
        if st.button("🔄 Reset Schedule", use_container_width=True):
            for day in days:
                for slot in time_slots:
                    st.session_state.kanban_data[day][slot] = []
            st.success("Schedule reset successfully!")
            st.rerun()
    
    # Schedule visualization
    if export_data:
        st.divider()
        st.subheader("📈 Schedule Visualization")
        
        # Create Gantt-like chart
        gantt_data = []
        
        for entry in export_data:
            # Parse time slot
            start_str, end_str = entry['Time Slot'].split('-')
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            
            gantt_data.append({
                'Task': entry['Doctor'],
                'Start': datetime.combine(datetime.today(), start_time),
                'Finish': datetime.combine(datetime.today(), end_time),
                'Day': entry['Day']
            })
        
        if gantt_data:
            gantt_df = pd.DataFrame(gantt_data)
            
            # Create figure
            fig = px.timeline(
                gantt_df,
                x_start="Start",
                x_end="Finish",
                y="Day",
                color="Task",
                title="Doctor Schedule Gantt Chart"
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="Time",
                yaxis_title="Day",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
