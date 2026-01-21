"""
Export manager UI
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from app.core.excel_generator import ExcelGenerator
from app.utils import init_session_state, dataframe_to_csv_bytes
from app.config import AppConfig


def show_export_manager():
    """Display export manager page"""
    
    # Initialize session state
    init_session_state()
    
    st.title("💾 Export Data")
    
    # Check if data exists
    if st.session_state.grid_data is None or st.session_state.grid_data.empty:
        st.info("ℹ️ Tidak ada data untuk di-export. Silakan upload dan konversi file terlebih dahulu.")
        
        if st.button("🔄 Ke Halaman Upload"):
            st.session_state['current_page'] = 'upload'
            st.rerun()
        return
    
    grid_df = st.session_state.grid_data
    
    # Export options
    st.markdown("### 📤 Pilihan Export")
    
    # Format selection
    export_format = st.radio(
        "Pilih format export:",
        ["Excel dengan Formatting", "Excel Sederhana", "CSV"],
        horizontal=True
    )
    
    # File name customization
    default_name = f"jadwal_hasil_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    custom_name = st.text_input(
        "Nama file:",
        value=default_name,
        help="Nama file untuk hasil export"
    )
    
    # Add file extension
    if export_format == "CSV":
        file_name = f"{custom_name}.csv"
    else:
        file_name = f"{custom_name}.xlsx"
    
    # Preview before export
    with st.expander("📋 Preview Data Sebelum Export", expanded=False):
        st.dataframe(grid_df.head(20), use_container_width=True)
    
    # Export buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if export_format == "Excel dengan Formatting":
            if st.button("💾 Export Excel dengan Formatting", use_container_width=True, type="primary"):
                with st.spinner("Membuat file Excel dengan formatting..."):
                    try:
                        generator = ExcelGenerator()
                        excel_bytes = generator.generate_excel(grid_df)
                        
                        st.download_button(
                            label="⬇️ Download File Excel",
                            data=excel_bytes,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.success("✅ File Excel siap di-download!")
                    except Exception as e:
                        st.error(f"❌ Error membuat file Excel: {str(e)}")
        
        elif export_format == "Excel Sederhana":
            if st.button("📊 Export Excel Sederhana", use_container_width=True, type="primary"):
                with st.spinner("Membuat file Excel sederhana..."):
                    try:
                        generator = ExcelGenerator()
                        excel_bytes = generator.generate_simple_excel(grid_df)
                        
                        st.download_button(
                            label="⬇️ Download File Excel",
                            data=excel_bytes,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.success("✅ File Excel siap di-download!")
                    except Exception as e:
                        st.error(f"❌ Error membuat file Excel: {str(e)}")
        
        else:  # CSV
            if st.button("📄 Export CSV", use_container_width=True, type="primary"):
                with st.spinner("Membuat file CSV..."):
                    try:
                        csv_bytes = dataframe_to_csv_bytes(grid_df)
                        
                        st.download_button(
                            label="⬇️ Download File CSV",
                            data=csv_bytes,
                            file_name=file_name,
                            mime="text/csv",
                            use_container_width=True
                        )
                        st.success("✅ File CSV siap di-download!")
                    except Exception as e:
                        st.error(f"❌ Error membuat file CSV: {str(e)}")
    
    with col2:
        # Quick export options
        st.markdown("**Export Cepat:**")
        
        quick_col1, quick_col2 = st.columns(2)
        
        with quick_col1:
            if st.button("📅 Jadwal Hari Ini", use_container_width=True):
                today = datetime.now().strftime('%A').upper()
                if today in ['SUNDAY', 'SATURDAY']:
                    today = 'SENIN'  # Default to Monday if weekend
                
                filtered_df = grid_df[grid_df['HARI'] == today]
                
                if not filtered_df.empty:
                    st.session_state.quick_export_data = filtered_df
                    st.success(f"✅ Filtered {len(filtered_df)} schedules for {today}")
                else:
                    st.warning(f"⚠️ Tidak ada jadwal untuk hari {today}")
        
        with quick_col2:
            if st.button("👨‍⚕️ Dokter Terbanyak", use_container_width=True):
                # Find doctor with most schedules
                doctor_counts = grid_df['DOKTER'].value_counts()
                top_doctor = doctor_counts.index[0]
                
                filtered_df = grid_df[grid_df['DOKTER'] == top_doctor]
                
                if not filtered_df.empty:
                    st.session_state.quick_export_data = filtered_df
                    st.success(f"✅ Filtered {len(filtered_df)} schedules for {top_doctor}")
                else:
                    st.warning("⚠️ Tidak bisa menemukan dokter dengan jadwal terbanyak")
    
    # Data filtering for export
    st.markdown("### 🔍 Filter Data untuk Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        poli_filter = st.multiselect(
            "Filter POLI:",
            options=sorted(grid_df['POLI'].unique()),
            help="Pilih POLI untuk di-export"
        )
    
    with col2:
        jenis_filter = st.multiselect(
            "Filter JENIS:",
            options=sorted(grid_df['JENIS'].unique()),
            help="Pilih jenis jadwal untuk di-export"
        )
    
    with col3:
        hari_filter = st.multiselect(
            "Filter HARI:",
            options=sorted(grid_df['HARI'].unique()),
            help="Pilih hari untuk di-export"
        )
    
    # Apply filters
    filtered_export_df = grid_df.copy()
    
    if poli_filter:
        filtered_export_df = filtered_export_df[filtered_export_df['POLI'].isin(poli_filter)]
    
    if jenis_filter:
        filtered_export_df = filtered_export_df[filtered_export_df['JENIS'].isin(jenis_filter)]
    
    if hari_filter:
        filtered_export_df = filtered_export_df[filtered_export_df['HARI'].isin(hari_filter)]
    
    # Show filtered data stats
    st.markdown(f"**Data yang akan di-export:** {len(filtered_export_df)} dari {len(grid_df)} jadwal")
    
    # Export filtered data
    if len(filtered_export_df) < len(grid_df):
        filtered_name = f"{custom_name}_filtered"
        
        if export_format == "CSV":
            filtered_file_name = f"{filtered_name}.csv"
        else:
            filtered_file_name = f"{filtered_name}.xlsx"
        
        if st.button("💾 Export Data Terfilter", use_container_width=True):
            with st.spinner("Membuat file export..."):
                try:
                    if export_format == "Excel dengan Formatting":
                        generator = ExcelGenerator()
                        excel_bytes = generator.generate_excel(filtered_export_df)
                        
                        st.download_button(
                            label=f"⬇️ Download {filtered_file_name}",
                            data=excel_bytes,
                            file_name=filtered_file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    elif export_format == "Excel Sederhana":
                        generator = ExcelGenerator()
                        excel_bytes = generator.generate_simple_excel(filtered_export_df)
                        
                        st.download_button(
                            label=f"⬇️ Download {filtered_file_name}",
                            data=excel_bytes,
                            file_name=filtered_file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:  # CSV
                        csv_bytes = dataframe_to_csv_bytes(filtered_export_df)
                        
                        st.download_button(
                            label=f"⬇️ Download {filtered_file_name}",
                            data=csv_bytes,
                            file_name=filtered_file_name,
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    st.success(f"✅ File {filtered_file_name} siap di-download!")
                except Exception as e:
                    st.error(f"❌ Error membuat file: {str(e)}")
    
    # Data statistics
    st.markdown("### 📊 Statistik Data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Data", len(grid_df))
    
    with col2:
        st.metric("Total Dokter", grid_df['DOKTER'].nunique())
    
    with col3:
        st.metric("Total Poli", grid_df['POLI'].nunique())
    
    with col4:
        st.metric("File Source", st.session_state.get('file_name', 'N/A'))
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #6B7280;'>
    <p><strong>Jadwal Dokter Converter v{AppConfig().VERSION}</strong></p>
    <p>Export terakhir: {datetime.now().strftime('%d %B %Y %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)
