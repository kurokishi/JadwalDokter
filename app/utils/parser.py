"""
Parser khusus untuk file Excel jadwal dokter format RS
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional
import streamlit as st

class JadwalHafisParser:
    """Parser khusus untuk format file jadwal_hafis.xlsx"""
    
    def __init__(self):
        self.days_mapping = {
            'SENIN': 'Monday',
            'SELASA': 'Tuesday', 
            'RABU': 'Wednesday',
            'KAMIS': 'Thursday',
            'JUMAT': 'Friday',
            'SABTU': 'Saturday'
        }
        
    def parse_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse file Excel dengan format khusus jadwal hafis
        """
        try:
            # Baca file Excel
            df_raw = pd.read_excel(
                file_path, 
                header=None,  # Tidak ada header standar
                dtype=str
            )
            
            # Clean data
            df_clean = self._clean_data(df_raw)
            
            # Parse ke format standar
            df_standard = self._convert_to_standard_format(df_clean)
            
            return df_standard
            
        except Exception as e:
            st.error(f"Error parsing file: {str(e)}")
            raise
    
    def _clean_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Bersihkan data mentah dari Excel"""
        # Ambil header yang benar (baris 3)
        df = df_raw.copy()
        
        # Set header dari baris 2 (index 1, 0-based)
        if df.shape[0] > 1:
            # Gunakan baris ke-2 sebagai header
            header_row = df.iloc[1].tolist()
            df = df[2:]  # Ambil data setelah header
            df.columns = header_row
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Bersihkan nama kolom
        df.columns = [str(col).strip() if pd.notna(col) else f"col_{i}" 
                     for i, col in enumerate(df.columns)]
        
        # Fill forward untuk KSM dan Nama dokter
        df['KSM'] = df['KSM'].ffill()
        df['Nama dokter spesialis/ sub spesialis'] = df['Nama dokter spesialis/ sub spesialis'].ffill()
        
        return df
    
    def _convert_to_standard_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Konversi ke format standar aplikasi"""
        records = []
        
        # Group by KSM dan Nama dokter
        current_doctor = None
        current_ksm = None
        jam_kerja_data = {}
        reguler_data = {}
        eksekutif_data = {}
        
        for idx, row in df.iterrows():
            ksm = row['KSM']
            nama = row['Nama dokter spesialis/ sub spesialis']
            poli = row['POLI']
            
            # Skip jika semua kosong
            if pd.isna(ksm) and pd.isna(nama):
                continue
                
            # Update current doctor jika ada nama baru
            if pd.notna(nama) and nama != current_doctor:
                # Simpan dokter sebelumnya jika ada
                if current_doctor:
                    records.extend(
                        self._create_doctor_records(
                            current_ksm, current_doctor,
                            jam_kerja_data, reguler_data, eksekutif_data
                        )
                    )
                
                # Reset untuk dokter baru
                current_doctor = nama
                current_ksm = ksm
                jam_kerja_data = {}
                reguler_data = {}
                eksekutif_data = {}
            
            # Kumpulkan data berdasarkan tipe poli
            for day_id, day_indonesia in enumerate(self.days_mapping.keys(), 1):
                day_col = day_indonesia
                if day_col in row:
                    value = row[day_col]
                    
                    if pd.notna(value) and str(value).strip() not in ['', '-', 'nan']:
                        # Clean value
                        clean_value = self._clean_time_value(str(value))
                        
                        if poli == 'JAM KERJA':
                            jam_kerja_data[day_indonesia] = clean_value
                        elif poli == 'REGULER':
                            reguler_data[day_indonesia] = clean_value
                        elif poli == 'EKSEKUTIF':
                            eksekutif_data[day_indonesia] = clean_value
        
        # Tambahkan dokter terakhir
        if current_doctor:
            records.extend(
                self._create_doctor_records(
                    current_ksm, current_doctor,
                    jam_kerja_data, reguler_data, eksekutif_data
                )
            )
        
        # Buat DataFrame
        result_df = pd.DataFrame(records)
        
        # Add metadata
        result_df['source_file'] = 'jadwal_hafis.xlsx'
        result_df['parsed_date'] = pd.Timestamp.now()
        
        return result_df
    
    def _clean_time_value(self, value: str) -> str:
        """Bersihkan dan standarisasi format waktu"""
        if pd.isna(value):
            return ""
        
        value = str(value).strip()
        
        # Handle Excel references
        if value.startswith('='):
            return "[Reference]"
        
        # Convert 07.30-08.25 to 07:30-08:25
        value = re.sub(r'(\d{1,2})\.(\d{2})', r'\1:\2', value)
        
        # Remove extra spaces
        value = re.sub(r'\s+', '', value)
        
        return value
    
    def _create_doctor_records(self, ksm: str, doctor_name: str,
                              jam_kerja: Dict, reguler: Dict, eksekutif: Dict) -> List[Dict]:
        """Buat record untuk setiap dokter"""
        records = []
        
        # Specialties mapping
        specialty_map = {
            'Anak': 'Pediatrics',
            'Bedah': 'Surgery',
            'Penyakit Dalam': 'Internal Medicine',
            'OBGYN': 'Obstetrics & Gynecology',
            'JANTUNG': 'Cardiology',
            'ORTHOPEDI': 'Orthopedics',
            'PARU': 'Pulmonology',
            'SYARAF': 'Neurology',
            'THT': 'ENT',
            'UROLOGI': 'Urology',
            'JIWA': 'Psychiatry',
            'KULIT KELAMIN': 'Dermatology',
            'BEDAH SYARAF': 'Neurosurgery',
            'GIGI': 'Dentistry',
            'PATOLOGI ANATOMI': 'Anatomical Pathology',
            'MATA': 'Ophthalmology',
            'PATOLOGI KLINIK': 'Clinical Pathology',
            'MIKROBIOLOGI': 'Microbiology',
            'ANASTHESI': 'Anesthesiology',
            'RADIOLOGI': 'Radiology',
            'REHAB MEDIK': 'Rehabilitation Medicine'
        }
        
        specialty = specialty_map.get(ksm, ksm)
        
        # Create records for each day
        for day_indonesia, day_english in self.days_mapping.items():
            record = {
                'doctor_name': doctor_name,
                'specialty': specialty,
                'department': ksm,
                'day': day_english,
                'working_hours': jam_kerja.get(day_indonesia, ''),
                'regular_schedule': reguler.get(day_indonesia, ''),
                'executive_schedule': eksekutif.get(day_indonesia, ''),
                'available': 1 if (jam_kerja.get(day_indonesia) or 
                                 reguler.get(day_indonesia) or 
                                 eksekutif.get(day_indonesia)) else 0
            }
            
            # Parse waktu untuk start_time dan end_time
            if record['working_hours']:
                times = self._parse_time_range(record['working_hours'])
                if times:
                    record['start_time'], record['end_time'] = times
            
            records.append(record)
        
        return records
    
    def _parse_time_range(self, time_str: str) -> Optional[tuple]:
        """Parse string waktu ke format datetime"""
        if not time_str or time_str == '[Reference]':
            return None
        
        try:
            # Clean string
            time_str = time_str.replace(' ', '')
            
            # Handle multiple formats
            if '-' in time_str:
                start_str, end_str = time_str.split('-')
                
                # Parse start time
                start_time = self._parse_single_time(start_str)
                
                # Parse end time  
                end_time = self._parse_single_time(end_str)
                
                return (start_time, end_time)
            
        except:
            pass
        
        return None
    
    def _parse_single_time(self, time_str: str) -> str:
        """Parse single time string to HH:MM format"""
        if not time_str:
            return ""
        
        # Remove non-numeric
        time_str = re.sub(r'[^\d:]', '', time_str)
        
        # Ensure format
        if ':' in time_str:
            parts = time_str.split(':')
        else:
            # Assume HHMM format
            if len(time_str) == 4:
                time_str = f"{time_str[:2]}:{time_str[2:]}"
            parts = time_str.split(':') if ':' in time_str else ['00', '00']
        
        # Pad to HH:MM
        if len(parts) >= 2:
            hours = parts[0].zfill(2)
            minutes = parts[1].zfill(2) if len(parts[1]) > 0 else '00'
            return f"{hours}:{minutes}"
        
        return "00:00"
