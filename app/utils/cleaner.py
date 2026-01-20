"""
Data cleaning utilities
"""
import pandas as pd
import numpy as np
import re

class DataCleaner:
    """Data cleaning utility class"""
    
    @staticmethod
    def clean_doctor_names(df: pd.DataFrame, name_column: str = 'doctor_name') -> pd.DataFrame:
        """Clean and standardize doctor names"""
        df = df.copy()
        
        if name_column in df.columns:
            df[name_column] = df[name_column].astype(str).apply(DataCleaner._clean_name)
        
        return df
    
    @staticmethod
    def _clean_name(name: str) -> str:
        """Clean individual doctor name"""
        if pd.isna(name):
            return ""
        
        name = str(name).strip()
        
        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name)
        
        # Capitalize properly
        parts = name.split()
        cleaned_parts = []
        
        for part in parts:
            if part.lower() in ['dr.', 'drg.', 'sp.', 'spa', 'spb', 'spog', 'sppd', 'spjp']:
                cleaned_parts.append(part.upper())
            elif len(part) > 1:
                cleaned_parts.append(part[0].upper() + part[1:].lower())
            else:
                cleaned_parts.append(part.upper())
        
        return ' '.join(cleaned_parts)
    
    @staticmethod
    def clean_specialty_names(df: pd.DataFrame, specialty_column: str = 'specialty') -> pd.DataFrame:
        """Clean and standardize specialty names"""
        df = df.copy()
        
        if specialty_column in df.columns:
            df[specialty_column] = df[specialty_column].astype(str).apply(DataCleaner._clean_specialty)
        
        return df
    
    @staticmethod
    def _clean_specialty(specialty: str) -> str:
        """Clean specialty name"""
        if pd.isna(specialty):
            return ""
        
        specialty = str(specialty).strip()
        
        # Common replacements
        replacements = {
            'PEDIATRICS': 'Pediatrics',
            'SURGERY': 'Surgery',
            'INTERNAL MEDICINE': 'Internal Medicine',
            'OBSTETRICS & GYNECOLOGY': 'Obstetrics & Gynecology',
            'CARDIOLOGY': 'Cardiology',
            'ORTHOPEDICS': 'Orthopedics',
            'PULMONOLOGY': 'Pulmonology',
            'NEUROLOGY': 'Neurology',
            'ENT': 'ENT',
            'UROLOGY': 'Urology',
            'PSYCHIATRY': 'Psychiatry',
            'DERMATOLOGY': 'Dermatology',
            'NEUROSURGERY': 'Neurosurgery',
            'DENTISTRY': 'Dentistry',
            'OPHTHALMOLOGY': 'Ophthalmology',
            'ANESTHESIOLOGY': 'Anesthesiology',
            'RADIOLOGY': 'Radiology'
        }
        
        # Capitalize properly
        words = specialty.split()
        cleaned_words = []
        
        for word in words:
            upper_word = word.upper()
            if upper_word in replacements:
                cleaned_words.append(replacements[upper_word])
            else:
                cleaned_words.append(word.title())
        
        return ' '.join(cleaned_words)
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
        """Remove duplicate rows"""
        if subset is None:
            subset = ['doctor_name', 'day', 'specialty']
        
        # Only use columns that exist
        subset = [col for col in subset if col in df.columns]
        
        if subset:
            return df.drop_duplicates(subset=subset, keep='first')
        
        return df
    
    @staticmethod
    def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with appropriate defaults"""
        df = df.copy()
        
        # Fill doctor_name if missing
        if 'doctor_name' in df.columns:
            df['doctor_name'] = df['doctor_name'].fillna('Unknown Doctor')
        
        # Fill specialty if missing
        if 'specialty' in df.columns:
            df['specialty'] = df['specialty'].fillna('General')
        
        # Fill day if missing
        if 'day' in df.columns:
            df['day'] = df['day'].fillna('Monday')
        
        # Fill available if missing
        if 'available' in df.columns:
            df['available'] = df['available'].fillna(0).astype(int)
        
        return df
