"""
Utility functions untuk aplikasi Jadwal Dokter
"""
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, time, date, timedelta
import base64
import io
from typing import Dict, List, Any, Optional, Tuple, Union
import json
import hashlib
import re

def initialize_session_state():
    """Initialize semua session state yang diperlukan"""
    default_states = {
        'uploaded_data': None,
        'file_name': None,
        'upload_time': None,
        'schedule_data': None,
        'validation_errors': [],
        'doctors_list': [],
        'specializations': [],
        'preferences': {},
        'current_view': 'home',
        'notification': None,
        'total_doctors': 0,
        'total_schedules': 0,
        'total_hours': 0,
        'conflicts': []
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def show_message(message: str, message_type: str = "info"):
    """Tampilkan message dengan format yang konsisten"""
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    icon = icons.get(message_type, "ℹ️")
    
    if message_type == "success":
        st.success(f"{icon} {message}")
    elif message_type == "error":
        st.error(f"{icon} {message}")
    elif message_type == "warning":
        st.warning(f"{icon} {message}")
    else:
        st.info(f"{icon} {message}")

def format_time(time_obj: Union[time, str]) -> str:
    """Format waktu menjadi string HH:MM"""
    if isinstance(time_obj, str):
        return time_obj
    elif isinstance(time_obj, time):
        return time_obj.strftime("%H:%M")
    elif pd.isna(time_obj):
        return ""
    else:
        return str(time_obj)

def parse_time(time_str: str) -> Optional[time]:
    """Parse string waktu ke objek time"""
    if pd.isna(time_str) or not time_str:
        return None
    
    try:
        # Coba berbagai format
        time_str = str(time_str).strip().lower()
        
        # Handle format 08:00, 8:00, 08.00, 8.00
        time_str = time_str.replace('.', ':')
        
        # Handle AM/PM
        is_pm = 'pm' in time_str or 'sore' in time_str or 'malam' in time_str
        is_am = 'am' in time_str or 'pagi' in time_str or 'siang' in time_str
        
        # Hapus kata-kata non-numeric
        time_str = re.sub(r'[^0-9:]', '', time_str)
        
        if ':' in time_str:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
        else:
            if len(time_str) <= 2:
                hour = int(time_str)
                minute = 0
            else:
                hour = int(time_str[:2])
                minute = int(time_str[2:4]) if len(time_str) >= 4 else 0
        
        # Adjust untuk PM
        if is_pm and hour < 12:
            hour += 12
        elif is_am and hour == 12:
            hour = 0
        
        # Validasi jam dan menit
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour, minute)
        else:
            return None
    except:
        return None

def calculate_duration(start_time: time, end_time: time) -> float:
    """Hitung durasi dalam jam"""
    if not start_time or not end_time:
        return 0
    
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    
    if end_minutes < start_minutes:
        end_minutes += 24 * 60  # Handle overnight
    
    return (end_minutes - start_minutes) / 60.0

def create_download_link(df: pd.DataFrame, filename: str = "data.csv", 
                        file_type: str = "csv") -> str:
    """Create download link untuk DataFrame"""
    if file_type == "csv":
        data = df.to_csv(index=False)
        mime_type = "text/csv"
        file_ext = "csv"
    elif file_type == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        data = output.getvalue()
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        file_ext = "xlsx"
    else:
        raise ValueError("file_type harus 'csv' atau 'excel'")
    
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}.{file_ext}">Download {filename}.{file_ext}</a>'
    return href

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """Validasi DataFrame"""
    errors = []
    
    # Cek jika DataFrame kosong
    if df.empty:
        errors.append("DataFrame kosong")
        return False, errors
    
    # Cek kolom yang diperlukan
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Kolom yang hilang: {', '.join(missing_columns)}")
    
    # Cek duplikat
    duplicate_rows = df.duplicated().sum()
    if duplicate_rows > 0:
        errors.append(f"Terdapat {duplicate_rows} baris duplikat")
    
    # Cek nilai null di kolom penting
    for col in required_columns:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                errors.append(f"Kolom '{col}' memiliki {null_count} nilai kosong")
    
    return len(errors) == 0, errors

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Bersihkan DataFrame"""
    # Buat copy
    df_clean = df.copy()
    
    # Hapus duplikat
    df_clean = df_clean.drop_duplicates()
    
    # Trim string columns
    for col in df_clean.select_dtypes(include=['object']).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    
    # Ubah ke huruf kapital untuk kolom tertentu
    capitalize_cols = ['nama_dokter', 'spesialisasi', 'hari', 'ruangan', 'poliklinik']
    for col in capitalize_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].str.title()
    
    return df_clean

def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
    """Dapatkan nilai unik dari kolom"""
    if column not in df.columns or df.empty:
        return []
    
    return sorted(df[column].dropna().unique().tolist())

def calculate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Hitung statistik dari DataFrame"""
    stats = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().sum(),
        "duplicate_rows": df.duplicated().sum()
    }
    
    # Tambahkan statistik berdasarkan kolom yang ada
    if 'nama_dokter' in df.columns:
        stats["unique_doctors"] = df['nama_dokter'].nunique()
    
    if 'spesialisasi' in df.columns:
        stats["unique_specializations"] = df['spesialisasi'].nunique()
    
    if 'hari' in df.columns:
        stats["unique_days"] = df['hari'].nunique()
    
    # Hitung total jam kerja jika ada kolom waktu
    if all(col in df.columns for col in ['jam_mulai', 'jam_selesai']):
        total_hours = 0
        for _, row in df.iterrows():
            start = parse_time(row['jam_mulai'])
            end = parse_time(row['jam_selesai'])
            if start and end:
                total_hours += calculate_duration(start, end)
        stats["total_working_hours"] = round(total_hours, 2)
    
    return stats
