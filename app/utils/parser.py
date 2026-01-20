"""
Parser khusus untuk file Excel jadwal dokter format RS
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional, Tuple
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
        
        # Mapping KSM to specialties
        self.specialty_map = {
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
    
    def parse_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse file Excel dengan format khusus jadwal hafis
        """
        try:
            st.info("🔍 Parsing file jadwal_hafis.xlsx format...")
            
            # Baca file Excel
            df_raw = pd.read_excel(
                file_path, 
                header=None,  # Tidak ada header standar
                dtype=str,
                engine='openpyxl'
            )
            
            # Clean data
            df_clean = self._clean_data(df_raw)
            
            # Parse ke format standar
            df_standard = self._convert_to_standard_format(df_clean)
            
            st.success(f"✅ Successfully parsed {len(df_standard)} records")
            return df_standard
            
        except Exception as e:
            st.error(f"❌ Error parsing file: {str(e)}")
            raise
    
    def _clean_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Bersihkan data mentah dari Excel"""
        df = df_raw.copy()
        
        # Find header row (contains 'SENIN')
        header_row_idx = None
        for idx in range(min(10, len(df))):  # Check first 10 rows
            row_vals = df.iloc[idx].astype(str).str.upper().tolist()
            if any('SENIN' in str(val) for val in row_vals):
                header_row_idx = idx
                break
        
        if header_row_idx is None:
            # Default to row 2 (index 1)
            header_row_idx = 1
        
        # Set header from found row
        header_row = df.iloc[header_row_idx].fillna('').astype(str).tolist()
        df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
        df.columns = header_row
        
        # Clean column names
        df.columns = [str(col).strip().upper() if pd.notna(col) else f"COL_{i}" 
                     for i, col in enumerate(df.columns)]
        
        # Fill forward for KSM and Doctor name
        if 'KSM' in df.columns:
            df['KSM'] = df['KSM'].ffill()
        
        if 'NAMA DOKTER SPESIALIS/ SUB SPESIALIS' in df.columns:
            df['NAMA DOKTER SPESIALIS/ SUB SPESIALIS'] = df['NAMA DOKTER SPESIALIS/ SUB SPESIALIS'].ffill()
        
        # Remove empty rows
        df = df.dropna(subset=['KSM', 'NAMA DOKTER SPESIALIS/ SUB SPESIALIS', 'POLI'], how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _convert_to_standard_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Konversi ke format standar aplikasi"""
        records = []
        
        # Group by KSM and Doctor name
        current_doctor = None
        current_ksm = None
        jam_kerja_data = {}
        reguler_data = {}
        eksekutif_data = {}
        
        for idx, row in df.iterrows():
            ksm = row.get('KSM', '')
            nama = row.get('NAMA DOKTER SPESIALIS/ SUB SPESIALIS', '')
            poli = row.get('POLI', '')
            
            # Skip jika semua kosong
            if pd.isna(ksm) and pd.isna(nama) and pd.isna(poli):
                continue
            
            # Convert to string and clean
            ksm = str(ksm).strip() if pd.notna(ksm) else ''
            nama = str(nama).strip() if pd.notna(nama) else ''
            poli = str(poli).strip() if pd.notna(poli) else ''
            
            # Update current doctor jika ada nama baru
            if nama and nama != current_doctor:
                # Save previous doctor if exists
                if current_doctor:
                    records.extend(
                        self._create_doctor_records(
                            current_ksm, current_doctor,
                            jam_kerja_data, reguler_data, eksekutif_data
                        )
                    )
                
                # Reset for new doctor
                current_doctor = nama
                current_ksm = ksm
                jam_kerja_data = {}
                reguler_data = {}
                eksekutif_data = {}
            
            # Collect data based on poli type
            for day_indonesia in self.days_mapping.keys():
                day_col = day_indonesia
                if day_col in row:
                    value = row[day_col]
                    
                    if pd.notna(value) and str(value).strip() not in ['', '-', 'nan', 'NAN', 'NaN']:
                        # Clean value
                        clean_value = self._clean_time_value(str(value))
                        
                        if poli == 'JAM KERJA':
                            jam_kerja_data[day_indonesia] = clean_value
                        elif poli == 'REGULER':
                            reguler_data[day_indonesia] = clean_value
                        elif poli == 'EKSEKUTIF':
                            eksekutif_data[day_indonesia] = clean_value
        
        # Add last doctor
        if current_doctor:
            records.extend(
                self._create_doctor_records(
                    current_ksm, current_doctor,
                    jam_kerja_data, reguler_data, eksekutif_data
                )
            )
        
        # Create DataFrame
        if records:
            result_df = pd.DataFrame(records)
            
            # Add metadata
            result_df['source_file'] = 'jadwal_hafis.xlsx'
            result_df['parsed_date'] = pd.Timestamp.now()
            result_df['available'] = result_df.apply(
                lambda x: 1 if (pd.notna(x['working_hours']) and x['working_hours'] != '') or 
                               (pd.notna(x['regular_schedule']) and x['regular_schedule'] != '') or
                               (pd.notna(x['executive_schedule']) and x['executive_schedule'] != '') 
                         else 0, 
                axis=1
            )
            
            return result_df
        else:
            return pd.DataFrame()
    
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
        
        # Get specialty
        specialty = self.specialty_map.get(ksm, ksm)
        
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
                'available': 0  # Will be calculated later
            }
            
            # Set available flag
            if (record['working_hours'] not in ['', '[Reference]'] or 
                record['regular_schedule'] not in ['', '[Reference]'] or 
                record['executive_schedule'] not in ['', '[Reference]']):
                record['available'] = 1
            
            records.append(record)
        
        return records
    
    def parse_time_range(self, time_str: str) -> Optional[Tuple[str, str]]:
        """Parse time range string"""
        if not time_str or time_str == '[Reference]':
            return None
        
        try:
            time_str = self._clean_time_value(time_str)
            
            if '-' in time_str:
                start_str, end_str = time_str.split('-')
                return (start_str, end_str)
            
        except:
            pass
        
        return None
