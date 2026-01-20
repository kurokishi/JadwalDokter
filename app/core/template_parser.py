"""
Modul untuk parsing template jadwal
"""
import pandas as pd
import numpy as np
from datetime import datetime, time, date
from typing import Dict, List, Any, Optional, Tuple
import re
import io
from ..utils import parse_time

class TemplateParser:
    """Parser untuk berbagai format template jadwal"""
    
    def __init__(self, template_type: str = 'standard'):
        self.template_type = template_type
    
    def parse_file(self, file_content: bytes, filename: str) -> Tuple[pd.DataFrame, List[str]]:
        """Parse file upload"""
        warnings = []
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif filename.endswith(('.xlsx', '.xls', '.xlsm')):
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise ValueError(f"Format file tidak didukung: {filename}")
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Parse waktu jika dalam format yang berbeda
            df = self._parse_time_columns(df)
            
            return df, warnings
            
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}")
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardisasi nama kolom"""
        df_clean = df.copy()
        
        # Lowercase semua nama kolom dan hapus spasi
        df_clean.columns = [str(col).strip().lower().replace(' ', '_') for col in df_clean.columns]
        
        return df_clean
    
    def _parse_time_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse kolom waktu"""
        df_parsed = df.copy()
        
        # Handle berbagai format waktu
        time_columns = ['jam_mulai', 'jam_selesai', 'jam']
        
        for col in time_columns:
            if col in df_parsed.columns:
                # Coba parse waktu
                df_parsed[col] = df_parsed[col].apply(self._parse_time_cell)
        
        # Handle format 'jam' yang mengandung range (e.g., "08:00-16:00")
        if 'jam' in df_parsed.columns and 'jam_mulai' not in df_parsed.columns:
            df_parsed[['jam_mulai', 'jam_selesai']] = df_parsed['jam'].apply(
                lambda x: pd.Series(self._split_time_range(x))
            )
        
        return df_parsed
    
    def _parse_time_cell(self, cell_value: Any) -> str:
        """Parse satu cell waktu"""
        if pd.isna(cell_value):
            return ""
        
        # Convert to string
        cell_str = str(cell_value).strip()
        
        # Parse menggunakan utils
        parsed_time = parse_time(cell_str)
        
        if parsed_time:
            return parsed_time.strftime("%H:%M")
        else:
            # Coba format lainnya
            # Format: "8-10" atau "8:00-10:00"
            if '-' in cell_str:
                parts = cell_str.split('-')
                if len(parts) == 2:
                    time1 = parse_time(parts[0].strip())
                    if time1:
                        return time1.strftime("%H:%M")
            
            # Jika tidak bisa diparse, return as-is
            return cell_str
    
    def _split_time_range(self, time_range: str) -> Tuple[str, str]:
        """Split time range menjadi start dan end"""
        if pd.isna(time_range):
            return "", ""
        
        time_str = str(time_range).strip()
        
        # Pattern untuk range waktu
        patterns = [
            r'(\d{1,2}[:.]?\d{0,2})\s*[-–]\s*(\d{1,2}[:.]?\d{0,2})',  # 08:00-16:00
            r'(\d{1,2})\s*[-–]\s*(\d{1,2})',  # 8-16
        ]
        
        for pattern in patterns:
            match = re.search(pattern, time_str)
            if match:
                start = match.group(1)
                end = match.group(2)
                
                # Parse waktu
                start_time = parse_time(start)
                end_time = parse_time(end)
                
                if start_time and end_time:
                    return start_time.strftime("%H:%M"), end_time.strftime("%H:%M")
        
        # Jika tidak match pattern, coba parse sebagai waktu tunggal
        single_time = parse_time(time_str)
        if single_time:
            # Asumsi durasi 1 jam
            end_time = time((single_time.hour + 1) % 24, single_time.minute)
            return single_time.strftime("%H:%M"), end_time.strftime("%H:%M")
        
        return "", ""
    
    def create_sample_template(self, template_type: str = 'standard') -> pd.DataFrame:
        """Buat template sample"""
        if template_type == 'standard':
            data = {
                'nama_dokter': ['Dr. Andi Wijaya', 'Dr. Sari Dewi'],
                'spesialisasi': ['Umum', 'Anak'],
                'hari': ['Senin', 'Selasa'],
                'jam_mulai': ['08:00', '09:00'],
                'jam_selesai': ['12:00', '16:00'],
                'ruangan': ['101', '202'],
                'poliklinik': ['Poli Umum', 'Poli Anak'],
                'kapasitas': [20, 15],
                'catatan': ['Pagi', 'Full']
            }
        elif template_type == 'simple':
            data = {
                'dokter': ['Dr. Andi Wijaya', 'Dr. Sari Dewi'],
                'hari': ['Senin', 'Selasa'],
                'jam': ['08:00-12:00', '09:00-16:00']
            }
        else:
            raise ValueError(f"Template type tidak dikenal: {template_type}")
        
        return pd.DataFrame(data)
