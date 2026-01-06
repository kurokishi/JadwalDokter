import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from openpyxl import Workbook
import plotly.express as px
import os

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Jadwal Dokter", layout="wide")

FILE_INPUT = "jadwal hafis.xlsx"
FILE_OUTPUT = "jadwal coba.xlsx"

HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]

# =========================================================
# TIME SLOT
# =========================================================
def generate_time_slots(start="07:00", end="14:00", step=30):
    slots = []
    t = datetime.strptime(start, "%H:%M")
    end_t = datetime.strptime(end, "%H:%M")
    while t <= end_t:
        slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=step)
    return slots

TIME_SLOTS = generate_time_slots()

# =========================================================
# PARSE JAM
# =========================================================
def parse_time_ranges(cell):
    if pd.isna(cell):
        return []

    text = str(cell).strip()
    if text in ["-", ""]:
        return []

    text = text.replace(".", ":")
    ranges = text.split(",")

    slots = []
    for r in ranges:
        try:
            start, end = r.strip().split("-")
            t = datetime.strptime(start.strip(), "%H:%M")
            end_t = datetime.strptime(end.strip(), "%H:%M")
            while t < end_t:
                slots.append(t.strftime("%H:%M"))
                t += timedelta(minutes=30)
        except Exception:
            continue
    return slots

# =========================================================
# LOAD EXCEL (ROBUST)
# =========================================================
@st.cache_data
def load_excel():
    if not os.path.exists(FILE_INPUT):
        return pd.DataFrame(columns=["KSM", "Dokter", "Hari", "Jenis", "Slot"])

    # --- AUTO DETECT SHEET ---
    xls = pd.ExcelFile(FILE_INPUT)
    sheet = xls.sheet_names[0]

    raw = pd.read_excel(FILE_INPUT, sheet_name=sheet)

    # --- NORMALISASI KOLOM ---
    raw.columns = [str(c).strip().upper() for c in raw.columns]

    # --- DETECT KOLOM WAJIB ---
    base_cols = raw.columns[:3]
    ksm_col, dokter_col, jenis_col = base_cols

    records = []

    for _, row in raw.iterrows():
        ksm = row[ksm_col]
        dokter = row[dokter_col]
        jenis = str(row[jenis_col]).upper()

        for hari in HARI_LIST:
            if hari in raw.columns:
                slots = parse_time_ranges(row[hari])
                for s in slots:
                    records.append({
                        "KSM": ksm,
                        "Dokter": dokter,
                        "Hari": hari,
                        "Jenis": jenis,
                        "Slot": s
                    })

    return pd.DataFrame(records, columns=["KSM", "Dokter", "Hari", "Jenis", "Slot"])

# =========================================================
# SAVE
# =========================================================
def save_to_excel(df):
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(df.columns.tolist())
    for _, r in df.iterrows():
        ws.append(list(r.values))
    wb.save(FILE_OUTPUT)

# =========================================================
# STYLE
# =========================================================
def color_slot(val):
    if val == "R":
        return "background-color:#C6EFCE"
    if val == "E":
        return "background-color:#BDD7EE"
    return "background-color:#F2F2F2"

# =========================================================
# LOAD DATA
# =========================================================
df = load_excel()

if df.empty:
    st.error("""
❌ Data tidak bisa diproses.

Periksa:
- File **jadwal hafis.xlsx** benar
- Kolom hari ada (Senin–Sabtu)
- Format jam benar (07:30-14:00)
""")
    st.stop()

# =========================================================
# UI
# =========================================================
st.title("📅 Jadwal Dokter (Excel-like)")

# FILTER
st.sidebar.header("Filter")
ksm_filter = st.sidebar.multiselect("KSM", sorted(df["KSM"].dropna().unique()))
hari_filter = st.sidebar.multiselect("Hari", HARI_LIST, default=HARI_LIST[:-1])
jenis_filter = st.sidebar.multiselect("Jenis", ["REGULER", "EKSEKUTIF"], default=["REGULER", "EKSEKUTIF"])
dokter_search = st.sidebar.text_input("Cari Dokter")

filtered = df.copy()

if ksm_filter:
    filtered = filtered[filtered["KSM"].isin(ksm_filter)]
filtered = filtered[
    filtered["Hari"].isin(hari_filter) &
    filtered["Jenis"].isin(jenis_filter)
]
if dokter_search:
    filtered = filtered[filtered["Dokter"].str.contains(dokter_search, case=False)]

# DASHBOARD
c1, c2, c3 = st.columns(3)
c1.metric("Dokter Aktif", filtered["Dokter"].nunique())
c2.metric("Total Slot", len(filtered))
c3.metric("Hari Aktif", filtered["Hari"].nunique())

# GRID
st.subheader("Tampilan Jadwal")
pivot = pd.DataFrame(index=filtered["Dokter"].unique(), columns=TIME_SLOTS)

for _, r in filtered.iterrows():
    pivot.loc[r["Dokter"], r["Slot"]] = "R" if r["Jenis"] == "REGULER" else "E"

pivot = pivot.fillna("")
st.dataframe(pivot.style.applymap(color_slot), use_container_width=True)

# SAVE
if st.button("💾 Simpan ke Excel"):
    save_to_excel(df)
    st.success("Berhasil disimpan ke jadwal coba.xlsx")
