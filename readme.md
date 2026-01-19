aplikasi generate jadwal dokter


JadwalDokter/
├── run.py                          # Entry point
├── requirements.txt                # Dependencies
├── runtime.txt                     # Python version
├── .streamlit/
│   └── config.toml                # Streamlit config
│
└── app/                           # Main package
    ├── __init__.py                # Package exports
    ├── config.py                  # App configuration
    ├── main.py                    # Main Streamlit app
    ├── utils.py                   # Utility functions
    │
    ├── core/                      # Business logic
    │   ├── __init__.py
    │   ├── cleaner.py            # Data cleaning
    │   ├── parser.py             # Schedule parsing
    │   ├── time_parser.py        # Time utilities
    │   ├── validator.py          # Data validation
    │   └── template_parser.py    # Template parsing
    │
    └── ui/                        # UI components
        ├── __init__.py
        ├── home.py               # Home page
        ├── tab_upload.py         # Upload tab
        ├── tab_schedule.py       # Schedule tab
        ├── tab_kanban_drag.py    # Kanban drag tab (simplified)
        ├── tab_preferences.py    # Preferences tab
        └── tab_about.py          # About tab
