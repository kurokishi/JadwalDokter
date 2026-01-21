"""
Jadwal Dokter Converter Package
"""
__version__ = "2.0.0"
__author__ = "Jadwal Dokter Team"

from .config import AppConfig
from .utils import init_session_state

# Export main components
__all__ = ['AppConfig', 'init_session_state', '__version__']
