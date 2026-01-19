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
from .core.cleaner import DataCleaner
from .core.parser import ScheduleParser
from .core.time_parser import TimeParser
from .core.validator import DataValidator
from .core.template_parser import TemplateParser

# Ekspor dari ui
from .ui.home import render as render_home
from .ui.tab_upload import render as render_upload
from .ui.tab_schedule import render as render_schedule
from .ui.tab_kanban_drag import render as render_kanban
from .ui.tab_preferences import render as render_preferences
from .ui.tab_about import render as render_about

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
