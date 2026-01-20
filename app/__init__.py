"""
Package UI - komponen Streamlit untuk aplikasi Jadwal Dokter
"""

from .home import render as render_home
from .tab_upload import render as render_upload
from .tab_schedule import render as render_schedule
from .tab_kanban_drag import render as render_kanban
from .tab_preferences import render as render_preferences
from .tab_about import render as render_about

__all__ = [
    'render_home',
    'render_upload', 
    'render_schedule',
    'render_kanban',
    'render_preferences',
    'render_about'
]
