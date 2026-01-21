"""
Entry point untuk aplikasi Jadwal Dokter
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
        st.info("Please check the error details above.")

if __name__ == "__main__":
    main()
