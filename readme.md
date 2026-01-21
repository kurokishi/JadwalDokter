aplikasi generate jadwal dokter


JadwalDokterConverter/
├── run.py                              # ENTRY POINT
├── requirements.txt                    # DEPENDENCIES
├── runtime.txt                         # PYTHON VERSION
├── .streamlit/
│   └── config.toml                     # STREAMLIT CONFIG
├── templates/
│   └── jadwal_hafis_template.xlsx     # TEMPLATE FILE
└── app/
    ├── __init__.py                     # PACKAGE INIT
    ├── config.py                       # APP CONFIG
    ├── main.py                         # MAIN APP
    ├── utils.py                        # UTILITY FUNCTIONS
    ├── core/
    │   ├── __init__.py
    │   ├── hafis_parser.py
    │   ├── grid_converter.py
    │   ├── time_slot_builder.py
    │   ├── excel_generator.py
    │   └── data_validator.py
    └── ui/
        ├── __init__.py
        ├── home.py
        ├── upload_converter.py
        ├── schedule_viewer.py
        ├── export_manager.py
        └── about.py
