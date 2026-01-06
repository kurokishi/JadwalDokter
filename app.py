import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import plotly.express as px
from openpyxl import Workbook
import os

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Jadwal Dokter",
    layout="wide",
    initial_sidebar_state="expanded"
)

FILE_INPUT = "/mnt/data/jadwal hafis.xlsx"
FILE_OUTPUT = "/mnt/data/jadwal coba.xlsx"

HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]

# =========================================================
# HELPER FUNCTIONS
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


def parse_time_ranges(cell):
    """
    "08.30-09.30, 10.30-11.30" → ['08:30','09:00','09:30','10:30','11:00','11:30']
    """
    if pd.isna(cell) or cell == "-" or str(cell).strip() == "":
        return []

    cell = str(cell).replace(".", ":")
    ranges = cell.split(",")

    slots = []
    for r in ranges:
        start, end = r.strip().split("-")
        t = datetime.strptime(start.strip(), "%H:%M")
        end_t = datetime.strptime(end.strip(), "%H:%M")
        while t < end_t:
            slots.append(t.strftime("%H:%M"))
            t += timedelta(minutes=30)
    return slots


@st.cache_data
def load_excel():
    if not os.path.exists(FILE_INPUT):
        return pd.DataFrame()

    df = pd.read_excel(FILE_INPUT, sheet_name="Sheet1")
    records = []

    for _, row in df.iterrows():
        ksm = row.iloc[0]
        dokter = row.iloc[1]
        poli = row.iloc[2]

        for hari in HARI_LIST:
            if hari in row:
                slots = parse_time_ranges(row[hari])
                for s in slots:
                    records.append({
                        "KSM": ksm,
                        "Dokter": dokter,
                        "Hari": hari,
                        "Jenis": poli.upper(),
                        "Slot": s
                    })

    return pd.DataFrame(records)


def save_to_excel(df):
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    headers = ["KSM", "Dokter", "Hari", "Jenis", "Slot"]
    ws.append(headers)

    for _, r in df.iterrows():
        ws.append(list(r.values))

    wb.save(FILE_OUTPUT)


def color_slot(val):
    if val == "R":
        return "background-color: #C6EFCE"
    if val == "E":
        return "background-color: #BDD7EE"
    return "background-color: #F2F2F2"


# =========================================================
# LOAD DATA
# =========================================================
df = load_excel()

st.title("📅 Aplikasi Penjadwalan Dokter")
st.caption("Tampilan mirip Excel | Reguler & Eksekutif | Editable")

# =========================================================
# SIDEBAR FILTER
# =========================================================
st.sidebar.header("🔎 Filter")

ksm_filter = st.sidebar.multiselect(
    "Pilih KSM",
    sorted(df["KSM"].unique()) if not df.empty else []
)

hari_filter = st.sidebar.multiselect(
    "Hari",
    ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"],
    default=["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
)

if st.sidebar.checkbox("Aktifkan Sabtu"):
    hari_filter.append("SABTU")

jenis_filter = st.sidebar.multiselect(
    "Jenis Layanan",
    ["REGULER", "EKSEKUTIF"],
    default=["REGULER", "EKSEKUTIF"]
)

dokter_search = st.sidebar.text_input("Cari Dokter")

# =========================================================
# FILTER DATA
# =========================================================
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

# =========================================================
# DASHBOARD OVERVIEW
# =========================================================
col1, col2, col3 = st.columns(3)

col1.metric("Jumlah Dokter Aktif", filtered["Dokter"].nunique())
col2.metric("Total Slot", len(filtered))
col3.metric("Hari Aktif", filtered["Hari"].nunique())

chart = filtered.groupby("Hari").size().reset_index(name="Slot")
fig = px.bar(chart, x="Hari", y="Slot", title="Ketersediaan Slot per Hari")
st.plotly_chart(fig, use_container_width=True)

# =========================================================
# GRID EXCEL-LIKE VIEW
# =========================================================
st.subheader("📊 Tampilan Jadwal (Excel-like)")

if not filtered.empty:
    pivot = pd.DataFrame(index=filtered["Dokter"].unique(), columns=TIME_SLOTS)

    for _, r in filtered.iterrows():
        pivot.loc[r["Dokter"], r["Slot"]] = "R" if r["Jenis"] == "REGULER" else "E"

    pivot = pivot.fillna("")

    st.dataframe(
        pivot.style.applymap(color_slot),
        use_container_width=True,
        height=500
    )
else:
    st.info("Tidak ada data sesuai filter.")

# =========================================================
# EDIT MODE
# =========================================================
st.divider()
st.subheader("✏️ Edit / Tambah Jadwal")

with st.form("edit_form"):
    col1, col2, col3 = st.columns(3)

    ksm = col1.text_input("KSM")
    dokter = col2.text_input("Nama Dokter")
    hari = col3.selectbox("Hari", HARI_LIST)

    col4, col5 = st.columns(2)
    jenis = col4.selectbox("Jenis", ["REGULER", "EKSEKUTIF"])
    slots = col5.multiselect("Slot Waktu", TIME_SLOTS)

    submitted = st.form_submit_button("➕ Tambahkan Jadwal")

    if submitted:
        if jenis == "EKSEKUTIF":
            for s in slots:
                count = df[
                    (df["Hari"] == hari) &
                    (df["Slot"] == s) &
                    (df["Jenis"] == "EKSEKUTIF")
                ].shape[0]
                if count >= 7:
                    st.warning(f"Slot {s} di {hari} sudah penuh (maks 7 Eksekutif)")
                    st.stop()

        for s in slots:
            df.loc[len(df)] = [ksm, dokter, hari, jenis, s]

        st.success("Jadwal berhasil ditambahkan!")

# =========================================================
# ACTION BUTTONS
# =========================================================
col1, col2 = st.columns(2)

if col1.button("💾 Simpan ke Excel"):
    save_to_excel(df)
    st.success(f"Data tersimpan ke {FILE_OUTPUT}")

if col2.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()
