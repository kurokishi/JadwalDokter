"""
Schedule viewer UI
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.utils import init_session_state


def show_schedule_viewer():
    """Display schedule viewer page"""
    
    # Initialize session state
    init_session_state()
    
    st.title("📅 View Jadwal")
    
    # Check if data exists
    if st.session_state.grid_data is None or st.session_state.grid_data.empty:
        st.info("ℹ️ Tidak ada data jadwal. Silakan upload dan konversi file terlebih dahulu di halaman Upload & Konversi.")
        
        if st.button("🔄 Ke Halaman Upload"):
            st.session_state['current_page'] = 'upload'
            st.rerun()
        return
    
    grid_df = st.session_state.grid_data
    
    # Overview
    st.markdown("### 📊 Overview Jadwal")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jadwal", len(grid_df))
    with col2:
        st.metric("Dokter", grid_df['DOKTER'].nunique())
    with col3:
        st.metric("Poli", grid_df['POLI'].nunique())
    with col4:
        st.metric("File", st.session_state.get('file_name', 'N/A'))
    
    # Interactive filters
    st.markdown("### 🔍 Filter & Pencarian")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Tabel Data", "📊 Visualisasi", "🔎 Pencarian Detail"])
    
    with tab1:
        show_data_table(grid_df)
    
    with tab2:
        show_visualizations(grid_df)
    
    with tab3:
        show_detailed_search(grid_df)


def show_data_table(grid_df: pd.DataFrame):
    """Display data table with filters"""
    
    # Multi-column filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # POLI filter
        poli_options = ['Semua'] + sorted(grid_df['POLI'].unique().tolist())
        selected_poli = st.multiselect(
            "Pilih POLI",
            options=poli_options[1:],
            default=poli_options[1] if len(poli_options) > 1 else []
        )
    
    with col2:
        # JENIS filter
        jenis_options = ['Semua'] + sorted(grid_df['JENIS'].unique().tolist())
        selected_jenis = st.multiselect(
            "Pilih JENIS",
            options=jenis_options[1:],
            default=jenis_options[1] if len(jenis_options) > 1 else []
        )
    
    with col3:
        # HARI filter
        hari_options = ['Semua'] + sorted(grid_df['HARI'].unique().tolist())
        selected_hari = st.multiselect(
            "Pilih HARI",
            options=hari_options[1:],
            default=hari_options[1] if len(hari_options) > 1 else []
        )
    
    # Apply filters
    filtered_df = grid_df.copy()
    
    if selected_poli and 'Semua' not in selected_poli:
        filtered_df = filtered_df[filtered_df['POLI'].isin(selected_poli)]
    
    if selected_jenis and 'Semua' not in selected_jenis:
        filtered_df = filtered_df[filtered_df['JENIS'].isin(selected_jenis)]
    
    if selected_hari and 'Semua' not in selected_hari:
        filtered_df = filtered_df[filtered_df['HARI'].isin(selected_hari)]
    
    # Search doctor
    search_term = st.text_input("🔍 Cari dokter atau poli...", "")
    if search_term:
        filtered_df = filtered_df[
            filtered_df['DOKTER'].str.contains(search_term, case=False, na=False) |
            filtered_df['POLI'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display data
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )
    
    # Show filter stats
    st.caption(f"Menampilkan {len(filtered_df)} dari {len(grid_df)} jadwal")


def show_visualizations(grid_df: pd.DataFrame):
    """Display data visualizations"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution by POLI
        poli_dist = grid_df['POLI'].value_counts().reset_index()
        poli_dist.columns = ['POLI', 'Count']
        
        fig1 = px.bar(
            poli_dist,
            x='POLI',
            y='Count',
            title='Distribusi Jadwal per POLI',
            color='POLI'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Distribution by JENIS
        jenis_dist = grid_df['JENIS'].value_counts().reset_index()
        jenis_dist.columns = ['JENIS', 'Count']
        
        fig2 = px.pie(
            jenis_dist,
            values='Count',
            names='JENIS',
            title='Distribusi Reguler vs Eksekutif',
            color='JENIS',
            color_discrete_map={'Reguler': '#10B981', 'Eksekutif': '#F59E0B'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Distribution by HARI
        hari_dist = grid_df['HARI'].value_counts().reset_index()
        hari_dist.columns = ['HARI', 'Count']
        
        # Order days properly
        day_order = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        hari_dist['HARI'] = pd.Categorical(hari_dist['HARI'], categories=day_order, ordered=True)
        hari_dist = hari_dist.sort_values('HARI')
        
        fig3 = px.bar(
            hari_dist,
            x='HARI',
            y='Count',
            title='Distribusi Jadwal per Hari',
            color='HARI'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        # Top doctors
        doctor_dist = grid_df['DOKTER'].value_counts().head(10).reset_index()
        doctor_dist.columns = ['DOKTER', 'Count']
        
        fig4 = px.bar(
            doctor_dist,
            y='DOKTER',
            x='Count',
            title='10 Dokter dengan Jadwal Terbanyak',
            orientation='h',
            color='Count'
        )
        st.plotly_chart(fig4, use_container_width=True)


def show_detailed_search(grid_df: pd.DataFrame):
    """Display detailed search functionality"""
    
    st.markdown("### 🔎 Pencarian Detail")
    
    # Doctor selector
    doctors = sorted(grid_df['DOKTER'].unique().tolist())
    selected_doctor = st.selectbox(
        "Pilih Dokter",
        options=[''] + doctors,
        help="Pilih dokter untuk melihat jadwal detail"
    )
    
    if selected_doctor:
        doctor_schedule = grid_df[grid_df['DOKTER'] == selected_doctor]
        
        if not doctor_schedule.empty:
            st.markdown(f"### 📋 Jadwal Dr. {selected_doctor}")
            
            # Display schedule in a nice format
            for _, row in doctor_schedule.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
                    
                    with col1:
                        st.markdown(f"**POLI:** {row['POLI']}")
                    
                    with col2:
                        st.markdown(f"**Hari:** {row['HARI']}")
                    
                    with col3:
                        jenis_color = "#10B981" if row['JENIS'] == 'Reguler' else "#F59E0B"
                        st.markdown(f"<span style='color: {jenis_color}; font-weight: bold;'>{row['JENIS']}</span>", 
                                  unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"**Jam:** {row['JAM']}")
                    
                    st.divider()
            
            # Time slot visualization for this doctor
            st.markdown("### 🕐 Visualisasi Time Slot")
            
            # Extract time slot data
            time_cols = [col for col in grid_df.columns if col not in ['POLI', 'JENIS', 'HARI', 'DOKTER', 'JAM']]
            
            # Create heatmap data
            heatmap_data = []
            for _, row in doctor_schedule.iterrows():
                for time_slot in time_cols:
                    if row[time_slot] in ['R', 'E']:
                        heatmap_data.append({
                            'Hari': row['HARI'],
                            'Time': time_slot,
                            'Jenis': row['JENIS'],
                            'Value': 1 if row[time_slot] == 'R' else 2
                        })
            
            if heatmap_data:
                heatmap_df = pd.DataFrame(heatmap_data)
                
                # Create pivot table
                pivot_df = heatmap_df.pivot_table(
                    index='Hari',
                    columns='Time',
                    values='Value',
                    aggfunc='max',
                    fill_value=0
                )
                
                # Reorder days
                day_order = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
                pivot_df = pivot_df.reindex(day_order, errors='ignore')
                
                # Create heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_df.values,
                    x=pivot_df.columns,
                    y=pivot_df.index,
                    colorscale=[[0, 'white'], [0.5, '#FFEB9C'], [1, '#C6EFCE']],
                    showscale=False
                ))
                
                fig.update_layout(
                    title=f"Time Slot Heatmap - {selected_doctor}",
                    xaxis_title="Time Slot",
                    yaxis_title="Hari",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Legend
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("<div style='background-color: #C6EFCE; padding: 10px; border-radius: 5px;'>Reguler (R)</div>", 
                              unsafe_allow_html=True)
                with col2:
                    st.markdown("<div style='background-color: #FFEB9C; padding: 10px; border-radius: 5px;'>Eksekutif (E)</div>", 
                              unsafe_allow_html=True)
                with col3:
                    st.markdown("<div style='background-color: white; border: 1px solid #ddd; padding: 10px; border-radius: 5px;'>Tidak Ada Jadwal</div>", 
                              unsafe_allow_html=True)
        else:
            st.warning(f"Tidak ada jadwal ditemukan untuk dokter {selected_doctor}")
    
    else:
        st.info("ℹ️ Pilih dokter untuk melihat jadwal detail")
