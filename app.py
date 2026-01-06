import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Jadwal Dokter", layout="wide")

FILE_INPUT = "jadwal hafis.xlsx"

HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]

# =====================================================
# TIME SLOT
# =====================================================
def generate_time_slots(start="07:00", end="14:00", step=30):
    slots = []
    t = datetime.strptime(start, "%H:%M")
    end_t = datetime.strptime(end, "%H:%M")
    while t <= end_t:
        slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=step)
    return slots

TIME_SLOTS = generate_time_slots()

# =====================================================
# PARSE JAM
# =====================================================
def parse_time_ranges(cell):
    if pd.isna(cell):
        return []

    text = str(cell).replace(".", ":").strip()
    if text in ["", "-"]:
        return []

    slots = []
    for part in text.split(","):
        try:
            start, end = part.strip().split("-")
            t = datetime.strptime(start.strip(), "%H:%M")
            end_t = datetime.strptime(end.strip(), "%H:%M")
            while t < end_t:
                slots.append(t.strftime("%H:%M"))
                t += timedelta(minutes=30)
        except Exception:
            continue
    return slots

# =====================================================
# LOAD EXCEL (FIX SESUAI STRUKTUR RS)
# =====================================================
@st.cache_data
def load_excel():
    if not os.path.exists(FILE_INPUT):
        return pd.DataFrame()

    raw = pd.read_excel(FILE_INPUT)
    raw.columns = [c.strip().upper() for c in raw.columns]

    # Forward fill KSM & Dokter
    raw["KSM"] = raw["KSM"].ffill()
    raw["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"] = \
        raw["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"].ffill()

    records = []

    for _, row in raw.iterrows():
        jenis = str(row["POLI"]).upper()

        if jenis not in ["REGULER", "EKSEKUTIF"]:
            continue  # skip JAM KERJA

        for hari in HARI_LIST:
            if hari in raw.columns:
                slots = parse_time_ranges(row[hari])
                for s in slots:
                    records.append({
                        "KSM": row["KSM"],
                        "Dokter": row["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"],
                        "Hari": hari,
                        "Jenis": jenis,
                        "Slot": s
                    })

    return pd.DataFrame(records)

# =====================================================
# LOAD DATA
# =====================================================
df = load_excel()

st.title("📅 Jadwal Dokter (Excel-like)")

if df.empty:
    st.error("""
❌ Jadwal tidak terbentuk.

Namun file Excel SUDAH terbaca.
Ini berarti format jam tidak sesuai.

Contoh format yang benar:
- 07:30-14:00
- 08.30-10.30
""")
    st.stop()

# =====================================================
# FILTER
# =====================================================
st.sidebar.header("Filter")

ksm_filter = st.sidebar.multiselect(
    "KSM", sorted(df["KSM"].dropna().unique())
)

hari_filter = st.sidebar.multiselect(
    "Hari", HARI_LIST, default=HARI_LIST[:-1]
)

jenis_filter = st.sidebar.multiselect(
    "Jenis", ["REGULER", "EKSEKUTIF"],
    default=["REGULER", "EKSEKUTIF"]
)

dokter_search = st.sidebar.text_input("Cari Dokter")

filtered = df.copy()

if ksm_filter:
    filtered = filtered[filtered["KSM"].isin(ksm_filter)]

filtered = filtered[
    filtered["Hari"].isin(hari_filter) &
    filtered["Jenis"].isin(jenis_filter)
]

if dokter_search:
    filtered = filtered[
        filtered["Dokter"].str.contains(dokter_search, case=False)
    ]

# =====================================================
# GRID EXCEL-LIKE
# =====================================================
st.subheader("📊 Jadwal Dokter")

pivot = pd.DataFrame(
    index=sorted(filtered["Dokter"].unique()),
    columns=TIME_SLOTS
)

for _, r in filtered.iterrows():
    pivot.loc[r["Dokter"], r["Slot"]] = (
        "R" if r["Jenis"] == "REGULER" else "E"
    )

pivot = pivot.fillna("")

def color(val):
    if val == "R":
        return "background-color:#C6EFCE"
    if val == "E":
        return "background-color:#BDD7EE"
    return "background-color:#F2F2F2"

st.dataframe(
    pivot.style.applymap(color),
    use_container_width=True,
    height=500
)
