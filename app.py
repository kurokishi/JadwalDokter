import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from openpyxl import Workbook
import plotly.express as px
import os

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Jadwal Dokter",
    layout="wide"
)

FILE_INPUT = "jadwal hafis.xlsx"
FILE_OUTPUT = "jadwal coba.xlsx"

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
    if pd.isna(cell):
        return []

    cell = str(cell).strip()
    if cell == "-" or cell == "":
        return []

    cell = cell.replace(".", ":")
    parts = cell.split(",")

    slots = []
    for p in parts:
        try:
            start, end = p.strip().split("-")
            t = datetime.strptime(start.strip(), "%H:%M")
            end_t = datetime.strptime(end.strip(), "%H:%M")
            while t < end_t:
                slots.append(t.strftime("%H:%M"))
                t += timedelta(minutes=30)
        except Exception:
            continue
    return slots


@st.cache_data
def load_excel():
    if not os.path.exists(FILE_INPUT):
        return pd.DataFrame(columns=["KSM", "Dokter", "Hari", "Jenis", "Slot"])

    try:
        raw = pd.read_excel(FILE_INPUT, sheet_name="Sheet1")
    except Exception:
        return pd.DataFrame(columns=["KSM", "Dokter", "Hari", "Jenis", "Slot"])

    records = []

    for _, row in raw.iterrows():
        ksm = row.iloc[0]
        dokter = row.iloc[1]
        jenis = str(row.iloc[2]).upper()

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


def save_to_excel(df):
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    ws.append(df.columns.tolist())
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
# LOAD DATA (SAFE)
# =========================================================
df = load_excel()

REQUIRED_COLS = {"KSM", "Dokter", "Hari", "Jenis", "Slot"}

if df.empty or not REQUIRED_COLS.issubset(df.columns):
    st.error("""
❌ Data tidak valid atau file Excel belum siap.

Pastikan:
- File **jadwal hafis.xlsx** ada di folder app
- Sheet bernama **Sheet1**
- Kolom hari: SENIN – SABTU
""")
    st.stop()

# =========================================================
# UI HEADER
# =========================================================
st.title("📅 Sistem Penjadwalan Dokter")
st.caption("Tampilan Excel-like | Reguler & Eksekutif")

# =========================================================
# SIDEBAR FILTER
# =========================================================
st.sidebar.header("🔎 Filter")

ksm_filter = st.sidebar.multiselect(
    "KSM",
    sorted(df["KSM"].dropna().unique())
)

hari_filter = st.sidebar.multiselect(
    "Hari",
    ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"],
    default=["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
)

if st.sidebar.checkbox("Aktifkan Sabtu"):
    hari_filter.append("SABTU")

jenis_filter = st.sidebar.multiselect(
    "Jenis",
    ["REGULER", "EKSEKUTIF"],
    default=["REGULER", "EKSEKUTIF"]
)

dokter_search = st.sidebar.text_input("Cari Dokter")

# =========================================================
# FILTER DATA (SAFE)
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
        filtered["Dokter"].str.contains(dokter_search, case=False, na=False)
    ]

# =========================================================
# DASHBOARD
# =========================================================
c1, c2, c3 = st.columns(3)
c1.metric("Dokter Aktif", filtered["Dokter"].nunique())
c2.metric("Total Slot", len(filtered))
c3.metric("Hari Aktif", filtered["Hari"].nunique())

chart = filtered.groupby("Hari").size().reset_index(name="Slot")
fig = px.bar(chart, x="Hari", y="Slot", title="Distribusi Slot per Hari")
st.plotly_chart(fig, use_container_width=True)

# =========================================================
# EXCEL-LIKE GRID
# =========================================================
st.subheader("📊 Jadwal (Grid Waktu)")

if not filtered.empty:
    pivot = pd.DataFrame(
        index=sorted(filtered["Dokter"].unique()),
        columns=TIME_SLOTS
    )

    for _, r in filtered.iterrows():
        pivot.loc[r["Dokter"], r["Slot"]] = (
            "R" if r["Jenis"] == "REGULER" else "E"
        )

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
st.subheader("✏️ Tambah / Edit Jadwal")

with st.form("edit_form"):
    col1, col2, col3 = st.columns(3)
    ksm = col1.text_input("KSM")
    dokter = col2.text_input("Nama Dokter")
    hari = col3.selectbox("Hari", HARI_LIST)

    col4, col5 = st.columns(2)
    jenis = col4.selectbox("Jenis", ["REGULER", "EKSEKUTIF"])
    slots = col5.multiselect("Slot Waktu", TIME_SLOTS)

    submit = st.form_submit_button("➕ Tambahkan")

    if submit:
        if jenis == "EKSEKUTIF":
            for s in slots:
                count = df[
                    (df["Hari"] == hari) &
                    (df["Slot"] == s) &
                    (df["Jenis"] == "EKSEKUTIF")
                ].shape[0]
                if count >= 7:
                    st.warning(f"Slot {s} hari {hari} sudah penuh (maks 7)")
                    st.stop()

        for s in slots:
            df.loc[len(df)] = [ksm, dokter, hari, jenis, s]

        st.success("Jadwal berhasil ditambahkan")

# =========================================================
# ACTIONS
# =========================================================
c1, c2 = st.columns(2)

if c1.button("💾 Simpan ke Excel"):
    save_to_excel(df)
    st.success("Data berhasil disimpan ke jadwal coba.xlsx")

if c2.button("🔄 Refresh"):
    st.cache_data.clear()
    st.experimental_rerun()
