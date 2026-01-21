"""
Data validation for schedule data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from app.utils import clean_dataframe


class DataValidator:
    """Validate schedule data"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.validation_log = []
    
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
        self.validation_log = []
        
        # Log validation start
        self._log_validation("START", "Starting validation")
        
        # Check if DataFrame is None or empty
        if df is None:
            self.errors.append("DataFrame is None")
            self._log_validation("ERROR", "DataFrame is None")
            return False, self.errors
        
        if df.empty:
            self.errors.append("DataFrame kosong")
            self._log_validation("ERROR", "DataFrame kosong")
            return False, self.errors
        
        # Clean the DataFrame before validation
        df_clean = self._clean_data_for_validation(df)
        self._log_validation("INFO", f"Cleaned DataFrame shape: {df_clean.shape}")
        
        # Check required columns
        required_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM']
        missing_cols = [col for col in required_cols if col not in df_clean.columns]
        
        if missing_cols:
            self.errors.append(f"Kolom yang diperlukan tidak ditemukan: {missing_cols}")
            self._log_validation("ERROR", f"Missing columns: {missing_cols}")
        
        # Only proceed with validation if we have the required columns
        if not self.errors:
            # Validate data types and values
            self._validate_poli(df_clean['POLI'] if 'POLI' in df_clean.columns else pd.Series())
            self._validate_jenis(df_clean['JENIS'] if 'JENIS' in df_clean.columns else pd.Series())
            self._validate_hari(df_clean['HARI'] if 'HARI' in df_clean.columns else pd.Series())
            self._validate_dokter(df_clean['DOKTER'] if 'DOKTER' in df_clean.columns else pd.Series())
            self._validate_jam(df_clean['JAM'] if 'JAM' in df_clean.columns else pd.Series())
            
            # Validate time slots
            self._validate_time_slots(df_clean)
            
            # Check for duplicates
            self._check_duplicates(df_clean)
        
        # Log validation results
        is_valid = len(self.errors) == 0
        validation_status = "VALID" if is_valid else "INVALID"
        self._log_validation("RESULT", f"Validation {validation_status}: {len(self.errors)} errors, {len(self.warnings)} warnings")
        
        return is_valid, self.errors + self.warnings
    
    def _clean_data_for_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data before validation"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Use the utility function
        df_clean = clean_dataframe(df)
        
        # Additional cleaning for validation
        # Ensure all required columns exist (add empty if missing)
        required_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM']
        for col in required_cols:
            if col not in df_clean.columns:
                df_clean[col] = ''
        
        return df_clean
    
    def _validate_poli(self, poli_series):
        """Validate POLI column"""
        if poli_series.empty:
            self.warnings.append("Kolom POLI kosong")
            self._log_validation("WARNING", "POLI column is empty")
            return
        
        # Check for None/NaN values
        null_count = poli_series.isna().sum()
        if null_count > 0:
            self.warnings.append(f"Ada {null_count} nilai kosong di kolom POLI")
            self._log_validation("WARNING", f"POLI has {null_count} null values")
        
        # Check for empty strings
        empty_count = (poli_series == '').sum()
        if empty_count > 0:
            self.warnings.append(f"Ada {empty_count} nilai string kosong di kolom POLI")
            self._log_validation("WARNING", f"POLI has {empty_count} empty strings")
    
    def _validate_jenis(self, jenis_series):
        """Validate JENIS column"""
        if jenis_series.empty:
            self.warnings.append("Kolom JENIS kosong")
            self._log_validation("WARNING", "JENIS column is empty")
            return
        
        valid_values = ['Reguler', 'Eksekutif']
        
        # Clean the series
        clean_series = jenis_series.dropna().astype(str).str.strip()
        
        invalid_values = clean_series[~clean_series.isin(valid_values)]
        if not invalid_values.empty:
            unique_invalid = invalid_values.unique()[:3]  # Show only first 3
            self.errors.append(f"Nilai JENIS tidak valid: {list(unique_invalid)}")
            self._log_validation("ERROR", f"Invalid JENIS values: {list(unique_invalid)}")
    
    def _validate_hari(self, hari_series):
        """Validate HARI column"""
        if hari_series.empty:
            self.warnings.append("Kolom HARI kosong")
            self._log_validation("WARNING", "HARI column is empty")
            return
        
        valid_days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        
        # Clean and uppercase the series
        clean_series = hari_series.dropna().astype(str).str.strip().str.upper()
        
        invalid_days = clean_series[~clean_series.isin(valid_days)]
        if not invalid_days.empty:
            unique_invalid = invalid_days.unique()[:3]
            self.errors.append(f"Hari tidak valid: {list(unique_invalid)}")
            self._log_validation("ERROR", f"Invalid HARI values: {list(unique_invalid)}")
    
    def _validate_dokter(self, dokter_series):
        """Validate DOKTER column"""
        if dokter_series.empty:
            self.warnings.append("Kolom DOKTER kosong")
            self._log_validation("WARNING", "DOKTER column is empty")
            return
        
        # Check for None/NaN values
        null_count = dokter_series.isna().sum()
        if null_count > 0:
            self.errors.append(f"Ada {null_count} nilai kosong di kolom DOKTER")
            self._log_validation("ERROR", f"DOKTER has {null_count} null values")
        
        # Check for empty strings
        empty_count = (dokter_series == '').sum()
        if empty_count > 0:
            self.warnings.append(f"Ada {empty_count} nilai string kosong di kolom DOKTER")
            self._log_validation("WARNING", f"DOKTER has {empty_count} empty strings")
    
    def _validate_jam(self, jam_series):
        """Validate JAM column"""
        if jam_series.empty:
            self.warnings.append("Kolom JAM kosong")
            self._log_validation("WARNING", "JAM column is empty")
            return
        
        # Check for None/NaN values
        null_count = jam_series.isna().sum()
        if null_count > 0:
            self.warnings.append(f"Ada {null_count} nilai kosong di kolom JAM")
            self._log_validation("WARNING", f"JAM has {null_count} null values")
    
    def _validate_time_slots(self, df: pd.DataFrame):
        """Validate time slot columns"""
        # Get time slot columns (all columns except base columns)
        base_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM']
        time_cols = [col for col in df.columns if col not in base_cols]
        
        if not time_cols:
            self.warnings.append("Tidak ada kolom time slot ditemukan")
            self._log_validation("WARNING", "No time slot columns found")
            return
        
        # Validate time slot values
        valid_values = ['', 'R', 'E']
        
        for col in time_cols:
            if col not in df.columns:
                continue
                
            # Get unique values
            unique_vals = df[col].dropna().unique()
            
            for val in unique_vals:
                if val not in valid_values:
                    self.errors.append(f"Nilai tidak valid '{val}' di kolom {col}")
                    self._log_validation("ERROR", f"Invalid value '{val}' in column {col}")
                    break  # Stop after first error per column
    
    def _check_duplicates(self, df: pd.DataFrame):
        """Check for duplicate schedule entries"""
        if df.empty:
            return
        
        # Check for exact duplicates
        duplicate_rows = df[df.duplicated()]
        if not duplicate_rows.empty:
            self.warnings.append(f"Ditemukan {len(duplicate_rows)} baris duplikat")
            self._log_validation("WARNING", f"Found {len(duplicate_rows)} duplicate rows")
        
        # Check for duplicates in key columns
        key_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER']
        key_cols_exist = [col for col in key_cols if col in df.columns]
        
        if len(key_cols_exist) >= 3:  # Need at least 3 key columns
            duplicate_keys = df[df.duplicated(subset=key_cols_exist, keep=False)]
            
            if not duplicate_keys.empty:
                duplicate_count = len(duplicate_keys) - duplicate_keys.drop_duplicates(subset=key_cols_exist).shape[0]
                if duplicate_count > 0:
                    self.errors.append(f"Ditemukan {duplicate_count} jadwal duplikat untuk kombinasi yang sama")
                    self._log_validation("ERROR", f"Found {duplicate_count} duplicate schedules")
    
    def _log_validation(self, level: str, message: str):
        """Log validation message"""
        log_entry = {
            'timestamp': datetime.now(),
            'level': level,
            'message': message
        }
        self.validation_log.append(log_entry)
    
    def get_validation_summary(self, df: pd.DataFrame) -> Dict[str, any]:
        """Get validation summary"""
        is_valid, messages = self.validate_grid_data(df)
        
        # Get basic stats from cleaned DataFrame
        df_clean = self._clean_data_for_validation(df) if df is not None else pd.DataFrame()
        
        summary = {
            'is_valid': is_valid,
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'errors': self.errors[:5],  # Limit to first 5 errors
            'warnings': self.warnings[:5],  # Limit to first 5 warnings
            'data_shape': df_clean.shape if not df_clean.empty else (0, 0),
            'unique_doctors': df_clean['DOKTER'].nunique() if 'DOKTER' in df_clean.columns else 0,
            'unique_poli': df_clean['POLI'].nunique() if 'POLI' in df_clean.columns else 0,
            'schedule_count': len(df_clean),
            'validation_timestamp': datetime.now().isoformat(),
            'validation_log_count': len(self.validation_log)
        }
        
        return summary
