"""
Modul untuk membersihkan dan memproses data
"""
import pandas as pd
import numpy as np
from datetime import datetime, time, date
from typing import Dict, List, Any, Optional, Tuple
import re
from ..config import config
from ..utils import parse_time, format_time

class DataCleaner:
    """Class untuk membersihkan data jadwal dokter"""
    
    def __init__(self):
        self.cleaning_rules = {
            'trim_spaces': True,
            'capitalize_names': True,
            'standardize_time': True,
            'remove_duplicates': True,
            'fill_missing': False
        }
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Bersihkan seluruh DataFrame"""
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        # 1. Hapus duplikat
        if self.cleaning_rules['remove_duplicates']:
            initial_count = len(df_clean)
            df_clean = df_clean.drop_duplicates()
            removed = initial_count - len(df_clean)
        
        # 2. Trim whitespace untuk semua string columns
        if self.cleaning_rules['trim_spaces']:
            for col in df_clean.select_dtypes(include=['object']).columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
        
        # 3. Kapitalisasi nama dan spesialisasi
        if self.cleaning_rules['capitalize_names']:
            capitalize_cols = ['nama_dokter', 'spesialisasi', 'hari', 'ruangan']
            for col in capitalize_cols:
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].str.title()
        
        # 4. Standardisasi waktu
        if self.cleaning_rules['standardize_time'] and 'jam_mulai' in df_clean.columns and 'jam_selesai' in df_clean.columns:
            df_clean = self._standardize_times(df_clean)
        
        # 5. Validasi dan koreksi data
        df_clean = self._validate_and_correct(df_clean)
        
        return df_clean
    
    def _standardize_times(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardisasi format waktu"""
        df_clean = df.copy()
        
        # Process jam_mulai
        if 'jam_mulai' in df_clean.columns:
            df_clean['jam_mulai_parsed'] = df_clean['jam_mulai'].apply(parse_time)
            df_clean['jam_mulai'] = df_clean['jam_mulai_parsed'].apply(
                lambda x: format_time(x) if x else None
            )
        
        # Process jam_selesai
        if 'jam_selesai' in df_clean.columns:
            df_clean['jam_selesai_parsed'] = df_clean['jam_selesai'].apply(parse_time)
            df_clean['jam_selesai'] = df_clean['jam_selesai_parsed'].apply(
                lambda x: format_time(x) if x else None
            )
        
        # Hapus kolom parsing sementara
        df_clean = df_clean.drop(columns=['jam_mulai_parsed', 'jam_selesai_parsed'], errors='ignore')
        
        return df_clean
    
    def _validate_and_correct(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validasi dan koreksi data"""
        df_clean = df.copy()
        
        # Validasi durasi waktu
        if all(col in df_clean.columns for col in ['jam_mulai', 'jam_selesai']):
            for idx, row in df_clean.iterrows():
                start = parse_time(row['jam_mulai'])
                end = parse_time(row['jam_selesai'])
                
                if start and end:
                    # Cek jika start > end (mungkin ada kesalahan)
                    start_minutes = start.hour * 60 + start.minute
                    end_minutes = end.hour * 60 + end.minute
                    
                    if end_minutes < start_minutes:
                        # Assume itu jadwal overnight atau swap
                        df_clean.at[idx, 'jam_mulai'], df_clean.at[idx, 'jam_selesai'] = (
                            df_clean.at[idx, 'jam_selesai'], 
                            df_clean.at[idx, 'jam_mulai']
                        )
        
        # Validasi hari
        if 'hari' in df_clean.columns:
            valid_days = config.WORK_DAYS + config.WEEKEND
            mask = df_clean['hari'].isin(valid_days)
        
        return df_clean
    
    def extract_unique_values(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Extract nilai unik dari DataFrame"""
        unique_values = {}
        
        if 'nama_dokter' in df.columns:
            unique_values['doctors'] = sorted(df['nama_dokter'].dropna().unique().tolist())
        
        if 'spesialisasi' in df.columns:
            unique_values['specializations'] = sorted(df['spesialisasi'].dropna().unique().tolist())
        
        if 'hari' in df.columns:
            unique_values['days'] = sorted(df['hari'].dropna().unique().tolist())
        
        return unique_values
