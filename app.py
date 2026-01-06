import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time
import io
import json

# Konfigurasi halaman
st.set_page_config(
    page_title="Jadwal Dokter RS",
    page_icon="🏥",
    layout="wide"
)

# Inisialisasi session state
if 'jadwal_data' not in st.session_state:
    st.session_state.jadwal_data = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Fungsi helper yang lebih sederhana
def parse_time_range(time_str):
    """Parse waktu dari format 07.30-14.00 atau 07:30-14:00"""
    if not time_str or str(time_str).strip() in ['', '-', 'nan', 'None']:
        return []
    
    time_str = str(time_str).replace('.', ':')
    
    # Handle multiple ranges
    ranges = []
    for part in time_str.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = part.split('-')
                start = start.strip()
                end = end.strip()
                ranges.append(f"{start}-{end}")
            except:
                continue
    return ranges

def process_uploaded_file(uploaded_file):
    """Proses file Excel yang diupload"""
    try:
        # Baca file Excel
        df = pd.read_excel(uploaded_file)
        
        # Debug: tampilkan kolom yang ada
        st.info(f"Kolom yang ditemukan: {list(df.columns)}")
        
        # Proses data
        processed_data = []
        
        # Cari kolom yang ada
        columns = df.columns
        ksm_col = None
        dokter_col = None
        poli_col = None
        
        # Cari kolom KSM
        for col in columns:
            if 'KSM' in str(col).upper():
                ksm_col = col
                break
        
        # Cari kolom Nama Dokter
        for col in columns:
            if 'NAMA' in str(col).upper() or 'DOKTER' in str(col).upper():
                dokter_col = col
                break
        
        # Cari kolom POLI
        for col in columns:
            if 'POLI' in str(col).upper():
                poli_col = col
                break
        
        # Hari-hari
        days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        day_cols = []
        for day in days:
            if day in columns:
                day_cols.append(day)
        
        # Jika tidak ditemukan kolom hari standar, cari yang lain
        if not day_cols:
            for col in columns:
                if any(day in str(col).upper() for day in days):
                    day_cols.append(col)
        
        # Logika pemrosesan
        current_ksm = None
        current_dokter = None
        
        for idx, row in df.iterrows():
            # Update KSM
            if ksm_col and pd.notna(row[ksm_col]):
                current_ksm = row[ksm_col]
            
            # Update Dokter
            if dokter_col and pd.notna(row[dokter_col]):
                current_dokter = row[dokter_col]
            
            # Proses jadwal
            if poli_col and pd.notna(row[poli_col]):
                jadwal_type = row[poli_col]
                
                # Proses setiap hari
                for day in day_cols:
                    if day in df.columns and pd.notna(row[day]):
                        jam_value = row[day]
                        if str(jam_value).strip() not in ['', '-', 'nan']:
                            processed_data.append({
                                'KSM': current_ksm,
                                'Dokter': current_dokter,
                                'Jenis': jadwal_type,
                                'Hari': day,
                                'Jam': str(jam_value)
                            })
        
        return pd.DataFrame(processed_data)
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return pd.DataFrame()

def create_empty_template():
    """Buat template kosong"""
    return pd.DataFrame(columns=['KSM', 'Dokter', 'Jenis', 'Hari', 'Jam'])

def save_to_excel(df):
    """Simpan data ke Excel"""
    try:
        # Buat Excel sederhana
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Jadwal')
        
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Error saving Excel: {str(e)}")
        return None

def main():
    st.title("🏥 Sistem Jadwal Dokter")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload File")
        
        uploaded_file = st.file_uploader(
            "Unggah file Excel jadwal dokter",
            type=['xlsx', 'xls'],
            key="file_uploader"
        )
        
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.jadwal_data = process_uploaded_file(uploaded_file)
            st.success("File berhasil diupload!")
        
        st.header("⚙️ Filter")
        
        # Mode tampilan
        view_mode = st.radio(
            "Mode",
            ["View", "Edit"],
            horizontal=True
        )
        
        # Filter hanya jika ada data
        if st.session_state.jadwal_data is not None and not st.session_state.jadwal_data.empty:
            # Filter Poli
            poli_options = ['Semua'] + sorted(st.session_state.jadwal_data['KSM'].dropna().unique().tolist())
            selected_poli = st.selectbox("Poli/KSM", poli_options)
            
            # Filter Hari
            hari_options = ['Semua'] + sorted(st.session_state.jadwal_data['Hari'].dropna().unique().tolist())
            selected_hari = st.multiselect("Hari", hari_options, default=['Semua'])
            
            # Filter Jenis
            jenis_options = ['Semua', 'REGULER', 'EKSEKUTIF', 'JAM KERJA']
            selected_jenis = st.multiselect("Jenis", jenis_options, default=['Semua'])
        
        st.header("📊 Statistik")
        if st.session_state.jadwal_data is not None:
            st.metric("Total Dokter", st.session_state.jadwal_data['Dokter'].nunique())
            st.metric("Total Jadwal", len(st.session_state.jadwal_data))
    
    # Main content
    if view_mode == "View":
        display_view_mode()
    else:
        display_edit_mode()

def display_view_mode():
    """Tampilkan mode view"""
    if st.session_state.jadwal_data is None or st.session_state.jadwal_data.empty:
        st.info("Silakan upload file Excel jadwal dokter di sidebar.")
        return
    
    data = st.session_state.jadwal_data.copy()
    
    # Terapkan filter
    if 'selected_poli' in st.session_state and st.session_state.selected_poli != 'Semua':
        data = data[data['KSM'] == st.session_state.selected_poli]
    
    if 'selected_hari' in st.session_state and 'Semua' not in st.session_state.selected_hari:
        data = data[data['Hari'].isin(st.session_state.selected_hari)]
    
    if 'selected_jenis' in st.session_state and 'Semua' not in st.session_state.selected_jenis:
        data = data[data['Jenis'].isin(st.session_state.selected_jenis)]
    
    # Tampilkan dalam tabs
    tab1, tab2 = st.tabs(["📋 Data Table", "📅 Jadwal Grid"])
    
    with tab1:
        # Tampilkan data
        st.dataframe(
            data,
            use_container_width=True,
            column_config={
                "KSM": "Poli/KSM",
                "Dokter": "Nama Dokter",
                "Jenis": "Jenis Jadwal",
                "Hari": "Hari",
                "Jam": "Jam Praktik"
            }
        )
        
        # Tombol download
        if not data.empty:
            csv = data.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                "jadwal_dokter.csv",
                "text/csv"
            )
    
    with tab2:
        # Buat grid sederhana
        st.subheader("Grid Jadwal")
        
        # Pilih hari untuk ditampilkan
        hari_grid = st.multiselect(
            "Pilih Hari untuk Grid",
            data['Hari'].unique(),
            default=data['Hari'].unique()[:3]
        )
        
        if hari_grid:
            grid_data = data[data['Hari'].isin(hari_grid)]
            
            # Buat pivot table sederhana
            try:
                pivot_df = grid_data.pivot_table(
                    index=['KSM', 'Dokter', 'Jenis'],
                    columns='Hari',
                    values='Jam',
                    aggfunc=lambda x: ', '.join(str(v) for v in x if pd.notna(v))
                ).fillna('-')
                
                # Style berdasarkan jenis
                def color_by_type(val):
                    if 'REGULER' in str(val):
                        return 'background-color: #d4edda'
                    elif 'EKSEKUTIF' in str(val):
                        return 'background-color: #cce5ff'
                    return ''
                
                styled_df = pivot_df.style.applymap(color_by_type)
                st.dataframe(styled_df, use_container_width=True)
            except:
                st.dataframe(grid_data, use_container_width=True)
        
        # Visualisasi sederhana
        st.subheader("Distribusi Jadwal")
        
        if not data.empty:
            # Hitung per hari
            distribusi = data['Hari'].value_counts().reset_index()
            distribusi.columns = ['Hari', 'Jumlah']
            
            # Buat chart menggunakan streamlit native
            st.bar_chart(distribusi.set_index('Hari'))

def display_edit_mode():
    """Tampilkan mode edit"""
    st.header("✏️ Edit Jadwal")
    
    if st.session_state.jadwal_data is None:
        st.info("Upload file terlebih dahulu untuk mengedit jadwal.")
        return
    
    data = st.session_state.jadwal_data.copy()
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Data Saat Ini")
        edited_df = st.data_editor(
            data,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "KSM": st.column_config.TextColumn("Poli/KSM"),
                "Dokter": st.column_config.TextColumn("Nama Dokter"),
                "Jenis": st.column_config.SelectboxColumn(
                    "Jenis Jadwal",
                    options=['REGULER', 'EKSEKUTIF', 'JAM KERJA']
                ),
                "Hari": st.column_config.SelectboxColumn(
                    "Hari",
                    options=['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
                ),
                "Jam": st.column_config.TextColumn("Jam Praktik")
            }
        )
        
        # Update data jika ada perubahan
        if not edited_df.equals(data):
            st.session_state.jadwal_data = edited_df
            st.success("Data berhasil diupdate!")
    
    with col2:
        st.subheader("Tambah Jadwal Baru")
        
        with st.form("tambah_jadwal"):
            new_ksm = st.text_input("Poli/KSM")
            new_dokter = st.text_input("Nama Dokter")
            new_jenis = st.selectbox("Jenis Jadwal", ['REGULER', 'EKSEKUTIF', 'JAM KERJA'])
            new_hari = st.selectbox("Hari", ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU'])
            new_jam = st.text_input("Jam (contoh: 07.30-14.00)")
            
            if st.form_submit_button("➕ Tambah Jadwal"):
                if new_ksm and new_dokter and new_jam:
                    new_row = pd.DataFrame([{
                        'KSM': new_ksm,
                        'Dokter': new_dokter,
                        'Jenis': new_jenis,
                        'Hari': new_hari,
                        'Jam': new_jam
                    }])
                    
                    st.session_state.jadwal_data = pd.concat([data, new_row], ignore_index=True)
                    st.success("Jadwal berhasil ditambahkan!")
                    st.rerun()
        
        st.subheader("💾 Export Data")
        
        if st.button("Simpan ke Excel"):
            excel_file = save_to_excel(st.session_state.jadwal_data)
            if excel_file:
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_file,
                    file_name="jadwal_dokter_updated.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()
