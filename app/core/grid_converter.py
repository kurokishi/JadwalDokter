"""
Convert parsed data to grid format like jadwal_hasil.xlsx
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from app.config import AppConfig
from app.utils import parse_time_string, time_to_minutes, minutes_to_time, clean_dataframe


class GridConverter:
    """Convert to grid format"""
    
    def __init__(self):
        self.config = AppConfig()
        self.time_slots = self.config.DEFAULT_TIME_SLOTS
    
    def convert_to_grid(self, schedules: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert parsed schedules to grid format
        
        Args:
            schedules: List of parsed schedule items
            
        Returns:
            DataFrame in grid format
        """
        grid_rows = []
        
        # Group by key combinations
        grouped = self._group_schedules(schedules)
        
        for key, schedule_group in grouped.items():
            # Extract base information
            poli, dokter, hari, jenis = key
            
            # Clean and validate data
            poli = self._clean_string(poli)
            dokter = self._clean_string(dokter)
            hari = self._clean_string(hari)
            jenis = self._clean_string(jenis)
            
            # Skip if essential data is missing
            if not dokter or not hari:
                continue
            
            # Default to 'Reguler' if jenis is empty
            if not jenis:
                jenis = 'Reguler'
            
            # Get all time ranges for this combination
            time_ranges = self._extract_time_ranges(schedule_group, jenis)
            
            if time_ranges:
                # Create grid row
                try:
                    grid_row = self._create_grid_row(
                        poli, dokter, hari, jenis, time_ranges
                    )
                    grid_rows.append(grid_row)
                except Exception as e:
                    print(f"Warning: Could not create grid row for {dokter} on {hari}: {str(e)}")
                    continue
        
        # Create DataFrame
        if grid_rows:
            df = pd.DataFrame(grid_rows)
            
            # Clean the DataFrame
            df = self._clean_grid_dataframe(df)
            
            # Reorder columns
            base_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM']
            time_cols = [col for col in df.columns if col not in base_cols]
            
            # Sort columns
            df = df[base_cols + sorted(time_cols)]
            
            # Sort rows if we have data
            if not df.empty:
                try:
                    df = df.sort_values(['POLI', 'DOKTER', 'HARI', 'JENIS'])
                except Exception as e:
                    print(f"Warning: Could not sort DataFrame: {str(e)}")
            
            return df
        else:
            return pd.DataFrame()
    
    def _clean_string(self, value: Any) -> str:
        """Clean a string value"""
        if value is None or pd.isna(value):
            return ""
        
        value_str = str(value).strip()
        
        # Handle common issues
        value_str = value_str.replace('nan', '')
        value_str = value_str.replace('None', '')
        value_str = value_str.replace('null', '')
        
        return value_str
    
    def _group_schedules(self, schedules: List[Dict]) -> Dict:
        """Group schedules by key combination"""
        groups = {}
        
        for schedule in schedules:
            # Only process REGULER and EKSEKUTIF types
            schedule_type = self._clean_string(schedule.get('Tipe', ''))
            if schedule_type not in ['REGULER', 'EKSEKUTIF']:
                continue
            
            poli = self._clean_string(schedule.get('POLI', ''))
            dokter = self._clean_string(schedule.get('Dokter', ''))
            hari = self._clean_string(schedule.get('Hari', ''))
            
            # Map schedule type to JENIS
            if schedule_type == 'REGULER':
                jenis = 'Reguler'
            else:  # EKSEKUTIF
                jenis = 'Eksekutif'
            
            # Create a unique key
            key = (poli, dokter, hari, jenis)
            
            if key not in groups:
                groups[key] = []
            
            groups[key].append(schedule)
        
        return groups
    
    def _extract_time_ranges(self, schedules: List[Dict], jenis: str) -> List[Dict]:
        """Extract time ranges from schedules"""
        time_ranges = []
        
        for schedule in schedules:
            parsed = schedule.get('Parsed', {})
            
            if not parsed:
                continue
                
            parsed_type = parsed.get('type', '')
            
            if parsed_type == 'range':
                start = self._clean_string(parsed.get('start', ''))
                end = self._clean_string(parsed.get('end', ''))
                
                if start and end:
                    time_range = {
                        'start': start,
                        'end': end,
                        'jenis': jenis
                    }
                    time_ranges.append(time_range)
                    
            elif parsed_type == 'single':
                # Convert single time to 30-minute range
                single_time = self._clean_string(parsed.get('time', ''))
                
                if single_time:
                    time_range = {
                        'start': single_time,
                        'end': self._add_minutes(single_time, 30),
                        'jenis': jenis
                    }
                    time_ranges.append(time_range)
        
        return time_ranges
    
    def _add_minutes(self, time_str: str, minutes: int) -> str:
        """Add minutes to time string"""
        try:
            if not time_str:
                return ""
                
            hour, minute = map(int, time_str.split(':'))
            
            total_minutes = hour * 60 + minute + minutes
            
            new_hour = total_minutes // 60
            new_minute = total_minutes % 60
            
            return f"{new_hour:02d}:{new_minute:02d}"
        except:
            return ""
    
    def _create_grid_row(self, poli: str, dokter: str, hari: str, 
                        jenis: str, time_ranges: List[Dict]) -> Dict:
        """Create a single grid row"""
        # Start with base columns
        row = {
            'POLI': poli,
            'JENIS': jenis,
            'HARI': hari,
            'DOKTER': dokter
        }
        
        # Combine time ranges for JAM column
        jam_strings = []
        for tr in time_ranges:
            start = self._clean_string(tr.get('start', ''))
            end = self._clean_string(tr.get('end', ''))
            
            if start and end:
                jam_strings.append(f"{start}-{end}")
        
        row['JAM'] = ', '.join(jam_strings) if jam_strings else ''
        
        # Initialize all time slots as empty
        for slot in self.time_slots:
            row[slot] = ''
        
        # Fill time slots based on time ranges
        for time_range in time_ranges:
            start_str = self._clean_string(time_range.get('start', ''))
            end_str = self._clean_string(time_range.get('end', ''))
            
            if not start_str or not end_str:
                continue
                
            start_min = time_to_minutes(start_str)
            end_min = time_to_minutes(end_str)
            
            if start_min == 0 or end_min == 0:
                continue
                
            for slot in self.time_slots:
                slot_min = time_to_minutes(slot)
                
                if start_min <= slot_min < end_min:
                    # Use R for Reguler, E for Eksekutif
                    row[slot] = 'R' if jenis == 'Reguler' else 'E'
        
        return row
    
    def _clean_grid_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean grid DataFrame"""
        if df.empty:
            return df
        
        # Use the utility function
        df_clean = clean_dataframe(df)
        
        # Additional cleaning specific to grid format
        # Ensure time slot columns exist
        for slot in self.time_slots:
            if slot not in df_clean.columns:
                df_clean[slot] = ''
        
        # Validate time slot values
        valid_slot_values = ['', 'R', 'E']
        for slot in self.time_slots:
            if slot in df_clean.columns:
                # Replace invalid values with empty string
                df_clean[slot] = df_clean[slot].apply(
                    lambda x: x if x in valid_slot_values else ''
                )
        
        # Remove rows with no time slots filled
        time_cols = [col for col in self.time_slots if col in df_clean.columns]
        if time_cols:
            # Check if any time slot has R or E
            has_schedule = df_clean[time_cols].apply(
                lambda row: any(val in ['R', 'E'] for val in row), axis=1
            )
            df_clean = df_clean[has_schedule]
        
        return df_clean
    
    def get_grid_summary(self, grid_df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for grid data"""
        if grid_df is None or grid_df.empty:
            return {
                'total_rows': 0,
                'total_doctors': 0,
                'total_poli': 0,
                'reguler_count': 0,
                'eksekutif_count': 0,
                'days_distribution': {}
            }
        
        # Clean the DataFrame first
        df_clean = clean_dataframe(grid_df)
        
        return {
            'total_rows': len(df_clean),
            'total_doctors': df_clean['DOKTER'].nunique() if 'DOKTER' in df_clean.columns else 0,
            'total_poli': df_clean['POLI'].nunique() if 'POLI' in df_clean.columns else 0,
            'reguler_count': len(df_clean[df_clean['JENIS'] == 'Reguler']) if 'JENIS' in df_clean.columns else 0,
            'eksekutif_count': len(df_clean[df_clean['JENIS'] == 'Eksekutif']) if 'JENIS' in df_clean.columns else 0,
            'days_distribution': df_clean['HARI'].value_counts().to_dict() if 'HARI' in df_clean.columns else {}
        }
