import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Jadwal Dokter",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# KONSTANTA
# =========================
FILE_EXCEL = "jadwal hafis.xlsx"
HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
JAM_SLOTS = pd.date_range("07:00", "14:00", freq="30min").strftime("%H:%M").tolist()

# =========================
# UTILITAS
# =========================
def parse_jam(text):
    if pd.isna(text) or text == "-" or str(text).strip() == "":
        return []

    text = str(text).replace(".", ":")
    hasil = []

    for part in text.split(","):
        match = re.findall(r"\d{2}:\d{2}", part)
        if len(match) == 2:
            start, end = match
            slots = pd.date_range(start, end, freq="30min").strftime("%H:%M").tolist()
            hasil.extend(slots[:-1])

    return hasil

def build_long_df(raw):
    rows = []
    for _, r in raw.iterrows():
        for hari in HARI_LIST:
            slots = parse_jam(r.get(hari, ""))
            for s in slots:
                rows.append({
                    "Hari": hari,
                    "Jam": s,
                    "Dokter": r["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"],
                    "Poli": r["KSM"],
                    "Jenis": r["POLI"]
                })
    return pd.DataFrame(rows)

def build_grid(df_hari):
    if df_hari.empty:
        return pd.DataFrame()

    return (
        df_hari
        .pivot_table(
            index="Jam",
            columns="Dokter",
            values="Poli",
            aggfunc="first"
        )
        .reindex(JAM_SLOTS)
        .reset_index()
    )

# =========================
# EXPORT EXCEL LANDSCAPE
# =========================
def export_excel_landscape(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for hari in HARI_LIST:
            d = df[df["Hari"] == hari]
            grid = build_grid(d)
            if grid.empty:
                grid = pd.DataFrame({"Info": [f"Tidak ada jadwal hari {hari}"]})

            grid.to_excel(writer, sheet_name=hari, index=False, startrow=1)

    output.seek(0)
    wb = load_workbook(output)

    for hari in HARI_LIST:
        ws = wb[hari]
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.fitToWidth = 1

        ws.insert_rows(1)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ws.max_column)
        c = ws.cell(row=1, column=1)
        c.value = f"JADWAL DOKTER – {hari}"
        c.font = Font(size=14, bold=True)
        c.alignment = Alignment(horizontal="center", vertical="center")

        ws.freeze_panes = "A3"

        for col in ws.columns:
            max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 25)

    final = BytesIO()
    wb.save(final)
    final.seek(0)
    return final

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    try:
        return pd.read_excel(FILE_EXCEL, sheet_name="Sheet1")
    except:
        return pd.DataFrame()

raw_df = load_data()

# =========================
# HEADER TV MODE
# =========================
st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center'>📺 JADWAL DOKTER RAWAT JALAN</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# =========================
# VALIDASI DATA
# =========================
if raw_df.empty:
    st.error("❌ File Excel tidak ditemukan atau kosong.")
    st.stop()

# =========================
# PROSES DATA
# =========================
df_long = build_long_df(raw_df)

# =========================
# TAMPILAN UTAMA (SEMUA HARI)
# =========================
tabs = st.tabs(HARI_LIST)

for i, hari in enumerate(HARI_LIST):
    with tabs[i]:
        grid = build_grid(df_long[df_long["Hari"] == hari])
        st.dataframe(grid, use_container_width=True, height=500)

# =========================
# EXPORT
# =========================
st.markdown("---")
st.subheader("📤 Export Jadwal")

excel = export_excel_landscape(df_long)

st.download_button(
    "⬇️ Download Excel (Landscape – 1 Sheet per Hari)",
    data=excel,
    file_name=f"jadwal_dokter_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("File siap dicetak dan dibagikan.")
