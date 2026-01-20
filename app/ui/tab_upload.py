"""
Tab untuk upload dan validasi data
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from ..config import config
from ..utils import show_message, create_download_link, validate_dataframe
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
                st.session_state['validation_errors'] = errors
                
                # Extract unique values
                unique_values = cleaner.extract_unique_values(df_clean)
                st.session_state['doctors_list'] = unique_values.get('doctors', [])
                st.session_state['specializations'] = unique_values.get('specializations', [])
                
                # Calculate summary
                summary = cleaner.calculate_schedule_summary(df_clean)
                st.session_state['schedule_summary'] = summary
                
            except Exception as e:
                st.error(f"❌ Error membaca file: {str(e)}")
                st.code(str(e))
    
    with col2:
        st.subheader("📋 Panduan Upload")
        
        st.markdown("""
        ### Format Data yang Didukung:
        
        **File:**
        - Excel (.xlsx, .xls)
        - CSV (.csv)
        
        **Kolom Wajib:**
        1. `nama_dokter` - Nama dokter
        2. `spesialisasi` - Spesialisasi dokter
        3. `hari` - Hari praktik
        4. `jam_mulai` - Waktu mulai
        5. `jam_selesai` - Waktu selesai
        
        **Kolom Opsional:**
        - `ruangan` - Nomor ruangan
        - `poliklinik` - Nama poliklinik
        - `kapasitas` - Kapasitas pasien
        - `catatan` - Catatan tambahan
        """)
        
        st.markdown("---")
        
        # Download template
        st.subheader("📥 Download Template")
        
        template_type = st.selectbox(
            "Pilih jenis template",
            ["standard", "simple"],
            help="Standard: lengkap dengan semua kolom. Simple: hanya kolom utama."
        )
        
        if st.button("⬇️ Download Template", use_container_width=True):
            template_parser = TemplateParser()
            sample_df = template_parser.create_sample_template(template_type)
            
            # Convert to CSV
            csv = sample_df.to_csv(index=False)
            
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"template_jadwal_{template_type}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Quick actions jika ada data
        if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
            st.subheader("⚡ Aksi Cepat")
            
            df = st.session_state.uploaded_data
            
            # Download data yang sudah diupload
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 Download Data",
                data=csv,
                file_name="jadwal_dokter_cleaned.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Lihat statistik
            if st.button("📈 Lihat Statistik", use_container_width=True):
                if 'schedule_summary' in st.session_state:
                    summary = st.session_state.schedule_summary
                    
                    st.info("📊 **Statistik Data**")
                    st.metric("Total Jadwal", summary.get('total_schedules', 0))
                    st.metric("Total Dokter", summary.get('total_doctors', 0))
                    st.metric("Total Jam Kerja", f"{summary.get('total_hours', 0):.1f} jam")
                    
                    # Tampilkan summary per hari
                    st.subheader("📅 Summary per Hari")
                    for day, day_summary in summary.get('daily_summary', {}).items():
                        st.markdown(f"**{day}:** {day_summary['schedules']} jadwal, {day_summary['hours']} jam")
    
    # Validasi detail jika ada data
    if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Validasi Data")
            
            validator = DataValidator()
            df = st.session_state.uploaded_data
            validation_summary = validator.get_validation_summary(df)
            
            # Tampilkan score
            score = validation_summary.get('data_quality_score', 0)
            score_color = "green" if score >= 80 else "orange" if score >= 60 else "red"
            
            st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
                    <h3 style="color: {score_color}; margin: 0;">Skor Kualitas Data</h3>
                    <h1 style="color: {score_color}; margin: 10px 0;">{score}/100</h1>
                    <p style="color: #666;">
                        {validation_summary['total_rows']} baris × {validation_summary['total_columns']} kolom
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("⚠️ Issues")
            
            errors = validation_summary.get('errors', [])
            if errors:
                st.warning(f"Terdapat {len(errors)} masalah yang terdeteksi:")
                
                # Tampilkan maksimal 5 error
                for error in errors[:5]:
                    st.markdown(f"- {error}")
                
                if len(errors) > 5:
                    st.markdown(f"... dan {len(errors) - 5} masalah lainnya")
            else:
                st.success("✅ Tidak ada masalah yang terdeteksi")
                
                # Tampilkan rekomendasi
                st.info("**💡 Rekomendasi:** Data sudah bersih dan siap untuk diproses lebih lanjut di tab **📅 Jadwal**")
