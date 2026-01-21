"""
Configuration for Jadwal Dokter App
"""
import os
from pathlib import Path

class AppConfig:
    """Application configuration"""
    
    # App info
    APP_NAME = "Jadwal Dokter RS"
    APP_VERSION = "1.0.0"
    
    # Default settings
    DEFAULT_WORKING_HOURS = {
        "start": "08:00",
        "end": "16:00"
    }
    
    DAYS_OF_WEEK = [
        "Monday", "Tuesday", "Wednesday", 
        "Thursday", "Friday", "Saturday", "Sunday"
    ]
    
    DAYS_INDONESIA = {
        "Monday": "Senin",
        "Tuesday": "Selasa", 
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu"
    }
    
    # File settings
    ALLOWED_EXTENSIONS = ['.xlsx', '.xls', '.csv']
    
    # Display settings
    PAGE_TITLE = "Jadwal Dokter RS"
    PAGE_ICON = "🏥"
    LAYOUT = "wide"
