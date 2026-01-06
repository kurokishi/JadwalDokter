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
        df.columns.astype(str)
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
                    "Jenis": str(r[col_poli]).upper()
                })

    return pd.DataFrame(rows)


def build_grid_with_jenis(df_hari):
    if df_hari.empty:
        return None, None

    grid_value = (
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

    grid_jenis = (
        df_hari
        .pivot_table(
            index="Jam",
            columns="Dokter",
            values="Jenis",
            aggfunc="first"
        )
        .reindex(JAM_SLOTS)
        .reset_index()
    )

    return grid_value, grid_jenis


def style_grid(grid_value, grid_jenis):
    styles = pd.DataFrame("", index=grid_value.index, columns=grid_value.columns)

    for col in grid_value.columns[1:]:  # skip Jam
        for i in grid_value.index:
            jenis = grid_jenis.at[i, col]
            if jenis == "REGULER":
                styles.at[i, col] = "background-color:#C6EFCE;color:black;"
            elif jenis == "EKSEKUTIF":
                styles.at[i, col] = "background-color:#BDD7EE;color:black;"

    return styles

# ======================================================
# EXPORT EXCEL (LANDSCAPE)
# ======================================================
def export_excel_landscape(df):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for hari in HARI_LIST:
            df_hari = df[df["Hari"] == hari]
            grid, _ = build_grid_with_jenis(df_hari)

            if grid is None or grid.empty:
                grid = pd.DataFrame({"Info": [f"Tidak ada jadwal hari {hari}"]})

            grid.to_excel(writer, sheet_name=hari, index=False, startrow=1)

    buffer.seek(0)
    wb = load_workbook(buffer)

    for hari in HARI_LIST:
        ws = wb[hari]
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.fitToWidth = 1

        ws.insert_rows(1)
        ws.merge_cells(1, 1, 1, ws.max_column)

        title = ws.cell(row=1, column=1)
        title.value = f"JADWAL DOKTER – {hari}"
        title.font = Font(size=14, bold=True)
        title.alignment = Alignment(horizontal="center", vertical="center")

        ws.freeze_panes = "A3"

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
if raw_df.empty:
    st.stop()

# ======================================================
# HEADER
# ======================================================
st.markdown("<h1 style='text-align:center'>📺 JADWAL DOKTER RAWAT JALAN</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ======================================================
# LEGEND WARNA (POIN 5)
# ======================================================
st.markdown("""
<div style="display:flex;justify-content:center;gap:60px;font-size:20px;margin-bottom:12px;">
  <div>
    <span style="display:inline-block;width:24px;height:24px;background:#C6EFCE;border:1px solid #555;margin-right:8px;"></span>
    <b>REGULER</b>
  </div>
  <div>
    <span style="display:inline-block;width:24px;height:24px;background:#BDD7EE;border:1px solid #555;margin-right:8px;"></span>
    <b>EKSEKUTIF</b>
  </div>
</div>
""", unsafe_allow_html=True)

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
        grid_val, grid_jenis = build_grid_with_jenis(
            df_long[df_long["Hari"] == hari]
        )

        if grid_val is None:
            st.info("Tidak ada jadwal")
        else:
            styled = grid_val.style.apply(
                lambda _: style_grid(grid_val, grid_jenis),
                axis=None
            )

            st.dataframe(styled, use_container_width=True, height=520)

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
