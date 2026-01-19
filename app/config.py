"""
Konfigurasi aplikasi Jadwal Dokter
"""
from datetime import datetime, time, date
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import streamlit as st

@dataclass
class TimeSlot:
    """Representasi slot waktu"""
    start: time
    end: time
    day: str = ""
    doctor: str = ""
    specialization: str = ""
    
    @property
    def duration(self) -> float:
        """Durasi dalam jam"""
        start_minutes = self.start.hour * 60 + self.start.minute
        end_minutes = self.end.hour * 60 + self.end.minute
        return (end_minutes - start_minutes) / 60.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            "start": self.start.strftime("%H:%M"),
            "end": self.end.strftime("%H:%M"),
            "day": self.day,
            "doctor": self.doctor,
            "specialization": self.specialization,
            "duration": self.duration
        }

class AppConfig:
    """Konfigurasi utama aplikasi"""
    
    # ============ WAKTU KERJA ============
    WORK_START = time(8, 0)      # 08:00
    WORK_END = time(16, 0)       # 16:00
    LUNCH_START = time(12, 0)    # 12:00
    LUNCH_END = time(13, 0)      # 13:00
    
    # ============ HARI KERJA ============
    WORK_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    WEEKDAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    WEEKEND = ["Sabtu", "Minggu"]
    
    # ============ SLOT WAKTU ============
    TIME_SLOT_DURATION = 60  # menit
    MIN_SLOT_DURATION = 30   # menit
    MAX_SLOT_DURATION = 120  # menit
    
    # ============ UI CONFIG ============
    PAGE_TITLE = "Sistem Penjadwalan Dokter"
    PAGE_ICON = "🏥"
    LAYOUT = "wide"
    
    # Colors
    COLORS = {
        "primary": "#1E88E5",
        "secondary": "#FFC107",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
        "info": "#2196F3"
    }
    
    # Specialization colors
    SPECIALIZATION_COLORS = {
        "Umum": "#4CAF50",
        "Spesialis": "#2196F3",
        "Gigi": "#FF9800",
        "Anak": "#9C27B0",
        "Bedah": "#F44336",
        "Jantung": "#E91E63",
        "Mata": "#00BCD4"
    }
    
    # ============ FILE CONFIG ============
    ALLOWED_EXTENSIONS = ['.xlsx', '.xls', '.csv', '.xlsm']
    MAX_FILE_SIZE_MB = 20
    DEFAULT_ENCODING = 'utf-8'
    
    # ============ VALIDATION RULES ============
    REQUIRED_COLUMNS = [
        "nama_dokter",
        "spesialisasi",
        "hari",
        "jam_mulai",
        "jam_selesai"
    ]
    
    OPTIONAL_COLUMNS = [
        "ruangan",
        "poliklinik",
        "kapasitas",
        "catatan"
    ]
    
    # ============ SESSION KEYS ============
    SESSION_KEYS = {
        "uploaded_data": "uploaded_data",
        "schedule_data": "schedule_data",
        "preferences": "preferences",
        "doctors_list": "doctors_list",
        "validation_errors": "validation_errors"
    }
    
    # ============ PROPERTIES ============
    @property
    def time_slot_start(self) -> time:
        """Waktu mulai slot"""
        return self.WORK_START
    
    @property
    def time_slot_end(self) -> time:
        """Waktu akhir slot"""
        return self.WORK_END
    
    @property
    def working_hours(self) -> float:
        """Total jam kerja per hari"""
        start = self.WORK_START.hour + self.WORK_START.minute / 60
        end = self.WORK_END.hour + self.WORK_END.minute / 60
        lunch = 1.0  # 1 jam istirahat
        return end - start - lunch
    
    # ============ METHODS ============
    @classmethod
    def get_time_slots(cls, include_lunch_break: bool = True) -> List[TimeSlot]:
        """Generate semua time slot untuk satu hari"""
        slots = []
        current_time = datetime.combine(date.today(), cls.WORK_START)
        end_time = datetime.combine(date.today(), cls.WORK_END)
        lunch_start = datetime.combine(date.today(), cls.LUNCH_START)
        lunch_end = datetime.combine(date.today(), cls.LUNCH_END)
        
        while current_time < end_time:
            slot_end = current_time + datetime.timedelta(minutes=cls.TIME_SLOT_DURATION)
            
            # Lewati waktu istirahat jika include_lunch_break=True
            if include_lunch_break:
                if current_time < lunch_end and slot_end > lunch_start:
                    current_time = lunch_end
                    continue
            
            # Buat slot
            slot = TimeSlot(
                start=current_time.time(),
                end=slot_end.time()
            )
            slots.append(slot)
            
            current_time = slot_end
        
        return slots
    
    @classmethod
    def get_day_color(cls, day: str) -> str:
        """Dapatkan warna untuk hari tertentu"""
        day_colors = {
            "Senin": "#FFEBEE",
            "Selasa": "#F3E5F5",
            "Rabu": "#E8EAF6",
            "Kamis": "#E0F2F1",
            "Jumat": "#FFF8E1",
            "Sabtu": "#F1F8E9",
            "Minggu": "#ECEFF1"
        }
        return day_colors.get(day, "#FFFFFF")
    
    @classmethod
    def save_preferences(cls, preferences: Dict[str, Any]):
        """Simpan preferensi ke session state"""
        for key, value in preferences.items():
            st.session_state[f"pref_{key}"] = value
    
    @classmethod
    def load_preferences(cls) -> Dict[str, Any]:
        """Load preferensi dari session state"""
        preferences = {}
        prefix = "pref_"
        
        for key in st.session_state.keys():
            if key.startswith(prefix):
                pref_key = key[len(prefix):]
                preferences[pref_key] = st.session_state[key]
        
        return preferences

# Instance global
config = AppConfig()
