"""
Upload tab UI component
"""
import streamlit as st
import pandas as pd
import tempfile
import os
from app.utils.parser import JadwalHafisParser
from app.utils.validator import DataValidator
from app.utils.cleaner import DataCleaner
from app.config import AppConfig

def display_upload_tab():
    """Display upload tab content"""
    
    st.header("📤 Upload Data Jadwal Dokter")
    
    # File upload section
    with st.container():
        st.subheader("1. Unggah File")
        
        uploaded_file = st.file_uploader(
            "Pilih file Excel atau CSV",
            type=AppConfig.ALLOWED_EXTENSIONS,
            help="Format yang didukung: .xlsx, .xls, .csv. Ukuran maksimal: 50MB"
        )
        
        if uploaded_file is not None:
            # Show file info
            file_size = uploaded_file.size / 1024 / 1024  # Convert to MB
            st.info(f"**File:** {uploaded_file.name} | **Size:** {file_size:.2f} MB")
            
            # Check if it's hafis format
            is_hafis_format = 'hafis' in uploaded_file.name.lower()
            
            if is_hafis_format:
                st.success("🎯 **Format jadwal_hafis.xlsx terdeteksi!** Akan menggunakan parser khusus.")
            
            # Parse button
            if st.button("🚀 Parse File", type="primary", use_container_width=True):
                parse_uploaded_file(uploaded_file, is_hafis_format)
    
    # Data preview section
    if 'data' in st.session_state and st.session_state.data_loaded:
        st.divider()
        st.subheader("2. Preview Data")
        
        df = st.session_state.data
        
        # Show data info
        show_data_preview(df)
        
        # Data cleaning options
        with st.expander("🧹 Data Cleaning Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Clean Doctor Names"):
                    df = DataCleaner.clean_doctor_names(df)
                    st.session_state.data = df
                    st.success("Doctor names cleaned!")
                    st.rerun()
            
            with col2:
                if st.button("Clean Specialty Names"):
                    df = DataCleaner.clean_specialty_names(df)
                    st.session_state.data = df
                    st.success("Specialty names cleaned!")
                    st.rerun()
            
            if st.button("Remove Duplicates"):
                df = DataCleaner.remove_duplicates(df)
                st.session_state.data = df
                st.success(f"Duplicates removed! {len(df)} records remaining")
                st.rerun()
        
        # Validation
        with st.expander("✅ Data Validation"):
            is_valid, errors = DataValidator.validate_dataframe(df)
            
            if is_valid:
                st.success("Data is valid!")
            else:
                st.error("Data validation failed:")
                for error in errors:
                    st.write(f"• {error}")
    
    # Template download
    st.divider()
    st.subheader("3. Template & Examples")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Template", use_container_width=True):
            create_template_download()
    
    with col2:
        if st.button("🎲 Load Sample Data", use_container_width=True):
            load_sample_data()

def parse_uploaded_file(uploaded_file, is_hafis_format: bool = False):
    """Parse uploaded file based on format"""
    try:
        with st.spinner("Parsing file..."):
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            
            try:
                if is_hafis_format:
                    # Use custom parser for hafis format
                    parser = JadwalHafisParser()
                    df = parser.parse_file(tmp_path)
                    
                    # Set flag
                    st.session_state.hafis_parsed = True
                    st.success("✅ File jadwal_hafis.xlsx berhasil diparsing!")
                    
                else:
                    # Standard Excel/CSV parsing
                    if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(tmp_path, engine='openpyxl')
                    else:
                        df = pd.read_csv(tmp_path)
                    
                    st.success("✅ File berhasil diunggah!")
                
                # Clean data
                df = DataCleaner.fill_missing_values(df)
                
                # Store in session state
                st.session_state.data = df
                st.session_state.data_loaded = True
                st.session_state.current_file = uploaded_file.name
                st.session_state.uploaded_file = uploaded_file
                
                # Show success message
                st.balloons()
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                
    except Exception as e:
        st.error(f"❌ Error parsing file: {str(e)}")
        st.info("""
        **Tips:**
        1. Pastikan file tidak sedang dibuka di program lain
        2. Untuk file Excel, pastikan format sesuai
        3. Untuk file jadwal_hafis.xlsx, pastikan struktur sesuai dengan contoh
        """)

def show_data_preview(df: pd.DataFrame):
    """Show data preview with statistics"""
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Unique Doctors", len(df['doctor_name'].unique()))
    with col3:
        st.metric("Specialties", len(df['specialty'].unique()))
    with col4:
        days = len(df['day'].unique()) if 'day' in df.columns else 0
        st.metric("Days", days)
    
    # Data preview
    st.write("**Data Preview:**")
    
    # Show first 50 rows
    st.dataframe(df.head(50), use_container_width=True)
    
    # Column information
    with st.expander("📋 Column Information"):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': df.notna().sum(),
            'Null Count': df.isna().sum(),
            'Unique Values': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)
    
    # Quick analysis
    with st.expander("📊 Quick Analysis"):
        if 'specialty' in df.columns:
            st.write("**Doctors per Specialty:**")
            specialty_counts = df['specialty'].value_counts()
            st.bar_chart(specialty_counts)
        
        if 'day' in df.columns:
            st.write("**Schedule Distribution by Day:**")
            day_counts = df['day'].value_counts()
            st.bar_chart(day_counts)

def create_template_download():
    """Create and download template file"""
    try:
        # Create template DataFrame
        template_data = {
            'doctor_name': ['Dr. John Doe', 'Dr. Jane Smith'],
            'specialty': ['Cardiology', 'Pediatrics'],
            'department': ['Cardiology', 'Pediatrics'],
            'day': ['Monday', 'Tuesday'],
            'working_hours': ['08:00-16:00', '09:00-17:00'],
            'regular_schedule': ['08:00-12:00', '09:00-13:00'],
            'executive_schedule': ['14:00-16:00', '14:00-17:00'],
            'available': [1, 1]
        }
        
        template_df = pd.DataFrame(template_data)
        
        # Convert to CSV
        csv = template_df.to_csv(index=False)
        
        # Download button
        st.download_button(
            label="📥 Download Template CSV",
            data=csv,
            file_name="jadwal_dokter_template.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error creating template: {str(e)}")

def load_sample_data():
    """Load sample data for demonstration"""
    try:
        # Create sample data
        sample_data = {
            'doctor_name': [
                'Dr. Ahmad Mahfur, Sp.A', 'Dr. Ahmad Mahfur, Sp.A',
                'Dr. Hakimah Maimunah, Sp.A', 'Dr. Hakimah Maimunah, Sp.A',
                'Dr. Agoeng Suprijadi, Sp.B', 'Dr. Agoeng Suprijadi, Sp.B'
            ],
            'specialty': [
                'Pediatrics', 'Pediatrics',
                'Pediatrics', 'Pediatrics',
                'Surgery', 'Surgery'
            ],
            'department': [
                'Anak', 'Anak',
                'Anak', 'Anak',
                'Bedah', 'Bedah'
            ],
            'day': [
                'Monday', 'Tuesday',
                'Monday', 'Wednesday',
                'Tuesday', 'Thursday'
            ],
            'working_hours': [
                '07:30-14:00', '07:30-14:00',
                '07:30-14:00', '07:30-14:00',
                '07:30-14:00', '07:30-14:00'
            ],
            'regular_schedule': [
                '08:00-12:00', '08:00-12:00',
                '09:00-13:00', '09:00-13:00',
                '08:00-12:00', '08:00-12:00'
            ],
            'executive_schedule': [
                '07:30-08:25', '07:30-08:25',
                '09:35-10:30', '09:30-10:25',
                '-', '07:30-08:25'
            ],
            'available': [1, 1, 1, 1, 1, 1]
        }
        
        df = pd.DataFrame(sample_data)
        
        # Store in session state
        st.session_state.data = df
        st.session_state.data_loaded = True
        st.session_state.current_file = "sample_data.csv"
        
        st.success("✅ Sample data loaded successfully!")
        st.balloons()
        
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
