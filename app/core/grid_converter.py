"""
Convert parsed data to grid format like jadwal_hasil.xlsx
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from app.config import AppConfig
from app.utils import parse_time_string, time_to_minutes, minutes_to_time


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
            
            # Get all time ranges for this combination
            time_ranges = self._extract_time_ranges(schedule_group, jenis)
            
            if time_ranges:
                # Create grid row
                grid_row = self._create_grid_row(
                    poli, dokter, hari, jenis, time_ranges
                )
                grid_rows.append(grid_row)
        
        # Create DataFrame
        if grid_rows:
            df = pd.DataFrame(grid_rows)
            
            # Reorder columns
            base_cols = ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM']
            time_cols = [col for col in df.columns if col not in base_cols]
            
            # Sort columns
            df = df[base_cols + sorted(time_cols)]
            
            # Sort rows
            df = df.sort_values(['POLI', 'DOKTER', 'HARI', 'JENIS'])
            
            return df
        else:
            return pd.DataFrame()
    
    def _group_schedules(self, schedules: List[Dict]) -> Dict:
        """Group schedules by key combination"""
        groups = {}
        
        for schedule in schedules:
            # Only process REGULER and EKSEKUTIF types
            if schedule['Tipe'] not in ['REGULER', 'EKSEKUTIF']:
                continue
            
            poli = schedule.get('POLI', '')
            dokter = schedule.get('Dokter', '')
            hari = schedule.get('Hari', '')
            
            # Map schedule type to JENIS
            if schedule['Tipe'] == 'REGULER':
                jenis = 'Reguler'
            else:  # EKSEKUTIF
                jenis = 'Eksekutif'
            
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
            
            if parsed.get('type') == 'range':
                time_range = {
                    'start': parsed['start'],
                    'end': parsed['end'],
                    'jenis': jenis
                }
                time_ranges.append(time_range)
            elif parsed.get('type') == 'single':
                # Convert single time to 30-minute range
                single_time = parsed['time']
                time_range = {
                    'start': single_time,
                    'end': self._add_minutes(single_time, 30),
                    'jenis': jenis
                }
                time_ranges.append(time_range)
        
        return time_ranges
    
    def _add_minutes(self, time_str: str, minutes: int) -> str:
        """Add minutes to time string"""
        hour, minute = map(int, time_str.split(':'))
        
        total_minutes = hour * 60 + minute + minutes
        
        new_hour = total_minutes // 60
        new_minute = total_minutes % 60
        
        return f"{new_hour:02d}:{new_minute:02d}"
    
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
            jam_strings.append(f"{tr['start']}-{tr['end']}")
        
        row['JAM'] = ', '.join(jam_strings)
        
        # Initialize all time slots as empty
        for slot in self.time_slots:
            row[slot] = ''
        
        # Fill time slots based on time ranges
        for time_range in time_ranges:
            start_min = time_to_minutes(time_range['start'])
            end_min = time_to_minutes(time_range['end'])
            
            for slot in self.time_slots:
                slot_min = time_to_minutes(slot)
                
                if start_min <= slot_min < end_min:
                    # Use R for Reguler, E for Eksekutif
                    row[slot] = 'R' if jenis == 'Reguler' else 'E'
        
        return row
    
    def get_grid_summary(self, grid_df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for grid data"""
        if grid_df.empty:
            return {}
        
        return {
            'total_rows': len(grid_df),
            'total_doctors': grid_df['DOKTER'].nunique(),
            'total_poli': grid_df['POLI'].nunique(),
            'reguler_count': len(grid_df[grid_df['JENIS'] == 'Reguler']),
            'eksekutif_count': len(grid_df[grid_df['JENIS'] == 'Eksekutif']),
            'days_distribution': grid_df['HARI'].value_counts().to_dict()
        }
