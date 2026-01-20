"""
Entry point untuk aplikasi Jadwal Dokter.
Jalankan dengan: streamlit run run.py
"""

import sys
import os

# Tambahkan current directory ke path Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import dan jalankan aplikasi
from app.main import main

if __name__ == "__main__":
    main()
