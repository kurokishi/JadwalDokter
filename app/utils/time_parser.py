"""
Time parsing utilities
"""
import re
from datetime import time, datetime
import pandas as pd

class TimeParser:
    """Time parsing utility class"""
    
    @staticmethod
    def parse_time(time_str: str):
        """Parse time string to datetime.time object"""
        if not time_str or pd.isna(time_str):
            return None
        
        time_str = str(time_str).strip()
        
        # Handle various formats
        # Format 1: HH:MM
        if re.match(r'^\d{1,2}:\d{2}$', time_str):
            hours, minutes = map(int, time_str.split(':'))
            if 0 <= hours < 24 and 0 <= minutes < 60:
                return time(hours, minutes)
        
        # Format 2: HH.MM
        elif re.match(r'^\d{1,2}\.\d{2}$', time_str):
            hours, minutes = map(int, time_str.split('.'))
            if 0 <= hours < 24 and 0 <= minutes < 60:
                return time(hours, minutes)
        
        # Format 3: HHMM
        elif re.match(r'^\d{3,4}$', time_str):
            if len(time_str) == 3:
                hours = int(time_str[0])
                minutes = int(time_str[1:])
            else:
                hours = int(time_str[:2])
                minutes = int(time_str[2:])
            
            if 0 <= hours < 24 and 0 <= minutes < 60:
                return time(hours, minutes)
        
        return None
    
    @staticmethod
    def parse_time_range(time_range_str: str):
        """Parse time range string to start and end times"""
        if not time_range_str:
            return None
        
        time_range_str = str(time_range_str).strip()
        
        # Split by common separators
        separators = ['-', 'to', 's/d', 'sd', 's.d']
        
        for sep in separators:
            if sep in time_range_str:
                parts = time_range_str.split(sep, 1)
                if len(parts) == 2:
                    start_time = TimeParser.parse_time(parts[0].strip())
                    end_time = TimeParser.parse_time(parts[1].strip())
                    
                    if start_time and end_time:
                        return (start_time, end_time)
        
        return None
    
    @staticmethod
    def format_time(time_obj: time, format_24h: bool = True) -> str:
        """Format time object to string"""
        if not time_obj:
            return ""
        
        if format_24h:
            return time_obj.strftime("%H:%M")
        else:
            return time_obj.strftime("%I:%M %p")
    
    @staticmethod
    def calculate_duration(start_time: time, end_time: time) -> float:
        """Calculate duration in hours"""
        if not start_time or not end_time:
            return 0.0
        
        # Convert to datetime for calculation
        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = datetime.combine(datetime.today(), end_time)
        
        # Handle overnight
        if end_dt < start_dt:
            end_dt = end_dt.replace(day=end_dt.day + 1)
        
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        return round(duration_hours, 2)
    
    @staticmethod
    def is_time_between(check_time: time, start_time: time, end_time: time) -> bool:
        """Check if time is between start and end times"""
        if not all([check_time, start_time, end_time]):
            return False
        
        # Handle overnight ranges
        if end_time < start_time:
            return check_time >= start_time or check_time <= end_time
        else:
            return start_time <= check_time <= end_time
    
    @staticmethod
    def time_to_minutes(time_obj: time) -> int:
        """Convert time to total minutes from midnight"""
        if not time_obj:
            return 0
        return time_obj.hour * 60 + time_obj.minute
