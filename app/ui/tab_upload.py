"""
Tab untuk upload dan validasi data
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from ..config import config
from ..utils import show_message, validate_dataframe, get_unique_values
from ..core import DataValidator, TemplateParser, DataCleaner

def render():
    """Render tab upload"""
    st.header("📤 Upload Data Jadwal")
    
    # Dua kolom utama
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File uploader
        uploaded_file = st.file_uploader(
            "Pilih file Excel atau CSV",
            type=config.ALLOWED_EXTENSIONS,
            help=f"Format yang didukung: {', '.join(config.ALLOWED_EXTENSIONS)}. Maksimum {config.MAX_FILE_SIZE_MB}MB."
        )
        
        if uploaded_file is not None:
            try:
                # Baca file
                file_bytes = uploaded_file.read()
                
                # Validasi ukuran file
                if len(file_bytes) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
                    show_message(f"File terlalu besar. Maksimum {config.MAX_FILE_SIZE_MB}MB", "error")
                    return
                
                # Parse file
                template_parser = TemplateParser()
                df, warnings = template_parser.parse_file(file_bytes, uploaded_file.name)
                
                # Tampilkan warnings jika ada
                if warnings:
                    for warning in warnings:
                        show_message(warning, "warning")
                
                # Validasi data
                validator = DataValidator()
                is_valid, errors = validator.validate_dataframe(df)
                
                if not is_valid:
                    st.error("❌ Data tidak valid!")
                    for error in errors:
                        st.warning(f"⚠️ {error}")
                    
                    # Tampilkan data meski ada error
                    with st.expander("👀 Lihat Data (dengan error)", expanded=False):
                        st.dataframe(df, use_container_width=True)
                    
                    # Simpan errors ke session state
                    st.session_state.validation_errors = errors
                    return
                
                # Clean data
                cleaner = DataCleaner()
                df_clean = cleaner.clean_dataframe(df)
                
                # Tampilkan success message
                show_message("✅ File berhasil diupload dan divalidasi!", "success")
                
                # Tampilkan preview
                st.subheader("📋 Preview Data")
                
                # Tampilkan statistik cepat
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                with stats_col1:
                    st.metric("Jumlah Baris", len(df_clean))
                with stats_col2:
                    st.metric("Jumlah Kolom", len(df_clean.columns))
                with stats_col3:
                    if 'nama_dokter' in df_clean.columns:
                        st.metric("Dokter Unik", df_clean['nama_dokter'].nunique())
                
                # Tampilkan data
                st.dataframe(df_clean.head(20), use_container_width=True)
                
                # Simpan ke session state
                st.session_state['uploaded_data'] = df_clean
                st.session_state['file_name'] = uploaded_file.name
                st.session_state['upload_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state['validation_errors'] = []
                
                # Extract unique values
                unique_values = cleaner.extract_unique_values(df_clean)
                st.session_state['doctors_list'] = unique_values.get('doctors', [])
                st.session_state['specializations'] = unique_values.get('specializations', [])
                
            except Exception as e:
                st.error(f"❌ Error membaca file: {str(e)}")
    
    with col2:
        st.subheader("📋 Pand
