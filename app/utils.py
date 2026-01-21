"""
Utility functions for Jadwal Dokter App
"""
import pandas as pd
import re
from datetime import datetime, time, timedelta

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

def get_unique_values(df: pd.DataFrame, column: str):
    """Get unique values from a column"""
    if column in df.columns:
        return sorted(df[column].dropna().unique().tolist())
    return []
