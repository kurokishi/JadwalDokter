"""
UI components module
"""
from app.ui.home import display_home_tab
from app.ui.tab_upload import display_upload_tab
from app.ui.tab_schedule import display_schedule_tab
from app.ui.tab_kanban_drag import display_kanban_tab
from app.ui.tab_preferences import display_preferences_tab
from app.ui.tab_about import display_about_tab

__all__ = [
    'display_home_tab',
    'display_upload_tab',
    'display_schedule_tab',
    'display_kanban_tab',
    'display_preferences_tab',
    'display_about_tab'
]
