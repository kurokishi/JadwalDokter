"""
Utility functions for Jadwal Dokter Converter
"""
import streamlit as st
import pandas as pd
import re
import numpy as np
from datetime import datetime, time
from typing import Optional, Tuple, List, Dict, Any
import io


def init_session_state():
    """Initialize session state variables"""
    default_states = {
        'grid_data': None,
        'original_data': None,
        'file_name': None,
        'parsed_data': None,
        'conversion_stats': {},
        'export_data': None,
        'current_page': 'home',
        'validation_results': None,
        'upload_time': None
    }
    
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clean_dataframe(df: pd.DataFrame, fill_empty: str = '') -> pd.DataFrame:
    """
    Clean DataFrame by handling missing values and type conversions
    
    Args:
        df: DataFrame to clean
        fill_empty: Value to fill empty cells with (default: '')
    
    Returns:
        Cleaned DataFrame
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Fill NaN with specified value
    df_clean = df_clean.fillna(fill_empty)
    
    # Convert all object columns to string and strip whitespace
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            # Replace None with empty string before string conversion
            df_clean[col] = df_clean[col].apply(
                lambda x: '' if x is None else str(x).strip()
            )
    
    # Remove rows where all values are empty
    df_clean = df_clean[~df_clean.apply(lambda row: all(v == fill_empty for v in row), axis=1)]
    
    return df_clean


def safe_sort(values: List[Any]) -> List[str]:
    """
    Safely sort a list that may contain None or mixed types
    
    Args:
        values: List of values to sort
        
    Returns:
        Sorted list of strings
    """
    if not values:
        return []
    
    # Filter out None and convert to string
    str_values = []
    for v in values:
        if v is not None and pd.notna(v):
            str_val = str(v).strip()
            if str_val:  # Only add non-empty strings
                str_values.append(str_val)
    
    # Remove duplicates and sort
    unique_values = list(set(str_values))
    return sorted(unique_values)


def get_unique_sorted(values: pd.Series, include_all: bool = True) -> List[str]:
    """
    Get unique sorted values from a pandas Series
    
    Args:
        values: pandas Series
        include_all: Whether to include 'Semua' option
        
    Returns:
        List of sorted unique values
    """
    # Clean the series
    cleaned = values.dropna()
    cleaned = cleaned[cleaned.notnull()]
    cleaned = cleaned.astype(str).str.strip()
    cleaned = cleaned[cleaned != '']
    
    # Get unique values
    unique_vals = cleaned.unique().tolist()
    
    # Sort
    sorted_vals = sorted(unique_vals)
    
    # Add 'Semua' option if requested
    if include_all and sorted_vals:
        return ['Semua'] + sorted_vals
    elif sorted_vals:
        return sorted_vals
    else:
        return ['Semua'] if include_all else []


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
        if pd.isna(time_str) or not time_str:
            return 0
            
        hour, minute = map(int, str(time_str).split(':'))
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


def format_datetime(dt: datetime) -> str:
    """Format datetime to readable string"""
    return dt.strftime("%d %B %Y %H:%M:%S")


def log_error(error: Exception, context: str = ""):
    """Log error with context"""
    error_msg = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    print(f"❌ {error_msg}")
    
    # Also log to Streamlit session state for debugging
    if 'error_log' not in st.session_state:
        st.session_state.error_log = []
    
    st.session_state.error_log.append({
        'timestamp': datetime.now(),
        'context': context,
        'error': str(error),
        'type': type(error).__name__
    })
