"""
Modul untuk validasi data
"""
import pandas as pd
import numpy as np
from datetime import datetime, time
from typing import Dict, List, Any, Optional, Tuple
import re
from ..config import config
from ..utils import parse_time

class DataValidator:
    """Class untuk validasi data jadwal dokter"""
    
    def __init__(self):
        self.validation_rules = {
            'required_columns': config.REQUIRED_COLUMNS,
            'time_format': r'^\d{1,2}[:.]\d{2}$|^\d{1,2}\s*[apAP][mM]$',
            'min_duration': 0.5,  # 30 menit minimum
            'max_duration': 12,   # 12 jam maximum
            'valid_days': config.WORK_DAYS + config.WEEKEND
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validasi seluruh DataFrame"""
        errors = []
        
        # 1. Cek jika DataFrame kosong
        if df.empty:
            errors.append("DataFrame kosong")
            return False, errors
        
        # 2. Cek kolom yang diperlukan
        missing_cols = self._check_required_columns(df)
        if missing_cols:
            errors.append(f"Kolom yang diperlukan tidak ditemukan: {', '.join(missing_cols)}")
        
        # 3. Validasi setiap baris
        row_errors = self._validate_rows(df)
        errors.extend(row_errors)
        
        # 4. Validasi konsistensi data
        consistency_errors = self._validate_consistency(df)
        errors.extend(consistency_errors)
        
        return len(errors) == 0, errors
    
    def _check_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Cek kolom yang diperlukan"""
        missing = []
        for col in self.validation_rules['required_columns']:
            if col not in df.columns:
                missing.append(col)
        return missing
    
    def _validate_rows(self, df: pd.DataFrame) -> List[str]:
        """Validasi setiap baris data"""
        errors = []
        
        for idx, row in df.iterrows():
            row_errors = self._validate_single_row(row, idx)
            if row_errors:
                errors.extend(row_errors)
        
        return errors
    
    def _validate_single_row(self, row: pd.Series, row_idx: int) -> List[str]:
        """Validasi satu baris data"""
        errors = []
        
        # 1. Validasi data dokter
        if 'nama_dokter' in row:
            doctor = str(row['nama_dokter']).strip()
            if not doctor or doctor.lower() in ['', 'nan', 'null', 'undefined']:
                errors.append(f"Baris {row_idx}: Nama dokter tidak valid")
        
        # 2. Validasi hari
        if 'hari' in row:
            day = str(row['hari']).strip().title()
            valid_days = self.validation_rules['valid_days']
            if day not in valid_days:
                errors.append(f"Baris {row_idx}: Hari '{day}' tidak valid. Hari yang valid: {', '.join(valid_days)}")
        
        # 3. Validasi waktu
        if 'jam_mulai' in row and 'jam_selesai' in row:
            start_time = parse_time(row['jam_mulai'])
            end_time = parse_time(row['jam_selesai'])
            
            if not start_time:
                errors.append(f"Baris {row_idx}: Format waktu mulai '{row['jam_mulai']}' tidak valid")
            
            if not end_time:
                errors.append(f"Baris {row_idx}: Format waktu selesai '{row['jam_selesai']}' tidak valid")
            
            if start_time and end_time:
                # Validasi durasi
                start_minutes = start_time.hour * 60 + start_time.minute
                end_minutes = end_time.hour * 60 + end_time.minute
                
                if end_minutes < start_minutes:
                    end_minutes += 24 * 60  # Handle overnight
                
                duration_hours = (end_minutes - start_minutes) / 60
                
                if duration_hours < self.validation_rules['min_duration']:
                    errors.append(f"Baris {row_idx}: Durasi terlalu pendek ({duration_hours:.2f} jam). Minimum: {self.validation_rules['min_duration']} jam")
                
                if duration_hours > self.validation_rules['max_duration']:
                    errors.append(f"Baris {row_idx}: Durasi terlalu panjang ({duration_hours:.2f} jam). Maksimum: {self.validation_rules['max_duration']} jam")
        
        # 4. Validasi spesialisasi (jika ada)
        if 'spesialisasi' in row:
            specialization = str(row['spesialisasi']).strip()
            if not specialization:
                errors.append(f"Baris {row_idx}: Spesialisasi tidak boleh kosong")
        
        return errors
    
    def _validate_consistency(self, df: pd.DataFrame) -> List[str]:
        """Validasi konsistensi data"""
        errors = []
        
        # 1. Cek duplikat jadwal
        duplicate_check_cols = ['nama_dokter', 'hari', 'jam_mulai', 'jam_selesai']
        available_cols = [col for col in duplicate_check_cols if col in df.columns]
        
        if len(available_cols) >= 3:
            duplicates = df.duplicated(subset=available_cols, keep=False)
            if duplicates.any():
                duplicate_count = duplicates.sum()
                errors.append(f"Terdapat {duplicate_count} jadwal duplikat")
        
        # 2. Cek konflik jadwal
        conflict_errors = self._check_schedule_conflicts(df)
        errors.extend(conflict_errors)
        
        # 3. Cek data outlier
        outlier_errors = self._check_outliers(df)
        errors.extend(outlier_errors)
        
        return errors
    
    def _check_schedule_conflicts(self, df: pd.DataFrame) -> List[str]:
        """Cek konflik jadwal untuk dokter yang sama di hari yang sama"""
        errors = []
        
        if 'nama_dokter' not in df.columns or 'hari' not in df.columns:
            return errors
        
        # Group by doctor and day
        for (doctor, day), group in df.groupby(['nama_dokter', 'hari']):
            if len(group) > 1:
                # Sort by start time
                schedules = []
                for _, row in group.iterrows():
                    start_time = parse_time(row.get('jam_mulai', ''))
                    end_time = parse_time(row.get('jam_selesai', ''))
                    
                    if start_time and end_time:
                        schedules.append({
                            'start': start_time,
                            'end': end_time,
                            'row': row
                        })
                
                # Sort by start time
                schedules.sort(key=lambda x: x['start'])
                
                # Check for overlaps
                for i in range(len(schedules) - 1):
                    current = schedules[i]
                    next_schedule = schedules[i + 1]
                    
                    if current['end'] > next_schedule['start']:
                        errors.append(
                            f"Konflik jadwal: Dr. {doctor} pada {day} "
                            f"({current['start'].strftime('%H:%M')}-{current['end'].strftime('%H:%M')}) "
                            f"overlap dengan ({next_schedule['start'].strftime('%H:%M')}-{next_schedule['end'].strftime('%H:%M')})"
                        )
        
        return errors
    
    def _check_outliers(self, df: pd.DataFrame) -> List[str]:
        """Cek data outlier"""
        errors = []
        
        # Cek waktu mulai yang terlalu awal atau terlalu malam
        if 'jam_mulai' in df.columns:
            early_count = 0
            late_count = 0
            
            for time_str in df['jam_mulai']:
                time_obj = parse_time(time_str)
                if time_obj:
                    if time_obj.hour < 5:  # Sebelum jam 5 pagi
                        early_count += 1
                    elif time_obj.hour >= 22:  # Setelah jam 10 malam
                        late_count += 1
            
            if early_count > 0:
                errors.append(f"Terdapat {early_count} jadwal dengan waktu mulai sebelum jam 5 pagi")
            
            if late_count > 0:
                errors.append(f"Terdapat {late_count} jadwal dengan waktu mulai setelah jam 10 malam")
        
        return errors
    
    def validate_time_format(self, time_str: str) -> bool:
        """Validasi format waktu"""
        if pd.isna(time_str):
            return False
        
        time_str = str(time_str).strip()
        
        # Coba parse dengan fungsi parse_time
        parsed = parse_time(time_str)
        return parsed is not None
    
    def get_validation_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Dapatkan summary validasi"""
        is_valid, errors = self.validate_dataframe(df)
        
        summary = {
            'is_valid': is_valid,
            'total_errors': len(errors),
            'errors': errors,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_required_columns': [],
            'data_quality_score': 0
        }
        
        # Hitung data quality score
        if len(df) > 0:
            # Base score
            score = 100
            
            # Deductions for errors
            score -= min(len(errors) * 5, 50)  # Max 50 points deduction for errors
            
            # Deductions for missing values
            if not df.empty:
                missing_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns))
                score -= missing_percentage * 30  # Max 30 points deduction for missing values
            
            summary['data_quality_score'] = max(0, min(100, round(score)))
        
        return summary
