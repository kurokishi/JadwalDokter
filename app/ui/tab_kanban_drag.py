"""
Kanban drag tab UI component - SIMPLIFIED
"""
import streamlit as st
import pandas as pd

def display_kanban_tab():
    """Display kanban drag tab content"""
    
    st.header("🧩 Kanban Drag Schedule")
    
    if 'data' not in st.session_state or not st.session_state.data_loaded:
        st.warning("⚠️ Silakan upload data terlebih dahulu di tab 'Upload Data'")
        return
    
    df = st.session_state.data
    
    st.info("**Simple Kanban Interface** - Select doctors and assign them to time slots.")
    
    # Initialize kanban data
    if 'kanban_data' not in st.session_state:
        st.session_state.kanban_data = {}
    
    # Simple interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Doctors")
        if 'doctor_name' in df.columns:
            doctors = sorted(df['doctor_name'].unique().tolist())
            selected_doctors = st.multiselect(
                "Select doctors:",
                doctors,
                default=doctors[:3] if len(doctors) > 3 else doctors
            )
    
    with col2:
        st.subheader("Time Slots")
        time_slots = st.text_area(
            "Enter time slots (one per line):",
            "08:00-09:00\n09:00-10:00\n10:00-11:00\n11:00-12:00\n13:00-14:00"
        ).split('\n')
    
    if selected_doctors and time_slots:
        # Create simple assignment table
        st.subheader("Assign Doctors to Time Slots")
        
        assignment_df = pd.DataFrame(index=selected_doctors, columns=time_slots)
        edited_df = st.data_editor(
            assignment_df,
            use_container_width=True,
            height=300
        )
        
        # Save assignments
        if st.button("💾 Save Assignments"):
            st.session_state.kanban_data = edited_df.to_dict()
            st.success("Assignments saved!")
            
            # Show summary
            st.subheader("📊 Assignment Summary")
            
            total_assignments = edited_df.notna().sum().sum()
            st.metric("Total Assignments", total_assignments)
            
            # Export
            csv = edited_df.to_csv()
            st.download_button(
                label="📥 Download Assignments",
                data=csv,
                file_name="doctor_assignments.csv",
                mime="text/csv"
            )

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
