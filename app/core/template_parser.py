"""
Modul untuk parsing template jadwal
"""
import pandas as pd
import numpy as np
from datetime import datetime, time, date
from typing import Dict, List, Any, Optional, Tuple
import re
import io
from ..config import config
from ..utils import parse_time

class TemplateParser:
    """Parser untuk berbagai format template jadwal"""
    
    # Template patterns untuk berbagai format
    TEMPLATE_PATTERNS = {
        'standard': {
            'required': ['nama_dokter', 'spesialisasi', 'hari', 'jam_mulai', 'jam_selesai'],
            'optional': ['ruangan', 'poliklinik', 'kapasitas', 'catatan'],
            'aliases': {
                'dokter': 'nama_dokter',
                'doctor': 'nama_dokter',
                'specialization': 'spesialisasi',
                'day': 'hari',
                'start': 'jam_mulai',
                'end': 'jam_selesai',
                'start_time': 'jam_mulai',
                'end_time': 'jam_selesai',
                'room': 'ruangan',
                'clinic': 'poliklinik',
                'capacity': 'kapasitas',
                'notes': 'catatan'
            }
        },
        'simple': {
            'required': ['dokter', 'hari', 'jam'],
            'aliases': {
                'doctor': 'dokter',
                'day': 'hari',
                'time': 'jam'
            }
        }
    }
    
    def __init__(self, template_type: str = 'standard'):
        self.template_type = template_type
        self.pattern = self.TEMPLATE_PATTERNS.get(template_type, self.TEMPLATE_PATTERNS['standard'])
    
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
            
            # Validate template structure
            is_valid, validation_warnings = self._validate_template_structure(df)
            warnings.extend(validation_warnings)
            
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
        
        # Apply aliases
        column_mapping = {}
        for col in df_clean.columns:
            standardized = self._standardize_column_name(col)
            if standardized:
                column_mapping[col] = standardized
        
        df_clean = df_clean.rename(columns=column_mapping)
        
        return df_clean
    
    def _standardize_column_name(self, column_name: str) -> Optional[str]:
        """Standardisasi nama kolom berdasarkan aliases"""
        # Cek di aliases
        for alias, standard in self.pattern.get('aliases', {}).items():
            if alias in column_name.lower():
                return standard
        
        # Jika tidak ditemukan di aliases, kembalikan aslinya
        return column_name
    
    def _validate_template_structure(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validasi struktur template"""
        warnings = []
        
        required_cols = self.pattern.get('required', [])
        missing_cols = []
        
        for col in required_cols:
            if col not in df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            warnings.append(f"Kolom yang diperlukan tidak ditemukan: {', '.join(missing_cols)}")
            return False, warnings
        
        return True, warnings
    
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
    
    def detect_template_type(self, df: pd.DataFrame) -> str:
        """Deteksi tipe template berdasarkan kolom yang ada"""
        columns = set(df.columns.str.lower())
        
        for template_name, pattern in self.TEMPLATE_PATTERNS.items():
            required = set(pattern.get('required', []))
            if required.issubset(columns):
                return template_name
        
        # Cek dengan aliases
        for template_name, pattern in self.TEMPLATE_PATTERNS.items():
            required = pattern.get('required', [])
            aliases = pattern.get('aliases', {})
            
            # Check jika required columns ada atau ada aliasesnya
            found_count = 0
            for req_col in required:
                if req_col in columns:
                    found_count += 1
                else:
                    # Cek aliases
                    for alias, standard in aliases.items():
                        if standard == req_col and alias in columns:
                            found_count += 1
                            break
            
            if found_count >= len(required) * 0.8:  # 80% match
                return template_name
        
        return 'unknown'
    
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
