# app/main.py
import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Import yang diperbaiki - tanpa "app." prefix
from config import Config
from core.scheduler import Scheduler
from core.cleaner import DataCleaner
from core.time_parser import TimeParser
from core.excel_writer import ExcelWriter
from ui.sidebar import render_sidebar


def main():
    st.set_page_config(
        page_title="Pengolah Jadwal Poli",
        page_icon="🚀",
        layout="wide"
    )
    
    config = Config()
    render_sidebar(config)

    st.title("🚀 Pengolah Jadwal Poli Modular")
    
    st.markdown("""
    Upload file Excel jadwal dokter untuk diproses. Mendukung:
    - **Format baru (KSM)**: Template dengan kolom JAM KERJA/REGULER/EKSEKUTIF
    - **Format lama**: Sheet Reguler dan Poleks terpisah
    """)

    uploaded = st.file_uploader(
        "Upload Excel",
        type=['xlsx', 'xls'],
        help="Upload file jadwal dokter dalam format Excel"
    )

    if uploaded:
        st.success(f"File terupload: **{uploaded.name}**")
        
        if st.button("🚀 Proses Jadwal", type="primary"):
            with st.spinner("Memproses data... Mohon tunggu"):
                try:
                    parser = TimeParser(
                        start_hour=config.start_hour,
                        start_minute=config.start_minute,
                        interval_minutes=config.interval_minutes
                    )
                    cleaner = DataCleaner()
                    scheduler = Scheduler(parser, cleaner, config)
                    
                    file_bytes = uploaded.getvalue()
                    file_stream = io.BytesIO(file_bytes)
                    
                    grid_df, slot_strings, errors = scheduler.process_dataframe(file_stream)
                    
                    if grid_df is not None and not grid_df.empty:
                        st.session_state["processed_data"] = grid_df
                        st.session_state["slot_strings"] = slot_strings
                        st.session_state["file_bytes"] = file_bytes
                        
                        st.success(f"Data berhasil diproses! ({len(grid_df)} baris, {len(slot_strings)} slot waktu)")
                        
                        if errors:
                            with st.expander(f"⚠️ {len(errors)} peringatan"):
                                for error in errors:
                                    st.write(f"- {error}")
                    else:
                        st.error("Gagal memproses data")
                        if errors:
                            for error in errors:
                                st.error(error)
                                
                except Exception as e:
                    st.error(f"Error saat memproses: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    if "processed_data" in st.session_state and st.session_state["processed_data"] is not None:
        st.divider()
        st.subheader("📊 Hasil Proses")
        
        grid_df = st.session_state["processed_data"]
        slot_strings = st.session_state["slot_strings"]
        
        st.dataframe(grid_df, use_container_width=True)
        
        st.subheader("💾 Download Hasil")
        
        try:
            writer = ExcelWriter(config)
            file_stream = io.BytesIO(st.session_state["file_bytes"])
            output_buffer = writer.write(
                source_file=file_stream,
                df_grid=grid_df,
                slot_str=slot_strings
            )
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"jadwal_hasil_{timestamp}.xlsx"
            
            st.download_button(
                label="📥 Download Excel Hasil",
                data=output_buffer,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Gagal membuat file download: {str(e)}")


if __name__ == "__main__":
    main()
