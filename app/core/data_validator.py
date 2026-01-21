"""
Data validation for schedule data
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class DataValidator:
    """Validate schedule data"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_grid_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate grid format DataFrame
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self.errors = []
        self.warnings = []
        
        # Check if DataFrame is empty
        if df.empty:
            self.errors.append("DataFrame kosong")
            return False, self.errors
        
        # Check required columns
        required_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            self.errors.append(f"Kolom yang diperlukan tidak ditemukan: {missing_cols}")
            return False, self.errors
        
        # Validate data types and values
        self._validate_poli(df['POLI'])
        self._validate_jenis(df['JENIS'])
        self._validate_hari(df['HARI'])
        self._validate_dokter(df['DOKTER'])
        self._validate_jam(df['JAM'])
        
        # Validate time slots
        self._validate_time_slots(df)
        
        # Check for duplicates
        self._check_duplicates(df)
        
        # Return validation result
        is_valid = len(self.errors) == 0
        
        return is_valid, self.errors + self.warnings
    
    def _validate_poli(self, poli_series):
        """Validate POLI column"""
        if poli_series.isna().any():
            self.errors.append("Ada nilai kosong di kolom POLI")
        
        # Check for very short values
        short_poli = poli_series[poli_series.str.len() < 2]
        if not short_poli.empty:
            self.warnings.append(f"POLI dengan nilai sangat pendek: {short_poli.unique()[:3]}")
    
    def _validate_jenis(self, jenis_series):
        """Validate JENIS column"""
        valid_values = ['Reguler', 'Eksekutif']
        
        invalid_values = jenis_series[~jenis_series.isin(valid_values)]
        if not invalid_values.empty:
            self.errors.append(f"Nilai JENIS tidak valid: {invalid_values.unique()}")
    
    def _validate_hari(self, hari_series):
        """Validate HARI column"""
        valid_days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        
        invalid_days = hari_series[~hari_series.isin(valid_days)]
        if not invalid_days.empty:
            self.errors.append(f"Hari tidak valid: {invalid_days.unique()}")
    
    def _validate_dokter(self, dokter_series):
        """Validate DOKTER column"""
        if dokter_series.isna().any():
            self.errors.append("Ada nilai kosong di kolom DOKTER")
        
        # Check for doctor names without "dr." prefix
        non_standard = dokter_series[~dokter_series.str.contains('dr\.', na=False)]
        if not non_standard.empty:
            self.warnings.append(f"Nama dokter tanpa prefix 'dr.': {non_standard.unique()[:3]}")
    
    def _validate_jam(self, jam_series):
        """Validate JAM column"""
        if jam_series.isna().any():
            self.errors.append("Ada nilai kosong di kolom JAM")
        
        # Check for invalid time formats
        for jam in jam_series.dropna():
            if not self._is_valid_jam_format(str(jam)):
                self.errors.append(f"Format JAM tidak valid: {jam}")
                break
    
    def _is_valid_jam_format(self, jam_str: str) -> bool:
        """Check if JAM string has valid format"""
        import re
        
        # Pattern for time ranges like "08:00-12:00" or "08:00-09:30, 10:00-12:00"
        time_range_pattern = r'^(\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})(\s*,\s*\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})*$'
        
        return bool(re.match(time_range_pattern, jam_str))
    
    def _validate_time_slots(self, df: pd.DataFrame):
        """Validate time slot columns"""
        # Get time slot columns (all columns except base columns)
        base_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM']
        time_cols = [col for col in df.columns if col not in base_cols]
        
        if not time_cols:
            self.warnings.append("Tidak ada kolom time slot ditemukan")
            return
        
        # Validate time slot values
        valid_values = ['', 'R', 'E']
        
        for col in time_cols:
            invalid_vals = df[col][~df[col].isin(valid_values)]
            if not invalid_vals.empty:
                self.errors.append(f"Nilai tidak valid di kolom {col}: {invalid_vals.unique()[:3]}")
                break
    
    def _check_duplicates(self, df: pd.DataFrame):
        """Check for duplicate schedule entries"""
        # Check for exact duplicates
        duplicate_rows = df[df.duplicated()]
        if not duplicate_rows.empty:
            self.warnings.append(f"Ditemukan {len(duplicate_rows)} baris duplikat")
        
        # Check for duplicates in key columns
        key_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER']
        duplicate_keys = df[df.duplicated(subset=key_cols, keep=False)]
        
        if not duplicate_keys.empty:
            duplicate_count = len(duplicate_keys) - duplicate_keys.drop_duplicates(subset=key_cols).shape[0]
            if duplicate_count > 0:
                self.errors.append(f"Ditemukan {duplicate_count} jadwal duplikat untuk kombinasi POLI-JENIS-HARI-DOKTER yang sama")
    
    def get_validation_summary(self, df: pd.DataFrame) -> Dict[str, any]:
        """Get validation summary"""
        is_valid, messages = self.validate_grid_data(df)
        
        summary = {
            'is_valid': is_valid,
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'errors': self.errors[:10],  # Limit to first 10 errors
            'warnings': self.warnings[:10],  # Limit to first 10 warnings
            'data_shape': df.shape,
            'unique_doctors': df['DOKTER'].nunique(),
            'unique_poli': df['POLI'].nunique(),
            'schedule_count': len(df),
            'validation_timestamp': datetime.now().isoformat()
        }
        
        return summary
