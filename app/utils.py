"""
Utility functions for Jadwal Dokter App
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime, time
import streamlit as st

def clean_time_string(time_str: str) -> str:
    """
    Clean and standardize time string
    Converts various formats to HH:MM
    """
    if pd.isna(time_str) or time_str in ['', '-', 'nan', 'None']:
        return ""
    
    # Convert to string
    time_str = str(time_str).strip()
    
    # Remove Excel references
    if time_str.startswith('='):
        return "[Reference]"
    
    # Convert dot format to colon (07.30 -> 07:30)
    time_str = re.sub(r'(\d{1,2})\.(\d{2})', r'\1:\2', time_str)
    
    # Remove all spaces
    time_str = re.sub(r'\s+', '', time_str)
    
    # Ensure proper format
    if '-' in time_str:
        parts = time_str.split('-')
        if len(parts) == 2:
            start = clean_single_time(parts[0])
            end = clean_single_time(parts[1])
            return f"{start}-{end}"
    
    return clean_single_time(time_str)

def clean_single_time(time_str: str) -> str:
    """Clean single time string to HH:MM format"""
    if not time_str:
        return ""
    
    # Remove non-numeric and non-colon characters
    time_str = re.sub(r'[^\d:]', '', time_str)
    
    # Handle various formats
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) >= 2:
            hours = parts[0].zfill(2)
            minutes = parts[1].zfill(2) if len(parts[1]) > 0 else '00'
            return f"{hours}:{minutes}"
    
    # Handle HHMM format
    elif len(time_str) == 4:
        return f"{time_str[:2]}:{time_str[2:]}"
    
    return "00:00"

def parse_time_range(time_str: str):
    """Parse time range string to datetime.time objects"""
    if not time_str or time_str == '[Reference]':
        return None
    
    try:
        # Clean the string
        time_str = clean_time_string(time_str)
        
        if '-' in time_str:
            start_str, end_str = time_str.split('-')
            
            # Parse start time
            start_parts = start_str.split(':')
            start_hour = int(start_parts[0]) if len(start_parts) > 0 else 0
            start_minute = int(start_parts[1]) if len(start_parts) > 1 else 0
            start_time = time(start_hour, start_minute)
            
            # Parse end time
            end_parts = end_str.split(':')
            end_hour = int(end_parts[0]) if len(end_parts) > 0 else 0
            end_minute = int(end_parts[1]) if len(end_parts) > 1 else 0
            end_time = time(end_hour, end_minute)
            
            return (start_time, end_time)
    
    except Exception as e:
        st.warning(f"Error parsing time range '{time_str}': {str(e)}")
    
    return None

def calculate_duration(start_time: time, end_time: time) -> float:
    """Calculate duration in hours between two times"""
    if start_time and end_time:
        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = datetime.combine(datetime.today(), end_time)
        
        # Handle overnight schedules
        if end_dt < start_dt:
            end_dt = end_dt + timedelta(days=1)
        
        duration = (end_dt - start_dt).total_seconds() / 3600
        return round(duration, 2)
    
    return 0.0

def validate_dataframe(df: pd.DataFrame):
    """Validate DataFrame structure and content"""
    errors = []
    
    # Check if DataFrame is empty
    if df.empty:
        errors.append("DataFrame is empty")
        return False, errors
    
    # Required columns for standard format
    required_columns = ['doctor_name', 'specialty', 'day']
    
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    
    # Check for hafis format columns
    hafis_columns = ['working_hours', 'regular_schedule', 'executive_schedule']
    is_hafis_format = all(col in df.columns for col in hafis_columns)
    
    if not errors:
        return True, []
    
    return False, errors

def filter_by_day(df: pd.DataFrame, day: str) -> pd.DataFrame:
    """Filter DataFrame by day"""
    if 'day' in df.columns:
        return df[df['day'] == day].copy()
    return df

def filter_by_specialty(df: pd.DataFrame, specialty: str) -> pd.DataFrame:
    """Filter DataFrame by specialty"""
    if 'specialty' in df.columns:
        return df[df['specialty'] == specialty].copy()
    return df

def get_unique_values(df: pd.DataFrame, column: str):
    """Get unique values from a column"""
    if column in df.columns:
        return sorted(df[column].dropna().unique().tolist())
    return []

def create_summary_stats(df: pd.DataFrame):
    """Create summary statistics from DataFrame"""
    stats = {}
    
    if df is not None and not df.empty:
        stats['total_records'] = len(df)
        
        if 'doctor_name' in df.columns:
            stats['total_doctors'] = len(df['doctor_name'].unique())
        
        if 'specialty' in df.columns:
            stats['total_specialties'] = len(df['specialty'].unique())
        
        if 'day' in df.columns:
            stats['days_covered'] = len(df['day'].unique())
        
        # Calculate availability
        if 'available' in df.columns:
            stats['available_slots'] = int(df['available'].sum())
            stats['availability_rate'] = round((df['available'].sum() / len(df)) * 100, 1)
    
    return stats

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

def format_time_display(time_str: str, format_24h: bool = True) -> str:
    """Format time for display"""
    if not time_str or pd.isna(time_str):
        return "-"
    
    # If already formatted as range
    if '-' in time_str:
        parts = time_str.split('-')
        if len(parts) == 2:
            start = format_single_time_display(parts[0], format_24h)
            end = format_single_time_display(parts[1], format_24h)
            return f"{start} - {end}"
    
    return format_single_time_display(time_str, format_24h)

def format_single_time_display(time_str: str, format_24h: bool = True) -> str:
    """Format single time for display"""
    try:
        if ':' in time_str:
            hours, minutes = map(int, time_str.split(':'))
            
            if not format_24h:
                # Convert to 12-hour format
                period = "AM" if hours < 12 else "PM"
                hours_12 = hours if hours <= 12 else hours - 12
                if hours_12 == 0:
                    hours_12 = 12
                return f"{hours_12}:{minutes:02d} {period}"
            else:
                return f"{hours:02d}:{minutes:02d}"
    
    except:
        pass
    
    return time_str

# Need to import timedelta
from datetime import timedelta
