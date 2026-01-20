"""
Template parsing utilities
"""
import pandas as pd
import json

class TemplateParser:
    """Template parsing utility class"""
    
    @staticmethod
    def create_template() -> pd.DataFrame:
        """Create an empty template DataFrame"""
        template_data = {
            'doctor_name': [],
            'specialty': [],
            'department': [],
            'day': [],
            'working_hours': [],
            'regular_schedule': [],
            'executive_schedule': [],
            'start_time': [],
            'end_time': [],
            'available': []
        }
        
        return pd.DataFrame(template_data)
    
    @staticmethod
    def save_template(template_df: pd.DataFrame, filepath: str):
        """Save template to file"""
        if filepath.endswith('.xlsx'):
            template_df.to_excel(filepath, index=False)
        elif filepath.endswith('.csv'):
            template_df.to_csv(filepath, index=False)
    
    @staticmethod
    def load_template(filepath: str) -> pd.DataFrame:
        """Load template from file"""
        if filepath.endswith('.xlsx'):
            return pd.read_excel(filepath)
        elif filepath.endswith('.csv'):
            return pd.read_csv(filepath)
        else:
            raise ValueError("Unsupported file format. Use .xlsx or .csv")
    
    @staticmethod
    def validate_template(template_df: pd.DataFrame):
        """Validate template structure"""
        errors = []
        
        # Check required columns
        required_columns = ['doctor_name', 'specialty', 'day']
        for col in required_columns:
            if col not in template_df.columns:
                errors.append(f"Missing required column: {col}")
        
        # Check data types
        if 'available' in template_df.columns:
            if not pd.api.types.is_numeric_dtype(template_df['available']):
                errors.append("Column 'available' must be numeric (0 or 1)")
        
        if errors:
            return False, errors
        
        return True, []
    
    @staticmethod
    def generate_sample_data() -> pd.DataFrame:
        """Generate sample data for testing"""
        sample_data = {
            'doctor_name': [
                'Dr. John Doe', 'Dr. John Doe', 'Dr. Jane Smith', 'Dr. Jane Smith',
                'Dr. Robert Johnson', 'Dr. Robert Johnson'
            ],
            'specialty': [
                'Cardiology', 'Cardiology', 'Pediatrics', 'Pediatrics',
                'Surgery', 'Surgery'
            ],
            'department': [
                'Cardiology', 'Cardiology', 'Pediatrics', 'Pediatrics',
                'General Surgery', 'General Surgery'
            ],
            'day': [
                'Monday', 'Tuesday', 'Monday', 'Wednesday',
                'Tuesday', 'Thursday'
            ],
            'working_hours': [
                '08:00-16:00', '08:00-16:00', '09:00-17:00', '09:00-17:00',
                '07:00-15:00', '07:00-15:00'
            ],
            'regular_schedule': [
                '08:00-12:00', '08:00-12:00', '09:00-13:00', '09:00-13:00',
                '07:00-11:00', '07:00-11:00'
            ],
            'executive_schedule': [
                '14:00-16:00', '14:00-16:00', '14:00-17:00', '14:00-17:00',
                '12:00-15:00', '12:00-15:00'
            ],
            'available': [1, 1, 1, 1, 1, 1]
        }
        
        return pd.DataFrame(sample_data)
