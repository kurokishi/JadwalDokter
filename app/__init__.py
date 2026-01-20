"""
Package utama aplikasi Jadwal Dokter
"""

__version__ = "1.0.0"
__author__ = "Tim Pengembang"

# Ekspor modul utama
from . import config
from . import main
from . import utils

# Ekspor dari core
from .core import (
    DataCleaner,
    ScheduleParser,
    TimeParser,
    DataValidator,
    TemplateParser
)

# Ekspor dari ui
from .ui import (
    render_home,
    render_upload,
    render_schedule,
    render_kanban,
    render_preferences,
    render_about
)

__all__ = [
    # Module
    'config',
    'main',
    'utils',
    
    # Core classes
    'DataCleaner',
    'ScheduleParser',
    'TimeParser',
    'DataValidator',
    'TemplateParser',
    
    # UI functions
    'render_home',
    'render_upload',
    'render_schedule',
    'render_kanban',
    'render_preferences',
    'render_about'
]
