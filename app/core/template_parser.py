"""
TemplateParser - Parser for the new KSM-based Excel template format
Converts the new template format to the standard format expected by the scheduler
"""

import pandas as pd
import io
from typing import Union, List
import traceback


class TemplateParser:
    """
    Parser for the new Excel template format with structure:
    - Row 0: Title ("Lampiran (kertas kerja)")
    - Row 1: Headers (KSM, Nama dokter, POLI, JAM PRAKTIK)
    - Row 2: Day names (SENIN, SELASA, RABU, KAMIS, JUMAT, SABTU) in columns 3-8
    - Row 3+: Doctor data - each doctor has 3 rows:
      - Row with KSM & doctor name + JAM KERJA
      - Row with REGULER schedule
      - Row with EKSEKUTIF schedule
    """
    
    def __init__(self):
        self.day_mapping = {
            'SENIN': 'Senin',
            'SELASA': 'Selasa',
            'RABU': 'Rabu',
            'KAMIS': 'Kamis',
            'JUMAT': "Jum'at",
            'JUM\'AT': "Jum'at",
            'SABTU': 'Sabtu'
        }
        print("✅ TemplateParser initialized")
    
    def parse(self, file_or_bytes: Union[io.BytesIO, str, bytes]) -> pd.DataFrame:
        """
        Parse the new template format and convert to standard format
        """
        print("🔄 TemplateParser.parse() called")
        
        try:
            if isinstance(file_or_bytes, bytes):
                file_or_bytes = io.BytesIO(file_or_bytes)
            elif isinstance(file_or_bytes, io.BytesIO):
                file_or_bytes.seek(0)
            
            df_raw = pd.read_excel(file_or_bytes, sheet_name=0, header=None)
            print(f"   Raw data loaded: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
            
            parsed_data = self._parse_template(df_raw)
            
            if parsed_data:
                result_df = pd.DataFrame(parsed_data)
                print(f"✅ Parsed {len(result_df)} doctor schedule entries")
                return result_df
            else:
                print("⚠️ No data parsed from template")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error parsing template: {e}")
            print(traceback.format_exc())
            raise
    
    def _parse_template(self, df: pd.DataFrame) -> List[dict]:
        """
        Parse the raw DataFrame from the new template format
        """
        results = []
        day_columns = {}
        
        for col_idx in range(3, min(9, len(df.columns))):
            if len(df) > 2:
                day_name = str(df.iloc[2, col_idx]).strip().upper()
                if day_name in self.day_mapping:
                    day_columns[col_idx] = self.day_mapping[day_name]
        
        print(f"   Day columns detected: {day_columns}")
        
        if not day_columns:
            print("   ⚠️ No day columns found, trying alternative detection")
            for row_idx in range(min(5, len(df))):
                for col_idx in range(len(df.columns)):
                    cell_val = str(df.iloc[row_idx, col_idx]).strip().upper()
                    if cell_val in self.day_mapping and col_idx not in day_columns:
                        day_columns[col_idx] = self.day_mapping[cell_val]
            print(f"   Day columns (alternative): {day_columns}")
        
        current_ksm = None
        current_doctor = None
        doctor_data = {}
        
        start_row = 3
        
        for row_idx in range(start_row, len(df)):
            row = df.iloc[row_idx]
            
            col0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() != 'nan' else ''
            col1 = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) and str(row.iloc[1]).strip() != 'nan' else ''
            col2 = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) and str(row.iloc[2]).strip() != 'nan' else ''
            
            if col0:
                skip_values = ['KSM', 'SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU', 
                               'JAM KERJA', 'REGULER', 'EKSEKUTIF', 'nan', 'NaN']
                if col0.upper() not in [s.upper() for s in skip_values]:
                    current_ksm = col0
            
            if col1:
                if 'dr.' in col1.lower() or 'Dr.' in col1:
                    if current_doctor and doctor_data:
                        entries = self._create_entries(current_doctor, current_ksm, doctor_data)
                        results.extend(entries)
                    
                    current_doctor = col1
                    doctor_data = {'reguler': {}, 'eksekutif': {}}
            
            poli_type = col2.upper()
            
            if poli_type in ['REGULER', 'EKSEKUTIF']:
                key = 'reguler' if poli_type == 'REGULER' else 'eksekutif'
                
                for col_idx, day_name in day_columns.items():
                    if col_idx < len(row):
                        time_value = row.iloc[col_idx]
                        if pd.notna(time_value):
                            time_str = str(time_value).strip()
                            if time_str and time_str not in ['nan', 'NaN', '-', '']:
                                doctor_data[key][day_name] = time_str
        
        if current_doctor and doctor_data:
            entries = self._create_entries(current_doctor, current_ksm, doctor_data)
            results.extend(entries)
        
        return results
    
    def _create_entries(self, doctor_name: str, ksm: str, doctor_data: dict) -> List[dict]:
        """
        Create standardized entries for a doctor
        """
        entries = []
        days = ['Senin', 'Selasa', 'Rabu', 'Kamis', "Jum'at", 'Sabtu']
        
        reguler_data = doctor_data.get('reguler', {})
        if any(reguler_data.values()):
            entry = {
                'Nama Dokter': doctor_name,
                'Poli Asal': ksm if ksm else 'Unknown',
                'Jenis Poli': 'Reguler'
            }
            for day in days:
                entry[day] = reguler_data.get(day, None)
            entries.append(entry)
        
        eksekutif_data = doctor_data.get('eksekutif', {})
        if any(eksekutif_data.values()):
            entry = {
                'Nama Dokter': doctor_name,
                'Poli Asal': ksm if ksm else 'Unknown',
                'Jenis Poli': 'Poleks'
            }
            for day in days:
                entry[day] = eksekutif_data.get(day, None)
            entries.append(entry)
        
        return entries
    
    def is_new_template_format(self, file_or_bytes: Union[io.BytesIO, str, bytes]) -> bool:
        """
        Check if the file is in the new template format
        """
        try:
            if isinstance(file_or_bytes, bytes):
                file_or_bytes = io.BytesIO(file_or_bytes)
            elif isinstance(file_or_bytes, io.BytesIO):
                file_or_bytes.seek(0)
            
            xl = pd.ExcelFile(file_or_bytes)
            
            if 'Reguler' in xl.sheet_names or 'Poleks' in xl.sheet_names:
                return False
            
            if isinstance(file_or_bytes, io.BytesIO):
                file_or_bytes.seek(0)
            
            df = pd.read_excel(file_or_bytes, sheet_name=0, header=None, nrows=5)
            
            first_cell = str(df.iloc[0, 0]).strip().lower() if pd.notna(df.iloc[0, 0]) else ''
            if 'lampiran' in first_cell or 'kertas kerja' in first_cell:
                return True
            
            second_row_first = str(df.iloc[1, 0]).strip().lower() if pd.notna(df.iloc[1, 0]) else ''
            if 'ksm' in second_row_first:
                return True
            
            for row_idx in range(min(5, len(df))):
                row_values = [str(v).upper().strip() for v in df.iloc[row_idx] if pd.notna(v)]
                day_indicators = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
                matches = sum(1 for day in day_indicators if day in row_values)
                if matches >= 3:
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking template format: {e}")
            return False


def parse_new_template(file_or_bytes: Union[io.BytesIO, str, bytes]) -> pd.DataFrame:
    """Utility function for parsing new template format"""
    parser = TemplateParser()
    return parser.parse(file_or_bytes)


def is_new_format(file_or_bytes: Union[io.BytesIO, str, bytes]) -> bool:
    """Utility function to check if file is new format"""
    parser = TemplateParser()
    return parser.is_new_template_format(file_or_bytes)


__all__ = ['TemplateParser', 'parse_new_template', 'is_new_format']
