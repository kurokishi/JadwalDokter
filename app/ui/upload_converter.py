"""
Upload and conversion UI
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import traceback

from app.core.hafis_parser import HafisParser
from app.core.grid_converter import GridConverter
from app.core.data_validator import DataValidator
from app.utils import init_session_state, validate_excel_file, format_file_size, clean_dataframe, get_unique_sorted


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
                
                if parsed_data and len(parsed_data) > 0:
                    # Show parsed data preview
                    with st.expander("📋 Preview Data Parsed", expanded=False):
                        df_parsed = pd.DataFrame(parsed_data)
                        df_parsed_clean = clean_dataframe(df_parsed)
                        st.dataframe(df_parsed_clean.head(20))
                    
                    # Convert to grid format
                    converter = GridConverter()
                    grid_df = converter.convert_to_grid(parsed_data)
                    
                    if not grid_df.empty:
                        # Clean the grid DataFrame
                        grid_df = clean_dataframe(grid_df)
                        
                        # Save to session state
                        st.session_state.parsed_data = parsed_data
                        st.session_state.grid_data = grid_df
                        st.session_state.file_name = uploaded_file.name
                        st.session_state.upload_time = datetime.now()
                        
                        # Show success message
                        st.success(f"✅ Berhasil mengkonversi {len(parsed_data)} data jadwal")
                        
                        # Show grid preview
                        show_grid_preview(grid_df)
                        
                        # Show statistics
                        show_conversion_stats(parsed_data, grid_df)
                        
                    else:
                        st.warning("⚠️ Tidak ada data yang bisa dikonversi ke format grid")
                        st.info("""
                        **Kemungkinan penyebab:**
                        1. Format file tidak sesuai dengan yang diharapkan
                        2. Data jadwal tidak ditemukan dalam file
                        3. Waktu jadwal tidak valid
                        """)
                
                else:
                    st.warning("⚠️ Tidak ada data jadwal yang ditemukan dalam file")
                    st.info("""
                    **Tips:**
                    - Pastikan file memiliki format yang benar
                    - Cek apakah ada data di sheet pertama
                    - Format harus sesuai dengan template jadwal_hafis.xlsx
                    """)
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                
                # Show detailed error for debugging
                with st.expander("🔍 Detail Error", expanded=False):
                    st.code(traceback.format_exc())
                
                st.info("""
                **Solusi:**
                1. Cek format file Excel Anda
                2. Pastikan file tidak corrupt
                3. Coba gunakan template yang disediakan
                """)
    
    else:
        # Show instructions when no file uploaded
        show_upload_instructions()


def show_grid_preview(grid_df: pd.DataFrame):
    """Display grid data preview"""
    st.markdown("### 📊 Preview Hasil Konversi")
    
    # Filter options - SAFE VERSION using utility functions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Use utility function for safe sorting
        poli_options = get_unique_sorted(grid_df['POLI'])
        selected_poli = st.selectbox("Filter POLI", poli_options)
    
    with col2:
        jenis_options = get_unique_sorted(grid_df['JENIS'])
        selected_jenis = st.selectbox("Filter JENIS", jenis_options)
    
    with col3:
        hari_options = get_unique_sorted(grid_df['HARI'])
        selected_hari = st.selectbox("Filter HARI", hari_options)
    
    with col4:
        dokter_options = get_unique_sorted(grid_df['DOKTER'])
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
    if not filtered_df.empty:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
        
        # Show filter stats
        st.caption(f"Menampilkan {len(filtered_df)} dari {len(grid_df)} jadwal")
    else:
        st.info("Tidak ada data yang sesuai dengan filter")
    
    # Data validation
    st.markdown("### 🔍 Validasi Data")
    
    validator = DataValidator()
    is_valid, messages = validator.validate_grid_data(grid_df)
    
    if is_valid:
        st.success("✅ Data grid valid")
    else:
        # Show errors and warnings
        if messages:
            with st.expander("📋 Detail Validasi", expanded=True):
                for i, msg in enumerate(messages):
                    if i < len(validator.errors):
                        st.error(f"❌ {msg}")
                    else:
                        st.warning(f"⚠️ {msg}")
        
        # Show validation summary
        summary = validator.get_validation_summary(grid_df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "Valid" if is_valid else "Invalid")
        with col2:
            st.metric("Errors", summary['total_errors'])
        with col3:
            st.metric("Warnings", summary['total_warnings'])


def show_conversion_stats(parsed_data: list, grid_df: pd.DataFrame):
    """Display conversion statistics"""
    st.markdown("### 📈 Statistik Konversi")
    
    # Get summary from converter
    converter = GridConverter()
    summary = converter.get_grid_summary(grid_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Data Parsed", len(parsed_data))
    
    with col2:
        st.metric("Total Grid Rows", summary['total_rows'])
    
    with col3:
        st.metric("Dokter Unik", summary['total_doctors'])
    
    with col4:
        st.metric("Poli Unik", summary['total_poli'])
    
    # Detailed stats
    with st.expander("📊 Detail Statistik", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Distribusi Jenis:**")
            if summary['reguler_count'] > 0 or summary['eksekutif_count'] > 0:
                jenis_data = pd.DataFrame({
                    'Jenis': ['Reguler', 'Eksekutif'],
                    'Count': [summary['reguler_count'], summary['eksekutif_count']]
                })
                st.dataframe(jenis_data, use_container_width=True)
            else:
                st.info("Tidak ada data jenis")
        
        with col2:
            st.markdown("**Distribusi Hari:**")
            if summary['days_distribution']:
                hari_data = pd.DataFrame(
                    list(summary['days_distribution'].items()),
                    columns=['Hari', 'Count']
                )
                # Sort by day order
                day_order = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
                hari_data['Hari'] = pd.Categorical(hari_data['Hari'], categories=day_order, ordered=True)
                hari_data = hari_data.sort_values('Hari')
                st.dataframe(hari_data, use_container_width=True)
            else:
                st.info("Tidak ada data hari")


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
    
    **Jika mengalami error:**
    - Pastikan format file sesuai contoh
    - Coba download template dari halaman Home
    - Hubungi administrator jika masalah berlanjut
    """)
    
    # Template download
    st.markdown("### 📥 Template File")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Struktur template:**
        - Kolom A: KSM (Kelompok Staf Medis)
        - Kolom B: Nama Dokter
        - Kolom C: Tipe (JAM KERJA/REGULER/EKSEKUTIF)
        - Kolom D-I: Hari (Senin-Sabtu)
        """)
    
    with col2:
        # Placeholder for template download button
        # In actual implementation, load template from file
        st.download_button(
            label="Download Template",
            data="",  # Placeholder - actual template should be loaded from file
            file_name="jadwal_hafis_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            disabled=True  # Disable until actual template is available
        )
