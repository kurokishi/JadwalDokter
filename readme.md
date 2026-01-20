aplikasi generate jadwal dokter


jadwal_dokter/
├── run.py
├── requirements.txt
├── runtime.txt
├── .streamlit/
│   └── config.toml
└── app/
    ├── __init__.py
    ├── config.py
    ├── main.py
    ├── utils.py
    ├── utils/
    │   ├── __init__.py
    │   ├── parser.py
    │   ├── cleaner.py
    │   ├── time_parser.py
    │   ├── validator.py
    │   └── template_parser.py
    ├── core/
    │   ├── __init__.py
    │   └── data_manager.py
    └── ui/
        ├── __init__.py
        ├── home.py
        ├── tab_upload.py
        ├── tab_schedule.py
        ├── tab_kanban_drag.py
        ├── tab_preferences.py
        └── tab_about.py
