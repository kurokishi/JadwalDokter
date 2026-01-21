aplikasi generate jadwal dokter


JadwalDokter/
├── run.py
├── requirements.txt
├── runtime.txt
├── .streamlit/
│   └── config.toml
├── templates/
│   └── jadwal_template.xlsx  # Template untuk hasil
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── utils.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── hafis_parser.py      # Parser khusus jadwal_hafis.xlsx
│   │   ├── grid_converter.py    # Konversi ke format grid
│   │   ├── time_slot_builder.py # Bangun time slots
│   │   └── excel_generator.py   # Generate jadwal_hasil.xlsx
│   └── ui/
│       ├── __init__.py
│       ├── home.py
│       ├── upload_converter.py  # Upload + Convert tab
│       ├── schedule_viewer.py   # View hasil
│       ├── export_manager.py    # Export ke Excel
│       └── about.py
