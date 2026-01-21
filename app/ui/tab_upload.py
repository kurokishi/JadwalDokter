"""
Upload tab UI component - SIMPLIFIED
"""
import streamlit as st
import pandas as pd
import tempfile
import os
from app.config import AppConfig

def display_upload_tab():
    """Display upload tab content"""
    
    st.header("📤 Upload Data Jadwal Dokter")
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Pilih file Excel atau CSV",
        type=AppConfig.ALLOWED_EXTENSIONS,
        help="Format yang didukung: .xlsx, .xls, .csv"
    )
    
    if uploaded_file is not None:
        # Show file info
        file_size = uploaded_file.size / 1024 / 1024  # Convert to MB
        st.info(f"**File:** {uploaded_file.name} | **Size:** {file_size:.2f} MB")
        
        # Check if it's hafis format
        is_hafis_format = 'hafis' in uploaded_file.name.lower()
        
        if is_hafis_format:
            st.success("🎯 **Format jadwal_hafis.xlsx terdeteksi!**")
        
        # Parse button
        if st.button("🚀 Parse File", type="primary", use_container_width=True):
            parse_uploaded_file(uploaded_file, is_hafis_format)
    
    # Data preview section
    if 'data' in st.session_state and st.session_state.data_loaded:
        st.divider()
        st.subheader("📋 Preview Data")
        
        df = st.session_state.data
        show_data_preview(df)
    
    # Sample data button
    st.divider()
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
                    from app.utils.parser import JadwalHafisParser
                    parser = JadwalHafisParser()
                    df = parser.parse_file(tmp_path)
                    
                    st.success("✅ File jadwal_hafis.xlsx berhasil diparsing!")
                    
                else:
                    # Standard Excel/CSV parsing
                    if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(tmp_path, engine='openpyxl')
                    else:
                        df = pd.read_csv(tmp_path)
                    
                    st.success("✅ File berhasil diunggah!")
                
                # Basic cleaning
                df = df.fillna('')
                
                # Store in session state
                st.session_state.data = df
                st.session_state.data_loaded = True
                st.session_state.current_file = uploaded_file.name
                
                # Show success message
                st.balloons()
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                
    except Exception as e:
        st.error(f"❌ Error parsing file: {str(e)}")

def show_data_preview(df: pd.DataFrame):
    """Show data preview with statistics"""
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        doctors = len(df['doctor_name'].unique()) if 'doctor_name' in df.columns else 0
        st.metric("Unique Doctors", doctors)
    with col3:
        specialties = len(df['specialty'].unique()) if 'specialty' in df.columns else 0
        st.metric("Specialties", specialties)
    with col4:
        days = len(df['day'].unique()) if 'day' in df.columns else 0
        st.metric("Days", days)
    
    # Data preview
    st.write("**Data Preview:**")
    st.dataframe(df.head(20), use_container_width=True)
    
    # Column information
    with st.expander("📋 Column Information"):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': df.notna().sum(),
            'Null Count': df.isna().sum()
        })
        st.dataframe(col_info, use_container_width=True)

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
