"""
Modul untuk parsing jadwal dokter
"""
import pandas as pd
import numpy as np
from datetime import datetime, time, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re
from ..config import config, TimeSlot
from ..utils import parse_time, calculate_duration
from .template_parser import TemplateParser

class ScheduleParser:
    """Class untuk parsing dan transformasi data jadwal"""
    
    def __init__(self):
        self.template_parser = TemplateParser()
    
    def parse_schedule_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse data jadwal ke dalam format yang terstruktur"""
        parsed_data = {
            'schedules': [],
            'doctors': {},
            'days': {},
            'time_slots': [],
            'conflicts': [],
            'statistics': {}
        }
        
        if df.empty:
            return parsed_data
        
        # Parse setiap baris
        schedules = []
        for idx, row in df.iterrows():
            schedule = self._parse_schedule_row(row, idx)
            if schedule:
                schedules.append(schedule)
        
        parsed_data['schedules'] = schedules
        
        # Generate struktur data terorganisir
        parsed_data.update(self._organize_schedules(schedules))
        
        # Generate time slots
        parsed_data['time_slots'] = self._generate_time_slots(schedules)
        
        # Deteksi konflik
        parsed_data['conflicts'] = self._detect_conflicts(schedules)
        
        # Hitung statistik
        parsed_data['statistics'] = self._calculate_statistics(parsed_data)
        
        return parsed_data
    
    def _parse_schedule_row(self, row: pd.Series, row_id: int) -> Optional[Dict[str, Any]]:
        """Parse satu baris data jadwal"""
        try:
            # Dapatkan data dasar
            doctor = str(row.get('nama_dokter', '')).strip()
            specialization = str(row.get('spesialisasi', '')).strip()
            day = str(row.get('hari', '')).strip()
            start_time_str = str(row.get('jam_mulai', ''))
            end_time_str = str(row.get('jam_selesai', ''))
            
            # Validasi data wajib
            if not doctor or not day or not start_time_str or not end_time_str:
                return None
            
            # Parse waktu
            start_time = parse_time(start_time_str)
            end_time = parse_time(end_time_str)
            
            if not start_time or not end_time:
                return None
            
            # Buat schedule object
            schedule = {
                'id': row_id,
                'doctor': doctor.title(),
                'specialization': specialization.title(),
                'day': day.title(),
                'start_time': start_time,
                'end_time': end_time,
                'start_str': start_time.strftime("%H:%M"),
                'end_str': end_time.strftime("%H:%M"),
                'duration': calculate_duration(start_time, end_time),
                'room': str(row.get('ruangan', '')).title(),
                'clinic': str(row.get('poliklinik', '')).title(),
                'capacity': row.get('kapasitas', None),
                'notes': str(row.get('catatan', '')).strip()
            }
            
            # Generate unique ID
            schedule['uid'] = f"{schedule['doctor']}_{schedule['day']}_{schedule['start_str']}"
            
            return schedule
        except Exception as e:
            print(f"Error parsing row {row_id}: {e}")
            return None
    
    def _organize_schedules(self, schedules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Organisasi jadwal berdasarkan dokter dan hari"""
        organized = {
            'doctors': {},
            'days': {},
            'by_doctor_day': {}
        }
        
        for schedule in schedules:
            doctor = schedule['doctor']
            day = schedule['day']
            
            # Organize by doctor
            if doctor not in organized['doctors']:
                organized['doctors'][doctor] = {
                    'specialization': schedule['specialization'],
                    'total_hours': 0,
                    'days': set(),
                    'schedules': []
                }
            
            organized['doctors'][doctor]['schedules'].append(schedule)
            organized['doctors'][doctor]['days'].add(day)
            organized['doctors'][doctor]['total_hours'] += schedule['duration']
            
            # Organize by day
            if day not in organized['days']:
                organized['days'][day] = {
                    'doctors': set(),
                    'total_hours': 0,
                    'schedules': []
                }
            
            organized['days'][day]['schedules'].append(schedule)
            organized['days'][day]['doctors'].add(doctor)
            organized['days'][day]['total_hours'] += schedule['duration']
            
            # Organize by doctor and day
            key = f"{doctor}_{day}"
            if key not in organized['by_doctor_day']:
                organized['by_doctor_day'][key] = []
            
            organized['by_doctor_day'][key].append(schedule)
        
        return organized
    
    def _generate_time_slots(self, schedules: List[Dict[str, Any]]) -> List[TimeSlot]:
        """Generate time slots dari semua jadwal"""
        time_slots = []
        
        for schedule in schedules:
            # Create TimeSlot object
            slot = TimeSlot(
                start=schedule['start_time'],
                end=schedule['end_time'],
                day=schedule['day'],
                doctor=schedule['doctor'],
                specialization=schedule['specialization']
            )
            time_slots.append(slot)
        
        return time_slots
    
    def _detect_conflicts(self, schedules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deteksi konflik jadwal"""
        conflicts = []
        
        # Group by doctor and day
        doctor_day_schedules = {}
        for schedule in schedules:
            key = (schedule['doctor'], schedule['day'])
            if key not in doctor_day_schedules:
                doctor_day_schedules[key] = []
            doctor_day_schedules[key].append(schedule)
        
        # Check for overlaps for each doctor on each day
        for (doctor, day), doc_schedules in doctor_day_schedules.items():
            if len(doc_schedules) > 1:
                # Sort by start time
                doc_schedules.sort(key=lambda x: x['start_time'])
                
                # Check for overlaps
                for i in range(len(doc_schedules) - 1):
                    current = doc_schedules[i]
                    next_schedule = doc_schedules[i + 1]
                    
                    if current['end_time'] > next_schedule['start_time']:
                        conflict = {
                            'doctor': doctor,
                            'day': day,
                            'schedule1': current,
                            'schedule2': next_schedule,
                            'overlap_minutes': self._calculate_overlap(
                                current['start_time'], current['end_time'],
                                next_schedule['start_time'], next_schedule['end_time']
                            )
                        }
                        conflicts.append(conflict)
        
        return conflicts
    
    def _calculate_overlap(self, start1: time, end1: time, start2: time, end2: time) -> int:
        """Hitung overlap dalam menit"""
        start1_min = start1.hour * 60 + start1.minute
        end1_min = end1.hour * 60 + end1.minute
        start2_min = start2.hour * 60 + start2.minute
        end2_min = end2.hour * 60 + end2.minute
        
        overlap_start = max(start1_min, start2_min)
        overlap_end = min(end1_min, end2_min)
        
        return max(0, overlap_end - overlap_start)
    
    def _calculate_statistics(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hitung statistik dari data yang di-parse"""
        stats = {
            'total_schedules': len(parsed_data['schedules']),
            'total_doctors': len(parsed_data.get('doctors', {})),
            'total_days': len(parsed_data.get('days', {})),
            'total_conflicts': len(parsed_data.get('conflicts', [])),
            'total_hours': 0,
            'avg_hours_per_doctor': 0,
            'avg_hours_per_day': 0
        }
        
        # Hitung total jam
        total_hours = 0
        for schedule in parsed_data['schedules']:
            total_hours += schedule['duration']
        
        stats['total_hours'] = round(total_hours, 2)
        
        # Hitung rata-rata
        if stats['total_doctors'] > 0:
            stats['avg_hours_per_doctor'] = round(total_hours / stats['total_doctors'], 2)
        
        if stats['total_days'] > 0:
            stats['avg_hours_per_day'] = round(total_hours / stats['total_days'], 2)
        
        return stats
    
    def create_schedule_table(self, parsed_data: Dict[str, Any]) -> pd.DataFrame:
        """Buat DataFrame dari data yang di-parse"""
        rows = []
        
        for schedule in parsed_data['schedules']:
            row = {
                'ID': schedule['id'],
                'Dokter': schedule['doctor'],
                'Spesialisasi': schedule['specialization'],
                'Hari': schedule['day'],
                'Mulai': schedule['start_str'],
                'Selesai': schedule['end_str'],
                'Durasi (jam)': schedule['duration'],
                'Ruangan': schedule.get('room', ''),
                'Poliklinik': schedule.get('clinic', ''),
                'Kapasitas': schedule.get('capacity', ''),
                'Catatan': schedule.get('notes', '')
            }
            rows.append(row)
        
        return pd.DataFrame(rows)
