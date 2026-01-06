import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment, Font

st.set_page_config(
    page_title="Jadwal Dokter RS",
    layout="wide"
)

FILE_PATH = "jadwal hafis.xlsx"
HARI = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE_PATH, sheet_name="Sheet1")
        df.columns = [c.strip().upper() for c in df.columns]
        return df
    except:
        return None

df = load_data()

st.title("📅 Jadwal Dokter")

if df is None:
    st.error("File Excel tidak ditemukan atau format salah.")
    st.stop()

# =========================
# SIDEBAR FILTER
# =========================
with st.sidebar:
    st.header("Filter")

    ksm_list = ["Semua"] + sorted(df["KSM"].dropna().unique().tolist())
    ksm = st.selectbox("KSM", ksm_list)

    hari_filter = st.multiselect(
        "Hari",
        HARI,
        default=HARI[:5]
    )

    search = st.text_input("Cari Dokter")

# =========================
# FILTER DATA
# =========================
df_view = df.copy()

if ksm != "Semua":
    df_view = df_view[df_view["KSM"] == ksm]

if search:
    df_view = df_view[df_view.iloc[:,1].str.contains(search, case=False, na=False)]

cols_show = ["KSM", df_view.columns[1], "POLI"] + hari_filter
df_view = df_view[cols_show]

# =========================
# STYLE WARNA (MIRIP EXCEL)
# =========================
def style_jadwal(val):
    if pd.isna(val) or val == "-" or val == "":
        return ""
    val = str(val).lower()
    if "eksek" in val or "e" in val:
        return "background-color:#BDD7EE"
    return "background-color:#C6EFCE"

styled = df_view.style.applymap(style_jadwal, subset=hari_filter)

# =========================
# LEGEND
# =========================
st.markdown("""
<div style="display:flex; gap:30px; font-size:16px; margin-bottom:10px;">
<div><span style="background:#C6EFCE;padding:6px 14px;"></span> Reguler</div>
<div><span style="background:#BDD7EE;padding:6px 14px;"></span> Eksekutif</div>
</div>
""", unsafe_allow_html=True)

# =========================
# TAMPILKAN TABEL
# =========================
st.dataframe(
    styled,
    use_container_width=True,
    height=600
)

# =========================
# EXPORT EXCEL (1 SHEET / HARI)
# =========================
def export_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for h in hari_filter:
            cols = ["KSM", df.columns[1], "POLI", h]
            temp = df[cols]
            temp.to_excel(writer, sheet_name=h, index=False)

    buffer.seek(0)
    return buffer

st.download_button(
    "⬇️ Download Excel Jadwal",
    export_excel(df_view),
    file_name="jadwal_dokter.xlsx"
)
