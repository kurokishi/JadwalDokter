"""
Upload and conversion UI
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from app.core.hafis_parser import HafisParser
from app.core.grid_converter import GridConverter
from app.core.data_validator import DataValidator
from app.utils import init_session_state, validate_excel_file, format_file_size


def show_upload_converter():
    """Display upload and conversion page"""
    
    # Initialize session state
    init_session_state()
    
    # Page header
    st.title("🔄 Upload & Konversi Jadwal")
    
    # File upload section
    st.markdown("### 📤 Upload File Jadwal")
    
    uploaded_file = st.file_uploader(
        "Pilih file jadwal_hafis.xlsx",
        type=['xlsx', 'xls'],
        help="Upload file Excel dengan format jadwal_hafis.xlsx"
    )
    
    if uploaded_file is not None:
        # Validate file
        is_valid, message = validate_excel_file(uploaded_file)
        
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 File", uploaded_file.name)
        with col2:
            st.metric("📊 Size", format_file_size(uploaded_file.size))
        with col3:
            st.metric("🕐 Upload", datetime.now().strftime("%H:%M"))
        
        # Process file
        with st.spinner("🔄 Memproses file..."):
            try:
                # Parse the file
                parser = HafisParser()
                parsed_data = parser.parse_file(uploaded_file)
                
                if parsed_data:
                    # Show parsed data preview
                    with st.expander("📋 Preview Data Parsed", expanded=False):
                        df_parsed = pd.DataFrame(parsed_data)
                        st.dataframe(df_parsed.head(20))
                    
                    # Convert to grid format
                    converter = GridConverter()
                    grid_df = converter.convert_to_grid(parsed_data)
                    
                    if not grid_df.empty:
                        # Save to session state
                        st.session_state.parsed_data = parsed_data
                        st.session_state.grid_data = grid_df
                        st.session_state.file_name = uploaded_file.name
                        
                        # Show success message
                        st.success(f"✅ Berhasil mengkonversi {len(parsed_data)} data jadwal")
                        
                        # Show grid preview
                        show_grid_preview(grid_df)
                        
                        # Show statistics
                        show_conversion_stats(parsed_data, grid_df)
                        
                    else:
                        st.warning("⚠️ Tidak ada data yang bisa dikonversi ke format grid")
                
                else:
                    st.warning("⚠️ Tidak ada data jadwal yang ditemukan dalam file")
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.exception(e)
    
    else:
        # Show instructions when no file uploaded
        show_upload_instructions()


def show_grid_preview(grid_df: pd.DataFrame):
    """Display grid data preview"""
    st.markdown("### 📊 Preview Hasil Konversi")
    
    # Filter options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        poli_options = ['Semua'] + sorted(grid_df['POLI'].unique().tolist())
        selected_poli = st.selectbox("Filter POLI", poli_options)
    
    with col2:
        jenis_options = ['Semua'] + sorted(grid_df['JENIS'].unique().tolist())
        selected_jenis = st.selectbox("Filter JENIS", jenis_options)
    
    with col3:
        hari_options = ['Semua'] + sorted(grid_df['HARI'].unique().tolist())
        selected_hari = st.selectbox("Filter HARI", hari_options)
    
    with col4:
        dokter_options = ['Semua'] + sorted(grid_df['DOKTER'].unique().tolist())
        selected_dokter = st.selectbox("Filter DOKTER", dokter_options)
    
    # Apply filters
    filtered_df = grid_df.copy()
    
    if selected_poli != 'Semua':
        filtered_df = filtered_df[filtered_df['POLI'] == selected_poli]
    
    if selected_jenis != 'Semua':
        filtered_df = filtered_df[filtered_df['JENIS'] == selected_jenis]
    
    if selected_hari != 'Semua':
        filtered_df = filtered_df[filtered_df['HARI'] == selected_hari]
    
    if selected_dokter != 'Semua':
        filtered_df = filtered_df[filtered_df['DOKTER'] == selected_dokter]
    
    # Display filtered data
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )
    
    # Data validation
    validator = DataValidator()
    is_valid, messages = validator.validate_grid_data(grid_df)
    
    if is_valid:
        st.success("✅ Data grid valid")
    else:
        st.warning(f"⚠️ Ada masalah dengan data: {messages[0] if messages else 'Unknown error'}")


def show_conversion_stats(parsed_data: list, grid_df: pd.DataFrame):
    """Display conversion statistics"""
    st.markdown("### 📈 Statistik Konversi")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Data Parsed", len(parsed_data))
    
    with col2:
        st.metric("Total Grid Rows", len(grid_df))
    
    with col3:
        unique_doctors = grid_df['DOKTER'].nunique()
        st.metric("Dokter Unik", unique_doctors)
    
    with col4:
        unique_poli = grid_df['POLI'].nunique()
        st.metric("Poli Unik", unique_poli)
    
    # Detailed stats
    with st.expander("📊 Detail Statistik", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Distribusi Jenis:**")
            jenis_dist = grid_df['JENIS'].value_counts()
            st.dataframe(jenis_dist)
        
        with col2:
            st.markdown("**Distribusi Hari:**")
            hari_dist = grid_df['HARI'].value_counts()
            st.dataframe(hari_dist)


def show_upload_instructions():
    """Show upload instructions"""
    st.info("""
    ### ℹ️ Instruksi Upload
    
    1. **Siapkan file** `jadwal_hafis.xlsx` Anda
    2. **Klik area upload** di atas atau drag & drop file
    3. **Tunggu proses** parsing dan konversi otomatis
    4. **Download hasil** dalam format Excel yang rapi
    
    **Format file yang didukung:**
    - Excel (.xlsx, .xls)
    - Maksimal ukuran: 10MB
    - Format: jadwal_hafis.xlsx (dengan formula Excel)
    
    **Contoh struktur file:**
    ```
    | KSM | Nama Dokter | POLI | SENIN | SELASA | ...
    |-----|-------------|------|-------|--------|-----
    | Anak| dr. Debby...| JAM KERJA | 07:30-14:00 | ...
    |     |             | REGULER | =[1]ANAK!T4 | ...
    |     |             | EKSEKUTIF | 10.30-11.25 | ...
    ```
    """)
