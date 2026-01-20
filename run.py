"""
Entry point untuk aplikasi Jadwal Dokter dengan support file jadwal_hafis.xlsx
"""
import sys
import os
import streamlit as st

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Import app
        from app.main import main as app_main
        
        # Run the app
        app_main()
        
    except Exception as e:
        st.error(f"❌ Error starting application: {str(e)}")
        st.info("""
        **Troubleshooting:**
        1. Pastikan semua file berada di struktur yang benar
        2. Install requirements: `pip install -r requirements.txt`
        3. Untuk file jadwal_hafis.xlsx, pastikan format sesuai
        """)

if __name__ == "__main__":
    main()
