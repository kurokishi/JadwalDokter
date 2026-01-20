"""
Modul untuk parsing dan manipulasi waktu
"""
from datetime import datetime, time, date, timedelta
from typing import List, Tuple, Optional, Dict, Any
import re
from ..config import TimeSlot, config
from ..utils import parse_time

class TimeParser:
    """Utility untuk parsing dan manipulasi waktu"""
    
    @staticmethod
    def parse_time_range(start_str: str, end_str: str) -> Tuple[Optional[time], Optional[time]]:
        """Parse range waktu dari string"""
        start_time = parse_time(start_str)
        end_time = parse_time(end_str)
        
        return start_time, end_time
    
    @staticmethod
    def split_into_slots(start_time: time, end_time: time, 
                        duration_minutes: int = 60) -> List[TimeSlot]:
        """Split waktu menjadi slot-slot dengan durasi tertentu"""
        slots = []
        
        current_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        
        # Handle overnight schedules
        if end_dt < current_dt:
            end_dt += timedelta(days=1)
        
        while current_dt + timedelta(minutes=duration_minutes) <= end_dt:
            slot_end_dt = current_dt + timedelta(minutes=duration_minutes)
            
            slot = TimeSlot(
                start=current_dt.time(),
                end=slot_end_dt.time()
            )
            slots.append(slot)
            
            current_dt = slot_end_dt
        
        return slots
    
    @staticmethod
    def calculate_working_hours(slots: List[TimeSlot]) -> float:
        """Hitung total jam kerja dari slot-slot"""
        total_hours = 0
        for slot in slots:
            total_hours += slot.duration
        return total_hours
    
    @staticmethod
    def find_available_slots(busy_slots: List[TimeSlot], day: str = "", 
                           doctor: str = "") -> List[TimeSlot]:
        """Temukan slot yang tersedia berdasarkan slot yang sudah terisi"""
        # Generate semua slot untuk hari kerja
        all_slots = config.get_time_slots()
        
        # Filter out busy slots
        available_slots = []
        
        for slot in all_slots:
            is_busy = False
            
            for busy in busy_slots:
                # Cek overlap
                if TimeParser._slots_overlap(slot, busy):
                    is_busy = True
                    break
            
            if not is_busy:
                # Tambahkan info hari dan dokter jika disediakan
                available_slot = TimeSlot(
                    start=slot.start,
                    end=slot.end,
                    day=day,
                    doctor=doctor
                )
                available_slots.append(available_slot)
        
        return available_slots
    
    @staticmethod
    def _slots_overlap(slot1: TimeSlot, slot2: TimeSlot) -> bool:
        """Cek jika dua slot overlap"""
        start1 = slot1.start.hour * 60 + slot1.start.minute
        end1 = slot1.end.hour * 60 + slot1.end.minute
        start2 = slot2.start.hour * 60 + slot2.start.minute
        end2 = slot2.end.hour * 60 + slot2.end.minute
        
        # Handle overnight
        if end1 < start1:
            end1 += 24 * 60
        if end2 < start2:
            end2 += 24 * 60
        
        return not (end1 <= start2 or end2 <= start1)
    
    @staticmethod
    def merge_consecutive_slots(slots: List[TimeSlot]) -> List[TimeSlot]:
        """Merge slot yang berurutan"""
        if not slots:
            return []
        
        # Sort by start time
        sorted_slots = sorted(slots, key=lambda x: x.start)
        
        merged = []
        current = sorted_slots[0]
        
        for slot in sorted_slots[1:]:
            # Jika slot berurutan atau overlap
            if (current.end.hour * 60 + current.end.minute >= 
                slot.start.hour * 60 + slot.start.minute):
                # Merge: extend end time if needed
                if slot.end > current.end:
                    current.end = slot.end
            else:
                merged.append(current)
                current = slot
        
        merged.append(current)
        
        return merged
    
    @staticmethod
    def calculate_daily_schedule(doctor_slots: List[TimeSlot], day: str) -> Dict[str, Any]:
        """Hitung jadwal harian untuk dokter"""
        # Filter slots untuk hari tertentu
        day_slots = [slot for slot in doctor_slots if slot.day == day]
        
        if not day_slots:
            return {
                'day': day,
                'has_schedule': False,
                'total_slots': 0,
                'total_hours': 0,
                'slots': []
            }
        
        # Merge consecutive slots
        merged_slots = TimeParser.merge_consecutive_slots(day_slots)
        
        # Calculate totals
        total_hours = TimeParser.calculate_working_hours(merged_slots)
        
        return {
            'day': day,
            'has_schedule': True,
            'total_slots': len(merged_slots),
            'total_hours': total_hours,
            'slots': merged_slots
        }
    
    @staticmethod
    def format_time_range(start_time: time, end_time: time) -> str:
        """Format range waktu menjadi string yang mudah dibaca"""
        start_str = start_time.strftime("%H:%M")
        end_str = end_time.strftime("%H:%M")
        return f"{start_str} - {end_str}"
    
    @staticmethod
    def get_time_difference(time1: time, time2: time) -> timedelta:
        """Hitung perbedaan waktu antara dua time object"""
        datetime1 = datetime.combine(date.today(), time1)
        datetime2 = datetime.combine(date.today(), time2)
        
        if datetime2 < datetime1:
            datetime2 += timedelta(days=1)
        
        return datetime2 - datetime1
    
    @staticmethod
    def validate_time_order(start_time: time, end_time: time) -> Tuple[bool, str]:
        """Validasi urutan waktu (start < end)"""
        if start_time == end_time:
            return False, "Waktu mulai dan selesai tidak boleh sama"
        
        if end_time < start_time:
            # Mungkin overnight schedule
            # Tambahkan 24 jam untuk end_time untuk perbandingan
            end_time_adj = time((end_time.hour + 24) % 24, end_time.minute)
            if end_time_adj < start_time:
                return False, "Waktu selesai harus setelah waktu mulai"
        
        return True, "Waktu valid"
