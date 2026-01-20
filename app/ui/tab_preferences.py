"""
Preferences tab UI component
"""
import streamlit as st
import json
from app.config import AppConfig

def display_preferences_tab():
    """Display preferences tab content"""
    
    st.header("⚙️ Preferences")
    
    # Initialize preferences if not exists
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {
            'working_hours_start': '08:00',
            'working_hours_end': '16:00',
            'days_to_show': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'view_mode': 'table',
            'time_format': '24h',
            'theme': 'light',
            'language': 'id'
        }
    
    preferences = st.session_state.preferences
    
    # Preferences form
    with st.form("preferences_form"):
        st.subheader("General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            working_start = st.time_input(
                "Working Hours Start",
                value=datetime.strptime(preferences['working_hours_start'], '%H:%M').time()
            )
        
        with col2:
            working_end = st.time_input(
                "Working Hours End",
                value=datetime.strptime(preferences['working_hours_end'], '%H:%M').time()
            )
        
        # Days to show
        st.subheader("Days to Display")
        days_options = AppConfig.DAYS_OF_WEEK
        selected_days = st.multiselect(
            "Select days to display in schedule:",
            days_options,
            default=preferences['days_to_show']
        )
        
        # View mode
        st.subheader("Display Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            view_mode = st.selectbox(
                "Default View Mode",
                ['table', 'grid', 'timeline'],
                index=['table', 'grid', 'timeline'].index(preferences['view_mode'])
            )
        
        with col2:
            time_format = st.radio(
                "Time Format",
                ['24h', '12h'],
                index=0 if preferences['time_format'] == '24h' else 1,
                horizontal=True
            )
        
        # Theme
        theme = st.selectbox(
            "Theme",
            ['light', 'dark', 'system'],
            index=['light', 'dark', 'system'].index(preferences.get('theme', 'light'))
        )
        
        # Language
        language = st.selectbox(
            "Language",
            ['id', 'en'],
            format_func=lambda x: 'Bahasa Indonesia' if x == 'id' else 'English',
            index=0 if preferences.get('language', 'id') == 'id' else 1
        )
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Preferences", type="primary")
        
        if submitted:
            # Update preferences
            st.session_state.preferences.update({
                'working_hours_start': working_start.strftime('%H:%M'),
                'working_hours_end': working_end.strftime('%H:%M'),
                'days_to_show': selected_days,
                'view_mode': view_mode,
                'time_format': time_format,
                'theme': theme,
                'language': language
            })
            
            st.success("✅ Preferences saved successfully!")
    
    # Export/Import preferences
    st.divider()
    st.subheader("Export/Import Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export preferences
        preferences_json = json.dumps(st.session_state.preferences, indent=2)
        
        st.download_button(
            label="📥 Export Preferences",
            data=preferences_json,
            file_name="jadwal_dokter_preferences.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Import preferences
        uploaded_preferences = st.file_uploader(
            "Import preferences file",
            type=['json'],
            key="preferences_upload"
        )
        
        if uploaded_preferences is not None:
            try:
                imported_prefs = json.load(uploaded_preferences)
                st.session_state.preferences.update(imported_prefs)
                st.success("✅ Preferences imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error importing preferences: {str(e)}")
    
    # Reset to defaults
    st.divider()
    st.subheader("Reset Settings")
    
    if st.button("🔄 Reset to Defaults", type="secondary", use_container_width=True):
        st.session_state.preferences = {
            'working_hours_start': '08:00',
            'working_hours_end': '16:00',
            'days_to_show': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'view_mode': 'table',
            'time_format': '24h',
            'theme': 'light',
            'language': 'id'
        }
        st.success("✅ Preferences reset to defaults!")
        st.rerun()
    
    # Current preferences display
    st.divider()
    st.subheader("Current Preferences")
    
    with st.expander("View Current Settings"):
        st.json(st.session_state.preferences)

# Need to import datetime for time parsing
from datetime import datetime
