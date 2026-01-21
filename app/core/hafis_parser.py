"""
Parser for jadwal_hafis.xlsx format
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Any, Tuple
import io
from app.utils import clean_dataframe, log_error


class HafisParser:
    """Parser untuk format jadwal_hafis.xlsx"""
    
    def __init__(self):
        self.days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        self.schedule_types = ['JAM KERJA', 'REGULER', 'EKSEKUTIF']
        self.parse_errors = []
        
    def parse_file(self, file_content) -> List[Dict[str, Any]]:
        """
        Parse uploaded Excel file
        
        Args:
            file_content: Uploaded file content
            
        Returns:
            List of parsed schedule items
        """
        self.parse_errors = []
        schedules = []
        
        try:
            # Read the Excel file
            xls = pd.ExcelFile(file_content)
            
            # Read the first sheet (assuming main data is in first sheet)
            df = pd.read_excel(xls, sheet_name=0, header=None)
            
            # Clean the DataFrame
            df = clean_dataframe(df, fill_empty='')
            
            current_ksm = ""
            current_doctor = ""
            current_poli = ""
            
            for idx in range(len(df)):
                try:
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
                        
                except Exception as e:
                    error_msg = f"Error parsing row {idx}: {str(e)}"
                    self.parse_errors.append(error_msg)
                    log_error(e, f"parse_file row {idx}")
                    continue
            
            # Log parsing results
            if self.parse_errors:
                print(f"⚠️ Parser found {len(self.parse_errors)} errors during parsing")
            
            return schedules
            
        except Exception as e:
            error_msg = f"Error parsing file: {str(e)}"
            self.parse_errors.append(error_msg)
            log_error(e, "parse_file")
            raise Exception(f"Error parsing file: {str(e)}")
    
    def _is_empty_row(self, row) -> bool:
        """Check if row is empty"""
        if row is None or len(row) == 0:
            return True
        
        # Check if all values are empty strings or NaN
        for val in row:
            if pd.notna(val) and str(val).strip() != '':
                return False
        return True
    
    def _extract_ksm(self, row) -> Optional[str]:
        """Extract KSM from row"""
        try:
            if len(row) > 0 and pd.notna(row[0]) and str(row[0]).strip():
                ksm = str(row[0]).strip()
                # Check if this is actually a KSM (not a schedule type)
                if ksm not in self.schedule_types:
                    return ksm
        except:
            pass
        return None
    
    def _extract_doctor_info(self, row) -> Optional[Tuple[str, str]]:
        """Extract doctor and poli information"""
        try:
            # Doctor should be in column B (index 1), poli in column C (index 2)
            if len(row) > 1 and pd.notna(row[1]) and str(row[1]).strip():
                doctor = str(row[1]).strip()
                poli = ""
                
                if len(row) > 2 and pd.notna(row[2]) and str(row[2]).strip():
                    poli = str(row[2]).strip()
                
                # Don't return if doctor name looks like a schedule type
                if doctor in self.schedule_types:
                    return None
                
                return (doctor, poli)
        except:
            pass
        return None
    
    def _extract_schedule_type(self, row) -> Optional[str]:
        """Extract schedule type (JAM KERJA, REGULER, EKSEKUTIF)"""
        try:
            if len(row) > 2 and pd.notna(row[2]) and str(row[2]).strip() in self.schedule_types:
                return str(row[2]).strip()
        except:
            pass
        return None
    
    def _parse_day_schedules(self, row, ksm: str, doctor: str, poli: str, schedule_type: str) -> List[Dict]:
        """Parse schedules for each day in a row"""
        schedules = []
        
        for day_idx, day in enumerate(self.days):
            col_idx = day_idx + 3  # Columns start at D (index 3)
            
            if col_idx < len(row):
                time_value = row[col_idx]
                
                if pd.notna(time_value) and str(time_value).strip():
                    time_str = str(time_value)
                    
                    # Skip if it's just a dash or empty
                    if time_str.strip() in ['-', 'nan', '', 'None']:
                        continue
                    
                    try:
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
                    except Exception as e:
                        error_msg = f"Error parsing time '{time_str}' for {doctor} on {day}: {str(e)}"
                        self.parse_errors.append(error_msg)
                        log_error(e, f"parse_time_value: {time_str}")
        
        return schedules
    
    def _parse_time_value(self, time_str: str) -> Dict[str, Any]:
        """Parse time string to structured format"""
        try:
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
        except Exception as e:
            log_error(e, f"_parse_time_value: {time_str}")
            return {
                'type': 'error',
                'error': str(e),
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
        try:
            pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$'
            return bool(re.match(pattern, time_str))
        except:
            return False
    
    def get_parse_errors(self) -> List[str]:
        """Get parsing errors"""
        return self.parse_errors.copy()
    
    def get_summary_stats(self, schedules: List[Dict]) -> Dict[str, Any]:
        """Get summary statistics from parsed schedules"""
        if not schedules:
            return {
                'total_schedules': 0,
                'total_doctors': 0,
                'total_poli': 0,
                'schedule_types': {},
                'days_coverage': {},
                'parse_errors': len(self.parse_errors)
            }
        
        try:
            df = pd.DataFrame(schedules)
            df_clean = clean_dataframe(df)
            
            return {
                'total_schedules': len(schedules),
                'total_doctors': df_clean['Dokter'].nunique() if 'Dokter' in df_clean.columns else 0,
                'total_poli': df_clean['POLI'].nunique() if 'POLI' in df_clean.columns else 0,
                'schedule_types': df_clean['Tipe'].value_counts().to_dict() if 'Tipe' in df_clean.columns else {},
                'days_coverage': df_clean['Hari'].value_counts().to_dict() if 'Hari' in df_clean.columns else {},
                'parse_errors': len(self.parse_errors)
            }
        except Exception as e:
            log_error(e, "get_summary_stats")
            return {
                'total_schedules': len(schedules),
                'total_doctors': 0,
                'total_poli': 0,
                'schedule_types': {},
                'days_coverage': {},
                'parse_errors': len(self.parse_errors)
            }
