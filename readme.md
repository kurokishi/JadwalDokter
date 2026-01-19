aplikasi generate jadwal dokter


JadwalDokter/                 (ROOT DIRECTORY)
├── run.py                    # File baru untuk menjalankan aplikasi
├── requirements.txt          # File requirements
├── app/                      # Package utama
│   ├── __init__.py
│   ├── config.py            # Dipindahkan ke sini
│   ├── main.py              # Dipindahkan ke sini
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scheduler.py
│   │   ├── cleaner.py
│   │   ├── time_parser.py
│   │   ├── excel_writer.py
│   │   ├── analyzer.py
│   │   ├── template_parser.py
│   │   └── validator.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   ├── tab_upload.py
│   │   ├── tab_analyzer.py
│   │   ├── tab_visualization.py
│   │   ├── tab_kanban_drag.py
│   │   └── tab_settings.py
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py
│       └── loggers.py
