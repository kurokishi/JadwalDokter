import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

# ======================================================
# KONFIGURASI HALAMAN (MODE TV)
# ======================================================
st.set_page_config(
    page_title="Jadwal Dokter",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ======================================================
# KONSTANTA
# ======================================================
FILE_EXCEL = "jadwal hafis.xlsx"
HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
JAM_SLOTS = pd.date_range("07:00", "14:00", freq="30min").strftime("%H:%M").tolist()

# ======================================================
# UTILITAS DATA
# ======================================================
def normalize_columns(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace("\n", " ", regex=False)
    )
    return df


def detect_column(df, keywords):
    for col in df.columns:
        for kw in keywords:
            if kw in col:
                return col
    return None


def parse_jam(value):
    if pd.isna(value):
        return []

    text = str(value).strip()
    if text in ["", "-"]:
        return []

    text = text.replace(".", ":")
    slots_all = []

    for part in text.split(","):
        jam = re.findall(r"\d{2}:\d{2}", part)
        if len(jam) == 2:
            start, end = jam
            slots = pd.date_range(start, end, freq="30min").strftime("%H:%M").tolist()
            slots_all.extend(slots[:-1])

    return slots_all


def build_long_df(raw):
    rows = []

    col_dokter = detect_column(raw, ["DOKTER"])
    col_ksm = detect_column(raw, ["KSM"])
    col_poli = detect_column(raw, ["POLI"])

    if not col_dokter or not col_ksm or not col_poli:
        st.error("❌ Kolom Dokter / KSM / POLI tidak terdeteksi di file Excel.")
        st.stop()

    for _, r in raw.iterrows():
        for hari in HARI_LIST:
            slots = parse_jam(r.get(hari, ""))
            for jam in slots:
                rows.append({
                    "Hari": hari,
                    "Jam": jam,
                    "Dokter": r[col_dokter],
                    "Poli": r[col_ksm],
                    "Jenis": r[col_poli]
                })

    return pd.DataFrame(rows)


def build_grid(df_hari):
    if df_hari.empty:
        return pd.DataFrame()

    grid = (
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

    return grid

# ======================================================
# EXPORT EXCEL (LANDSCAPE, 1 SHEET / HARI)
# ======================================================
def export_excel_landscape(df):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for hari in HARI_LIST:
            df_hari = df[df["Hari"] == hari]
            grid = build_grid(df_hari)

            if grid.empty:
                grid = pd.DataFrame({"Info": [f"Tidak ada jadwal hari {hari}"]})

            grid.to_excel(writer, sheet_name=hari, index=False, startrow=1)

    buffer.seek(0)
    wb = load_workbook(buffer)

    for hari in HARI_LIST:
        ws = wb[hari]

        # Landscape & fit
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.fitToWidth = 1

        # Judul
        ws.insert_rows(1)
        ws.merge_cells(
            start_row=1,
            start_column=1,
            end_row=1,
            end_column=ws.max_column
        )

        title = ws.cell(row=1, column=1)
        title.value = f"JADWAL DOKTER – {hari}"
        title.font = Font(size=14, bold=True)
        title.alignment = Alignment(horizontal="center", vertical="center")

        ws.freeze_panes = "A3"

        # Auto width kolom (AMAN merged cell)
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            max_len = 0

            for row_idx in range(2, ws.max_row + 1):
                val = ws.cell(row=row_idx, column=col_idx).value
                if val:
                    max_len = max(max_len, len(str(val)))

            ws.column_dimensions[col_letter].width = min(max_len + 2, 25)

    final = BytesIO()
    wb.save(final)
    final.seek(0)
    return final

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE_EXCEL, sheet_name="Sheet1")
        return normalize_columns(df)
    except Exception as e:
        st.error(f"❌ Gagal membaca Excel: {e}")
        return pd.DataFrame()


raw_df = load_data()

# ======================================================
# HEADER
# ======================================================
st.markdown(
    "<h1 style='text-align:center'>📺 JADWAL DOKTER RAWAT JALAN</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)

if raw_df.empty:
    st.stop()

# ======================================================
# PROSES DATA
# ======================================================
df_long = build_long_df(raw_df)

# ======================================================
# TAMPILAN JADWAL (SEMUA HARI)
# ======================================================
tabs = st.tabs(HARI_LIST)

for i, hari in enumerate(HARI_LIST):
    with tabs[i]:
        grid = build_grid(df_long[df_long["Hari"] == hari])
        st.dataframe(grid, use_container_width=True, height=520)

# ======================================================
# EXPORT
# ======================================================
st.markdown("---")
st.subheader("📤 Export Jadwal")

excel_file = export_excel_landscape(df_long)

st.download_button(
    label="⬇️ Download Excel (Landscape – 1 Sheet per Hari)",
    data=excel_file,
    file_name=f"jadwal_dokter_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("File siap dicetak & dibagikan.")
