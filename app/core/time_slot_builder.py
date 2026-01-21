"""
Build time slots from time ranges
"""
from typing import List, Tuple, Dict
from app.utils import time_to_minutes, minutes_to_time


class TimeSlotBuilder:
    """Build time slots for grid format"""
    
    def __init__(self, start_time: str = "07:00", end_time: str = "14:00", 
                 interval_minutes: int = 30):
        self.start_time = start_time
        self.end_time = end_time
        self.interval_minutes = interval_minutes
        self.time_slots = self._generate_time_slots()
    
    def _generate_time_slots(self) -> List[str]:
        """Generate time slots based on configuration"""
        slots = []
        
        start_min = time_to_minutes(self.start_time)
        end_min = time_to_minutes(self.end_time)
        
        current = start_min
        while current < end_min:
            slots.append(minutes_to_time(current))
            current += self.interval_minutes
        
        return slots
    
    def get_time_slots(self) -> List[str]:
        """Get all time slots"""
        return self.time_slots.copy()
    
    def fill_slots_for_range(self, start_range: str, end_range: str, 
                           fill_value: str = 'R') -> Dict[str, str]:
        """
        Fill time slots for a given time range
        
        Args:
            start_range: Start time (e.g., "08:00")
            end_range: End time (e.g., "12:00")
            fill_value: Value to fill (e.g., 'R' or 'E')
            
        Returns:
            Dictionary mapping time slots to fill values
        """
        filled_slots = {}
        
        start_min = time_to_minutes(start_range)
        end_min = time_to_minutes(end_range)
        
        for slot in self.time_slots:
            slot_min = time_to_minutes(slot)
            
            if start_min <= slot_min < end_min:
                filled_slots[slot] = fill_value
            else:
                filled_slots[slot] = ''
        
        return filled_slots
    
    def merge_slot_fills(self, slot_fills_list: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Merge multiple slot fill dictionaries
        
        Args:
            slot_fills_list: List of slot fill dictionaries
            
        Returns:
            Merged dictionary
        """
        merged = {}
        
        # Initialize with empty values
        for slot in self.time_slots:
            merged[slot] = ''
        
        # Merge all fills
        for slot_fills in slot_fills_list:
            for slot, value in slot_fills.items():
                if value:  # Only overwrite if value is not empty
                    merged[slot] = value
        
        return merged
    
    def get_slot_coverage(self, slot_fills: Dict[str, str]) -> Dict[str, int]:
        """
        Get coverage statistics for filled slots
        
        Args:
            slot_fills: Dictionary of filled slots
            
        Returns:
            Statistics dictionary
        """
        total_slots = len(self.time_slots)
        filled_slots = sum(1 for value in slot_fills.values() if value)
        empty_slots = total_slots - filled_slots
        
        # Count by fill type
        fill_counts = {}
        for value in slot_fills.values():
            if value:
                fill_counts[value] = fill_counts.get(value, 0) + 1
        
        return {
            'total_slots': total_slots,
            'filled_slots': filled_slots,
            'empty_slots': empty_slots,
            'fill_counts': fill_counts,
            'coverage_percentage': (filled_slots / total_slots * 100) if total_slots > 0 else 0
        }
