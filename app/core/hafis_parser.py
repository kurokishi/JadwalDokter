"""
Parser untuk format jadwal_hafis.xlsx
"""
import pandas as pd
import numpy as np
from datetime import time
from typing import Dict, List, Tuple, Optional
import re


class HafisParser:
    """
    Parsing file Excel dengan format jadwal_hafis.xlsx
    """
    
    def __init__(self):
        self.workbook = None
        self.sheet_names = []
        self.days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        
    def load_workbook(self, file_path: str):
        """Load workbook dan semua sheet"""
        self.workbook = pd.ExcelFile(file_path)
        self.sheet_names = self.workbook.sheet_names
        return self.workbook
        
    def parse_schedule(self, file_path: str) -> List[Dict]:
        """
        Parse file jadwal_hafis.xlsx ke format structured data
        
        Returns:
            List of schedule items
        """
        try:
            df = pd.read_excel(file_path, sheet_name=0, header=None)
            
            schedules = []
            current_ksm = None
            current_doctor = None
            current_poli = None
            
            for idx, row in df.iterrows():
                # Skip baris kosong
                if pd.isna(row[0]) and pd.isna(row[1]) and pd.isna(row[2]):
                    continue
                    
                # Deteksi KSM (Department)
                if not pd.isna(row[0]) and pd.isna(row[1]) and pd.isna(row[2]):
                    current_ksm = str(row[0]).strip()
                    continue
                    
                # Deteksi Dokter
                if pd.isna(row[0]) and not pd.isna(row[1]) and pd.isna(row[2]):
                    current_doctor = str(row[1]).strip()
                    current_poli = str(row[2]).strip() if not pd.isna(row[2]) else current_ksm
                    continue
                    
                # Deteksi tipe jadwal (JAM KERJA, REGULER, EKSEKUTIF)
                if not pd.isna(row[2]) and row[2] in ['JAM KERJA', 'REGULER', 'EKSEKUTIF']:
                    schedule_type = str(row[2]).strip()
                    
                    for day_idx, day in enumerate(self.days):
                        if day_idx + 3 < len(row):  # +3 karena kolom A, B, C
                            time_str = str(row[day_idx + 3]) if not pd.isna(row[day_idx + 3]) else ""
                            
                            if time_str and time_str not in ['-', 'nan']:
                                # Parse waktu
                                parsed_time = self._parse_time_string(time_str)
                                
                                if parsed_time:
                                    schedule_item = {
                                        'KSM': current_ksm,
                                        'Dokter': current_doctor,
                                        'POLI': current_poli,
                                        'Jenis': 'Reguler' if schedule_type == 'REGULER' else 'Eksekutif',
                                        'Hari': day,
                                        'Jam Kerja': self._get_working_hours(df, idx-1, day_idx+3),
                                        'Waktu': parsed_time,
                                        'Raw': time_str
                                    }
                                    schedules.append(schedule_item)
            
            return schedules
            
        except Exception as e:
            raise Exception(f"Error parsing file: {str(e)}")
    
    def _parse_time_string(self, time_str: str) -> Optional[Dict]:
        """Parse string waktu ke format standardized"""
        time_str = str(time_str).strip()
        
        # Handle Excel formula references
        if time_str.startswith('='):
            # Formula seperti =[1]ANAK!T4
            return {
                'type': 'formula',
                'reference': time_str,
                'start': None,
                'end': None
            }
        
        # Handle time ranges: 07:30-14:00 atau 07.30-14.00
        time_str = time_str.replace('.', ':')
        
        # Pattern untuk time range
        pattern = r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})'
        match = re.search(pattern, time_str)
        
        if match:
            try:
                start_time = self._parse_time_to_minutes(match.group(1))
                end_time = self._parse_time_to_minutes(match.group(2))
                
                return {
                    'type': 'time_range',
                    'start': start_time,
                    'end': end_time,
                    'start_str': match.group(1),
                    'end_str': match.group(2)
                }
            except:
                pass
        
        # Single time: 08:00 atau 08.00
        pattern_single = r'(\d{1,2}:\d{2})'
        match_single = re.search(pattern_single, time_str)
        
        if match_single:
            try:
                time_minutes = self._parse_time_to_minutes(match_single.group(1))
                return {
                    'type': 'single_time',
                    'time': time_minutes,
                    'time_str': match_single.group(1)
                }
            except:
                pass
        
        return None
    
    def _parse_time_to_minutes(self, time_str: str) -> int:
        """Convert time string to minutes since midnight"""
        try:
            if ':' in time_str:
                hours, minutes = map(int, time_str.split(':'))
            elif '.' in time_str:
                hours, minutes = map(int, time_str.split('.'))
            else:
                hours = int(time_str)
                minutes = 0
                
            return hours * 60 + minutes
        except:
            return 0
    
    def _get_working_hours(self, df, doctor_idx, day_idx):
        """Get working hours for a doctor on specific day"""
        try:
            # Look for 'JAM KERJA' row for this doctor
            for i in range(max(0, doctor_idx-2), min(len(df), doctor_idx+3)):
                if df.iloc[i, 2] == 'JAM KERJA':
                    time_str = str(df.iloc[i, day_idx]) if not pd.isna(df.iloc[i, day_idx]) else ""
                    return time_str
        except:
            pass
        return ""
