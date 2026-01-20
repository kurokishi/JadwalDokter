"""
Data validation utilities
"""
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any

class DataValidator:
    """Data validation utility class"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, expected_columns: List[str] = None) -> Tuple[bool, List[str]]:
        """Validate DataFrame structure and content"""
        errors = []
        
        if df.empty:
            errors.append("DataFrame is empty")
            return False, errors
        
        # Check for required columns
        if expected_columns:
            for col in expected_columns:
                if col not in df.columns:
                    errors.append(f"Missing required column: {col}")
        
        # Check for null values in critical columns
        critical_columns = ['doctor_name', 'specialty', 'day']
        for col in critical_columns:
            if col in df.columns:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    errors.append(f"Column '{col}' has {null_count} null values")
        
        # Check for duplicate doctor-day combinations
        if all(col in df.columns for col in ['doctor_name', 'day']):
            duplicates = df.duplicated(subset=['doctor_name', 'day'], keep=False)
            if duplicates.any():
                dup_count = duplicates.sum()
                errors.append(f"Found {dup_count} duplicate doctor-day combinations")
        
        # Validate time formats
        time_columns = ['working_hours', 'regular_schedule', 'executive_schedule', 'start_time', 'end_time']
        for col in time_columns:
            if col in df.columns:
                invalid_times = DataValidator._count_invalid_times(df[col])
                if invalid_times > 0:
                    errors.append(f"Column '{col}' has {invalid_times} invalid time formats")
        
        if errors:
            return False, errors
        
        return True, []
    
    @staticmethod
    def _count_invalid_times(series: pd.Series) -> int:
        """Count invalid time formats in a series"""
        if series.empty:
            return 0
        
        invalid_count = 0
        
        for value in series:
            if pd.isna(value):
                continue
            
            str_value = str(value).strip()
            
            # Skip empty strings and references
            if str_value in ['', '-', '[Reference]']:
                continue
            
            # Check for valid time format
            if not DataValidator._is_valid_time_format(str_value):
                invalid_count += 1
        
        return invalid_count
    
    @staticmethod
    def _is_valid_time_format(time_str: str) -> bool:
        """Check if string is valid time format"""
        import re
        
        # Empty is valid
        if not time_str or time_str.strip() == '':
            return True
        
        # Time range format
        if '-' in time_str:
            parts = time_str.split('-')
            if len(parts) != 2:
                return False
            
            # Check both parts
            for part in parts:
                if not DataValidator._is_valid_single_time(part.strip()):
                    return False
            return True
        
        # Single time format
        return DataValidator._is_valid_single_time(time_str)
    
    @staticmethod
    def _is_valid_single_time(time_str: str) -> bool:
        """Check if string is valid single time format"""
        import re
        
        patterns = [
            r'^\d{1,2}:\d{2}$',  # HH:MM
            r'^\d{1,2}\.\d{2}$',  # HH.MM
            r'^\d{3,4}$',  # HHMM or HMM
        ]
        
        for pattern in patterns:
            if re.match(pattern, time_str):
                return True
        
        return False
    
    @staticmethod
    def validate_doctor_schedule(df: pd.DataFrame, doctor_name: str) -> Dict[str, Any]:
        """Validate schedule for a specific doctor"""
        validation_result = {
            'doctor_name': doctor_name,
            'has_schedule': False,
            'days_available': 0,
            'total_hours': 0,
            'conflicts': [],
            'warnings': []
        }
        
        if 'doctor_name' not in df.columns:
            validation_result['warnings'].append("No doctor_name column in data")
            return validation_result
        
        doctor_data = df[df['doctor_name'] == doctor_name].copy()
        
        if doctor_data.empty:
            validation_result['warnings'].append(f"No schedule found for doctor: {doctor_name}")
            return validation_result
        
        validation_result['has_schedule'] = True
        validation_result['days_available'] = len(doctor_data)
        
        # Calculate total hours
        if 'working_hours' in doctor_data.columns:
            total_hours = 0
            for hours in doctor_data['working_hours']:
                if pd.notna(hours) and hours != '':
                    # Simple calculation - assuming 8 hours per day if time range present
                    if '-' in str(hours):
                        total_hours += 8
            
            validation_result['total_hours'] = total_hours
        
        # Check for schedule conflicts (same doctor, overlapping times on same day)
        if all(col in doctor_data.columns for col in ['day', 'working_hours']):
            days_with_schedule = doctor_data['day'].unique()
            
            for day in days_with_schedule:
                day_schedule = doctor_data[doctor_data['day'] == day]
                if len(day_schedule) > 1:
                    validation_result['conflicts'].append(
                        f"Multiple entries for {doctor_name} on {day}"
                    )
        
        return validation_result
