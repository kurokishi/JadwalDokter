"""
Utility functions for Jadwal Dokter Converter
"""
import streamlit as st
import pandas as pd
import re
from datetime import datetime, time
from typing import Optional, Tuple, List, Dict
import io


def init_session_state():
    """Initialize session state variables"""
    if 'grid_data' not in st.session_state:
        st.session_state.grid_data = None
    if 'original_data' not in st.session_state:
        st.session_state.original_data = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'parsed_data' not in st.session_state:
        st.session_state.parsed_data = None
    if 'conversion_stats' not in st.session_state:
        st.session_state.conversion_stats = {}
    if 'export_data' not in st.session_state:
        st.session_state.export_data = None


def parse_time_string(time_str: str) -> Optional[Tuple[str, str]]:
    """
    Parse time string to start and end time
    
    Args:
        time_str: Time string like "07:30-14:00" or "07.30-14.00"
    
    Returns:
        Tuple of (start_time, end_time) or None
    """
    if pd.isna(time_str) or not isinstance(time_str, str):
        return None
    
    # Clean the string
    time_str = str(time_str).strip()
    
    # Handle various formats
    time_str = time_str.replace('.', ':')
    
    # Pattern for time range
    pattern = r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})'
    match = re.search(pattern, time_str)
    
    if match:
        start_time = match.group(1)
        end_time = match.group(2)
        
        # Validate times
        if is_valid_time(start_time) and is_valid_time(end_time):
            return (start_time, end_time)
    
    # Try single time
    pattern_single = r'(\d{1,2}:\d{2})'
    match_single = re.search(pattern_single, time_str)
    
    if match_single:
        single_time = match_single.group(1)
        if is_valid_time(single_time):
            return (single_time, single_time)
    
    return None


def is_valid_time(time_str: str) -> bool:
    """Check if time string is valid"""
    try:
        if ':' in time_str:
            hour, minute = map(int, time_str.split(':'))
        else:
            return False
        
        return 0 <= hour < 24 and 0 <= minute < 60
    except:
        return False


def time_to_minutes(time_str: str) -> int:
    """Convert time string to minutes since midnight"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    except:
        return 0


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to time string"""
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02d}:{minute:02d}"


def create_time_slots(start_time: str, end_time: str, interval_minutes: int = 30) -> List[str]:
    """Create time slots between start and end time"""
    slots = []
    
    start_min = time_to_minutes(start_time)
    end_min = time_to_minutes(end_time)
    
    current = start_min
    while current < end_min:
        slots.append(minutes_to_time(current))
        current += interval_minutes
    
    return slots


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel bytes"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Jadwal')
    output.seek(0)
    return output.getvalue()


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes"""
    return df.to_csv(index=False).encode('utf-8')


def get_file_info(uploaded_file) -> Dict:
    """Get file information"""
    return {
        'name': uploaded_file.name,
        'size_kb': uploaded_file.size / 1024,
        'type': uploaded_file.type,
        'upload_time': datetime.now()
    }


def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def validate_excel_file(file) -> Tuple[bool, str]:
    """Validate uploaded Excel file"""
    try:
        # Check file extension
        if not file.name.lower().endswith(('.xlsx', '.xls')):
            return False, "File harus berformat Excel (.xlsx atau .xls)"
        
        # Check file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            return False, "File terlalu besar (maksimal 10MB)"
        
        # Try to read the file
        try:
            df = pd.read_excel(file, nrows=5)
            if df.empty:
                return False, "File Excel kosong"
        except Exception as e:
            return False, f"Tidak bisa membaca file Excel: {str(e)}"
        
        return True, "File valid"
    except Exception as e:
        return False, f"Error validasi file: {str(e)}"
