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
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    TEMPLATE_DIR = BASE_DIR / "templates"
    
    # Default settings
    DEFAULT_WORKING_HOURS = {
        "start": "07:00",
        "end": "15:00"
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
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Display settings
    PAGE_TITLE = "Jadwal Dokter RS"
    PAGE_ICON = "🏥"
    LAYOUT = "wide"
    
    # Colors
    COLORS = {
        "primary": "#1E88E5",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
        "info": "#2196F3"
    }
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.TEMPLATE_DIR.mkdir(exist_ok=True)
