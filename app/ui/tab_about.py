"""
About tab UI component
"""
import streamlit as st
from app.config import AppConfig

def display_about_tab():
    """Display about tab content"""
    
    st.header("ℹ️ About")
    
    # App information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("🏥", width=150)
    
    with col2:
        st.markdown(f"""
        ### {AppConfig.APP_NAME}
        **Version:** {AppConfig.APP_VERSION}
        
        Aplikasi manajemen jadwal dokter rumah sakit dengan fitur lengkap untuk 
        upload, view, edit, dan analisis jadwal dokter.
        """)
    
    # Features
    st.divider()
    st.subheader("✨ Features")
    
    features = [
        {
            "icon": "📤",
            "title": "Upload Data",
            "description": "Support untuk file Excel/CSV termasuk format khusus jadwal_hafis.xlsx"
        },
        {
            "icon": "📅", 
            "title": "Schedule Management",
            "description": "View, filter, dan analisis jadwal dokter dengan berbagai tampilan"
        },
        {
            "icon": "🧩",
            "title": "Kanban Drag",
            "description": "Sistem penjadwalan visual dengan drag & drop interface"
        },
        {
            "icon": "📊",
            "title": "Analytics",
            "description": "Statistik dan visualisasi data jadwal dokter"
        },
        {
            "icon": "⚙️",
            "title": "Customization",
            "description": "Pengaturan preferensi dan tampilan yang dapat disesuaikan"
        },
        {
            "icon": "📁",
            "title": "Export Data",
            "description": "Export data ke format CSV untuk analisis lebih lanjut"
        }
    ]
    
    # Display features in grid
    cols = st.columns(3)
    for idx, feature in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="
                padding: 1.5rem;
                background-color: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 1rem;
                height: 180px;
            ">
                <h3>{feature['icon']} {feature['title']}</h3>
                <p>{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # File format support
    st.divider()
    st.subheader("📁 Supported File Formats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Standard Formats
        - **Excel**: .xlsx, .xls
        - **CSV**: .csv
        
        **Required columns:**
        - `doctor_name` (Nama dokter)
        - `specialty` (Spesialisasi)
        - `day` (Hari)
        - `working_hours` (Jam kerja)
        """)
    
    with col2:
        st.markdown("""
        ### Special Format: jadwal_hafis.xlsx
        Format khusus RS dengan struktur:
        
        ```
        KSM | Nama dokter | POLI | SENIN | SELASA | ...
        Anak | dr. Debby | JAM KERJA | 07:30-14:00
          |   | REGULER | [Reference]
          |   | EKSEKUTIF | 10:30-11:25
        ```
        
        **Auto-detected and parsed with custom parser**
        """)
    
    # How to use
    st.divider()
    st.subheader("🚀 How to Use")
    
    with st.expander("Quick Start Guide", expanded=False):
        st.markdown("""
        1. **Upload Data** (Tab Upload)
           - Upload file Excel/CSV
           - Untuk file jadwal_hafis.xlsx, sistem akan otomatis mengenali
        
        2. **View Schedule** (Tab Jadwal Dokter)
           - Pilih tampilan: tabel, per dokter, atau timeline
           - Filter berdasarkan spesialisasi atau hari
        
        3. **Manage Schedule** (Tab Kanban Drag)
           - Atur jadwal dengan drag & drop interface
           - Assign dokter ke time slots
        
        4. **Customize** (Tab Preferences)
           - Atur preferensi tampilan
           - Export/import settings
        
        5. **Export Data**
           - Download data sebagai CSV
           - Simpan perubahan
        """)
    
    # Technology stack
    st.divider()
    st.subheader("🛠️ Technology Stack")
    
    tech_cols = st.columns(4)
    
    with tech_cols[0]:
        st.markdown("""
        **Frontend**
        - Streamlit
        - Plotly
        """)
    
    with tech_cols[1]:
        st.markdown("""
        **Backend**
        - Python 3.11
        - Pandas
        - NumPy
        """)
    
    with tech_cols[2]:
        st.markdown("""
        **Data Processing**
        - Custom parsers
        - Data validation
        - Cleaning utilities
        """)
    
    with tech_cols[3]:
        st.markdown("""
        **Deployment**
        - Streamlit Cloud
        - Docker (optional)
        """)
    
    # Contact & Support
    st.divider()
    st.subheader("📞 Contact & Support")
    
    st.markdown("""
    Untuk pertanyaan, masalah, atau saran:
    
    - **Issues**: Laporkan bug atau request fitur
    - **Documentation**: Lihat dokumentasi lengkap
    - **Support**: Hubungi tim developer
    
    **Version:** {}
    **Last Updated:** {}
    """.format(AppConfig.APP_VERSION, "2024"))
