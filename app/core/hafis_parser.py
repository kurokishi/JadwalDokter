"""
Parser for jadwal_hafis.xlsx format
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Any
import io


class HafisParser:
    """Parser untuk format jadwal_hafis.xlsx"""
    
    def __init__(self):
        self.days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        self.schedule_types = ['JAM KERJA', 'REGULER', 'EKSEKUTIF']
        
    def parse_file(self, file_content) -> List[Dict[str, Any]]:
        """
        Parse uploaded Excel file
        
        Args:
            file_content: Uploaded file content
            
        Returns:
            List of parsed schedule items
        """
        try:
            # Read the Excel file
            xls = pd.ExcelFile(file_content)
            
            # Read the first sheet (assuming main data is in first sheet)
            df = pd.read_excel(xls, sheet_name=0, header=None)
            
            schedules = []
            current_ksm = None
            current_doctor = None
            current_poli = None
            
            for idx in range(len(df)):
                row = df.iloc[idx]
                
                # Check for empty row
                if self._is_empty_row(row):
                    continue
                
                # Detect KSM (Department)
                ksm = self._extract_ksm(row)
                if ksm:
                    current_ksm = ksm
                    continue
                
                # Detect Doctor
                doctor_info = self._extract_doctor_info(row)
                if doctor_info:
                    current_doctor, current_poli = doctor_info
                    continue
                
                # Detect Schedule Type
                schedule_type = self._extract_schedule_type(row)
                if schedule_type:
                    # Parse schedule for each day
                    day_schedules = self._parse_day_schedules(
                        row, current_ksm, current_doctor, current_poli, schedule_type
                    )
                    schedules.extend(day_schedules)
            
            return schedules
            
        except Exception as e:
            raise Exception(f"Error parsing file: {str(e)}")
    
    def _is_empty_row(self, row) -> bool:
        """Check if row is empty"""
        return row.isna().all() or (row[0] is None and row[1] is None and row[2] is None)
    
    def _extract_ksm(self, row) -> Optional[str]:
        """Extract KSM from row"""
        if pd.notna(row[0]) and pd.isna(row[1]) and pd.isna(row[2]):
            return str(row[0]).strip()
        return None
    
    def _extract_doctor_info(self, row) -> Optional[tuple]:
        """Extract doctor and poli information"""
        if pd.isna(row[0]) and pd.notna(row[1]):
            doctor = str(row[1]).strip()
            poli = str(row[2]).strip() if pd.notna(row[2]) else None
            return (doctor, poli)
        return None
    
    def _extract_schedule_type(self, row) -> Optional[str]:
        """Extract schedule type (JAM KERJA, REGULER, EKSEKUTIF)"""
        if pd.notna(row[2]) and str(row[2]).strip() in self.schedule_types:
            return str(row[2]).strip()
        return None
    
    def _parse_day_schedules(self, row, ksm, doctor, poli, schedule_type) -> List[Dict]:
        """Parse schedules for each day in a row"""
        schedules = []
        
        for day_idx, day in enumerate(self.days):
            col_idx = day_idx + 3  # Columns start at D (index 3)
            
            if col_idx < len(row):
                time_value = row[col_idx]
                
                if pd.notna(time_value):
                    time_str = str(time_value)
                    
                    # Skip if it's just a dash or empty
                    if time_str.strip() in ['-', 'nan', '']:
                        continue
                    
                    # Parse the time value
                    parsed_time = self._parse_time_value(time_str)
                    
                    if parsed_time:
                        schedule_item = {
                            'KSM': ksm,
                            'Dokter': doctor,
                            'POLI': poli or ksm,
                            'Tipe': schedule_type,
                            'Hari': day,
                            'Waktu': time_str,
                            'Parsed': parsed_time
                        }
                        schedules.append(schedule_item)
        
        return schedules
    
    def _parse_time_value(self, time_str: str) -> Dict[str, Any]:
        """Parse time string to structured format"""
        time_str = str(time_str).strip()
        
        # Handle Excel formulas
        if time_str.startswith('='):
            return {
                'type': 'formula',
                'reference': time_str,
                'original': time_str
            }
        
        # Clean the string
        time_str = time_str.replace('.', ':')
        
        # Try to parse as time range
        time_range = self._parse_time_range(time_str)
        if time_range:
            return time_range
        
        # Try to parse as single time
        single_time = self._parse_single_time(time_str)
        if single_time:
            return single_time
        
        # Return as raw string
        return {
            'type': 'raw',
            'value': time_str,
            'original': time_str
        }
    
    def _parse_time_range(self, time_str: str) -> Optional[Dict]:
        """Parse time range like '07:30-14:00'"""
        pattern = r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})'
        match = re.search(pattern, time_str)
        
        if match:
            start = match.group(1)
            end = match.group(2)
            
            # Validate times
            if self._is_valid_time_format(start) and self._is_valid_time_format(end):
                return {
                    'type': 'range',
                    'start': start,
                    'end': end,
                    'original': time_str
                }
        
        return None
    
    def _parse_single_time(self, time_str: str) -> Optional[Dict]:
        """Parse single time like '08:00'"""
        pattern = r'(\d{1,2}:\d{2})'
        match = re.search(pattern, time_str)
        
        if match:
            time_val = match.group(1)
            if self._is_valid_time_format(time_val):
                return {
                    'type': 'single',
                    'time': time_val,
                    'original': time_str
                }
        
        return None
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Check if time string is in valid format"""
        pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$'
        return bool(re.match(pattern, time_str))
    
    def get_summary_stats(self, schedules: List[Dict]) -> Dict[str, Any]:
        """Get summary statistics from parsed schedules"""
        if not schedules:
            return {}
        
        df = pd.DataFrame(schedules)
        
        return {
            'total_schedules': len(schedules),
            'total_doctors': df['Dokter'].nunique(),
            'total_poli': df['POLI'].nunique(),
            'schedule_types': df['Tipe'].value_counts().to_dict(),
            'days_coverage': df['Hari'].value_counts().to_dict()
        }
