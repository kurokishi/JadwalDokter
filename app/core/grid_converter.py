"""
Konversi data parsed ke format grid seperti jadwal_hasil.xlsx
"""
import pandas as pd
from datetime import time
from typing import Dict, List
from .hafis_parser import HafisParser


class GridConverter:
    """
    Konversi data dari HafisParser ke format grid
    """
    
    def __init__(self):
        self.time_slots = self._generate_time_slots()
        
    def _generate_time_slots(self):
        """Generate time slots dari 07:00 sampai 14:00 dengan interval 30 menit"""
        slots = []
        for hour in range(7, 15):  # 07:00 sampai 14:00
            for minute in [0, 30]:
                if hour == 14 and minute == 30:  # Stop at 14:30
                    break
                time_str = f"{hour:02d}:{minute:02d}"
                slots.append(time_str)
        return slots
    
    def convert_to_grid(self, schedules: List[Dict]) -> pd.DataFrame:
        """
        Convert parsed schedules to grid format
        
        Returns:
            DataFrame dengan format seperti jadwal_hasil.xlsx
        """
        rows = []
        
        for schedule in schedules:
            if schedule['Waktu']['type'] != 'time_range':
                continue
                
            # Create base row
            row = {
                'POLI': schedule['POLI'],
                'JENIS': schedule['Jenis'],
                'HARI': schedule['Hari'],
                'DOKTER': schedule['DOKTER'],
                'JAM': f"{schedule['Waktu']['start_str']}-{schedule['Waktu']['end_str']}",
            }
            
            # Add time slots
            start_min = schedule['Waktu']['start']
            end_min = schedule['Waktu']['end']
            
            for slot in self.time_slots:
                slot_hour, slot_minute = map(int, slot.split(':'))
                slot_minutes = slot_hour * 60 + slot_minute
                
                # Check if slot is within the time range
                if start_min <= slot_minutes < end_min:
                    row[slot] = 'R' if schedule['Jenis'] == 'Reguler' else 'E'
                else:
                    row[slot] = ''
            
            rows.append(row)
        
        # Create DataFrame
        columns = ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM'] + self.time_slots
        df = pd.DataFrame(rows, columns=columns)
        
        # Sort the DataFrame
        df = df.sort_values(['POLI', 'DOKTER', 'HARI', 'JENIS'])
        
        return df
    
    def fill_time_slots_from_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill time slots based on JAM column
        """
        for idx, row in df.iterrows():
            if pd.isna(row['JAM']) or row['JAM'] == '':
                continue
                
            # Parse time range from JAM column
            try:
                time_range = str(row['JAM'])
                if '-' in time_range:
                    start_str, end_str = time_range.split('-')
                    
                    # Convert to minutes
                    start_hour, start_minute = map(int, start_str.strip().split(':'))
                    end_hour, end_minute = map(int, end_str.strip().split(':'))
                    
                    start_minutes = start_hour * 60 + start_minute
                    end_minutes = end_hour * 60 + end_minute
                    
                    # Fill slots
                    for slot in self.time_slots:
                        slot_hour, slot_minute = map(int, slot.split(':'))
                        slot_minutes = slot_hour * 60 + slot_minute
                        
                        if start_minutes <= slot_minutes < end_minutes:
                            df.at[idx, slot] = 'R' if row['JENIS'] == 'Reguler' else 'E'
            except:
                continue
        
        return df
