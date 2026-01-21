"""
Application configuration settings
"""
from datetime import time
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Application configuration"""
    
    # App metadata
    APP_NAME = "Jadwal Dokter Converter"
    VERSION = "2.0.0"
    AUTHOR = "Jadwal Dokter Team"
    
    # Time settings
    WORK_START = time(7, 0)  # 07:00
    WORK_END = time(14, 0)   # 14:00
    TIME_SLOT_MINUTES = 30   # 30 minutes per slot
    
    # File settings
    ALLOWED_EXTENSIONS = ['.xlsx', '.xls']
    MAX_FILE_SIZE_MB = 10
    
    # Display settings
    DEFAULT_TIME_SLOTS = [
        "07:00", "07:30", "08:00", "08:30", "09:00", "09:30",
        "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
        "13:00", "13:30", "14:00"
    ]
    
    DAYS = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
    JENIS_OPTIONS = ['Reguler', 'Eksekutif']
    
    # Color codes for Excel output
    COLOR_REGULER = "C6EFCE"  # Light green
    COLOR_EKSEKUTIF = "FFEB9C"  # Light yellow
    COLOR_HEADER = "4472C4"  # Blue
    
    @property
    def time_slots(self):
        """Generate time slots from WORK_START to WORK_END"""
        slots = []
        current = self.WORK_START
        
        while current < self.WORK_END:
            slots.append(current.strftime("%H:%M"))
            # Add TIME_SLOT_MINUTES
            hour = current.hour
            minute = current.minute + self.TIME_SLOT_MINUTES
            if minute >= 60:
                hour += 1
                minute -= 60
            current = time(hour, minute)
        
        return slots
