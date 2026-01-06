import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import os

st.set_page_config(page_title="Jadwal Dokter", layout="wide")

FILE_INPUT = "jadwal hafis.xlsx"

HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]

# ======================================================
# TIME SLOT
# ======================================================
def generate_time_slots(start="07:00", end="14:00", step=30):
    slots = []
    t = datetime.strptime(start, "%H:%M")
    end_t = datetime.strptime(end, "%H:%M")
    while t <= end_t:
        slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=step)
    return slots

TIME_SLOTS = generate_time_slots()

# ======================================================
# PARSE JAM
# ======================================================
def parse_time_ranges(text):
    if pd.isna(text):
        return []

    text = str(text).upper().replace(".", ":")
    if text.strip() in ["", "-"]:
        return []

    ranges = re.findall(r"\d{2}:\d{2}\s*-\s*\d{2}:\d{2}", text)

    slots = []
    for r in ranges:
        start, end = r.split("-")
        t = datetime.strptime(start.strip(), "%H:%M")
        end_t = datetime.strptime(end.strip(), "%H:%M")
        while t < end_t:
            slots.append(t.strftime("%H:%M"))
            t += timedelta(minutes=30)
    return slots

# ======================================================
# LOAD EXCEL (SUPER ROBUST)
# ======================================================
@st.cache_data
def load_excel():
    if not os.path.exists(FILE_INPUT):
        return pd.DataFrame(), None

    xls = pd.ExcelFile(FILE_INPUT)
    sheet = xls.sheet_names[0]
    raw = pd.read_excel(FILE_INPUT, sheet_name=sheet)

    raw.columns = [str(c).strip().upper() for c in raw.columns]

    records = []

    # ASSUME 3 KOLOM PERTAMA = IDENTITAS
    id_cols = raw.columns[:3]
    other_cols = raw.columns[3:]

    for _, row in raw.iterrows():
        ksm = row[id_cols[0]]
        dokter = row[id_cols[1]]
        jenis = row[id_cols[2]]

        for col in other_cols:
            cell = str(row[col]).upper()
            for hari in HARI_LIST:
                if hari in cell:
                    slots = parse_time_ranges(cell)
                    for s in slots:
                        records.append({
                            "KSM": ksm,
                            "Dokter": dokter,
                            "Hari": hari,
                            "Jenis": str(jenis).upper(),
                            "Slot": s
                        })

    return pd.DataFrame(records), raw

# ======================================================
# LOAD
# ======================================================
df, raw_df = load_excel()

st.title("📅 Jadwal Dokter (Excel-like)")

# ======================================================
# DEBUG VIEW (INI KUNCI)
# ======================================================
with st.expander("🔍 Lihat Data Excel Asli (Debug)"):
    if raw_df is not None:
        st.dataframe(raw_df, use_container_width=True)
    else:
        st.warning("File Excel belum ditemukan.")

# ======================================================
# JIKA DATA KOSONG → TETAP JALAN
# ======================================================
if df.empty:
    st.warning("""
⚠️ Jadwal belum berhasil diparse otomatis.

Silakan cek:
- Apakah hari (SENIN–SABTU) tertulis di dalam sel
- Format jam: 07.30-14.00 atau 07:30-14:00

Data Excel asli tetap ditampilkan di atas.
""")
    st.stop()

# ======================================================
# FILTER
# ======================================================
st.sidebar.header("Filter")
ksm_filter = st.sidebar.multiselect("KSM", sorted(df["KSM"].dropna().unique()))
hari_filter = st.sidebar.multiselect("Hari", HARI_LIST, default=HARI_LIST[:-1])
jenis_filter = st.sidebar.multiselect("Jenis", df["Jenis"].unique().tolist())
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

# ======================================================
# GRID
# ======================================================
st.subheader("📊 Jadwal (Grid Waktu)")

pivot = pd.DataFrame(index=filtered["Dokter"].unique(), columns=TIME_SLOTS)

for _, r in filtered.iterrows():
    pivot.loc[r["Dokter"], r["Slot"]] = "✔"

pivot = pivot.fillna("")
st.dataframe(pivot, use_container_width=True)
