"""
Data management core logic
"""
import pandas as pd
import numpy as np
from datetime import datetime, time
from typing import Dict, List, Any, Optional
import streamlit as st

class DataManager:
    """Manages data operations for the application"""
    
    def __init__(self):
        self.data = None
        self.original_data = None
    
    def load_data(self, file_path: str, file_type: str = 'excel'):
        """Load data from file"""
        try:
            if file_type == 'excel':
                self.data = pd.read_excel(file_path)
            elif file_type == 'csv':
                self.data = pd.read_csv(file_path)
            
            self.original_data = self.data.copy()
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def save_data(self, file_path: str, file_type: str = 'excel'):
        """Save data to file"""
        try:
            if file_type == 'excel':
                self.data.to_excel(file_path, index=False)
            elif file_type == 'csv':
                self.data.to_csv(file_path, index=False)
            return True
            
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
            return False
    
    def get_doctor_schedule(self, doctor_name: str) -> pd.DataFrame:
        """Get schedule for specific doctor"""
        if self.data is not None and 'doctor_name' in self.data.columns:
            return self.data[self.data['doctor_name'] == doctor_name].copy()
        return pd.DataFrame()
    
    def get_day_schedule(self, day: str) -> pd.DataFrame:
        """Get schedule for specific day"""
        if self.data is not None and 'day' in self.data.columns:
            return self.data[self.data['day'] == day].copy()
        return pd.DataFrame()
    
    def get_specialty_schedule(self, specialty: str) -> pd.DataFrame:
        """Get schedule for specific specialty"""
        if self.data is not None and 'specialty' in self.data.columns:
            return self.data[self.data['specialty'] == specialty].copy()
        return pd.DataFrame()
    
    def get_available_doctors(self, day: str = None) -> List[str]:
        """Get list of available doctors"""
        if self.data is None or 'doctor_name' not in self.data.columns:
            return []
        
        if day and 'day' in self.data.columns and 'available' in self.data.columns:
            available_df = self.data[(self.data['day'] == day) & (self.data['available'] == 1)]
            return sorted(available_df['doctor_name'].unique().tolist())
        
        return sorted(self.data['doctor_name'].unique().tolist())
    
    def get_specialties(self) -> List[str]:
        """Get list of specialties"""
        if self.data is not None and 'specialty' in self.data.columns:
            return sorted(self.data['specialty'].unique().tolist())
        return []
    
    def get_days(self) -> List[str]:
        """Get list of days with data"""
        if self.data is not None and 'day' in self.data.columns:
            return sorted(self.data['day'].unique().tolist())
        return []
    
    def add_schedule(self, schedule_data: Dict[str, Any]):
        """Add new schedule entry"""
        if self.data is None:
            # Create new DataFrame
            self.data = pd.DataFrame([schedule_data])
        else:
            # Append to existing DataFrame
            new_df = pd.DataFrame([schedule_data])
            self.data = pd.concat([self.data, new_df], ignore_index=True)
    
    def update_schedule(self, index: int, schedule_data: Dict[str, Any]):
        """Update existing schedule entry"""
        if self.data is not None and 0 <= index < len(self.data):
            for key, value in schedule_data.items():
                if key in self.data.columns:
                    self.data.at[index, key] = value
    
    def delete_schedule(self, index: int):
        """Delete schedule entry"""
        if self.data is not None and 0 <= index < len(self.data):
            self.data = self.data.drop(index).reset_index(drop=True)
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate statistics from data"""
        stats = {}
        
        if self.data is not None and not self.data.empty:
            stats['total_entries'] = len(self.data)
            
            if 'doctor_name' in self.data.columns:
                stats['total_doctors'] = len(self.data['doctor_name'].unique())
            
            if 'specialty' in self.data.columns:
                stats['total_specialties'] = len(self.data['specialty'].unique())
            
            if 'day' in self.data.columns:
                stats['days_covered'] = len(self.data['day'].unique())
            
            if 'available' in self.data.columns:
                stats['available_slots'] = int(self.data['available'].sum())
                stats['availability_rate'] = round((self.data['available'].sum() / len(self.data)) * 100, 2)
            
            # Calculate working hours if available
            if 'working_hours' in self.data.columns:
                total_hours = 0
                for hours in self.data['working_hours']:
                    if pd.notna(hours) and isinstance(hours, str) and '-' in hours:
                        # Simple calculation: assume 8 hours per working day
                        total_hours += 8
                stats['total_working_hours'] = total_hours
        
        return stats
    
    def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Filter data based on criteria"""
        if self.data is None:
            return pd.DataFrame()
        
        filtered_df = self.data.copy()
        
        for column, value in filters.items():
            if column in filtered_df.columns and value is not None:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def reset_to_original(self):
        """Reset data to original state"""
        if self.original_data is not None:
            self.data = self.original_data.copy()
