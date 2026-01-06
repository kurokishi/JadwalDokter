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
        except:
            continue
    return slots

# =====================================================
# LOAD EXCEL (SESUI FILE RS)
# =====================================================
@st.cache_data
def load_excel():
    if not os.path.exists(FILE_INPUT):
        return pd.DataFrame()

    raw = pd.read_excel(FILE_INPUT)
    raw.columns = [c.strip().upper() for c in raw.columns]

    raw["KSM"] = raw["KSM"].ffill()
    raw["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"] = \
        raw["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"].ffill()

    records = []

    for _, row in raw.iterrows():
        jenis = str(row["POLI"]).upper()
        if jenis not in ["REGULER", "EKSEKUTIF"]:
            continue

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

st.title("📅 Jadwal Dokter (Editable Slot)")

if df.empty:
    st.error("❌ Jadwal tidak terbentuk dari Excel.")
    st.stop()

# =====================================================
# GRID
# =====================================================
st.subheader("📊 Jadwal (Grid Waktu)")

pivot = pd.DataFrame(
    index=sorted(df["Dokter"].unique()),
    columns=TIME_SLOTS
)

for _, r in df.iterrows():
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

st.dataframe(pivot.style.applymap(color), use_container_width=True)

# =====================================================
# SLOT EDITOR (POINT 1)
# =====================================================
st.divider()
st.subheader("✏️ Edit Slot Jadwal")

col1, col2, col3 = st.columns(3)

dokter = col1.selectbox("Dokter", sorted(df["Dokter"].unique()))
hari = col2.selectbox("Hari", HARI_LIST)
slot = col3.selectbox("Slot Waktu", TIME_SLOTS)

current = df[
    (df["Dokter"] == dokter) &
    (df["Hari"] == hari) &
    (df["Slot"] == slot)
]

current_status = (
    current.iloc[0]["Jenis"] if not current.empty else "KOSONG"
)

st.info(f"Status saat ini: **{current_status}**")

new_status = st.radio(
    "Ubah menjadi:",
    ["KOSONG", "REGULER", "EKSEKUTIF"],
    horizontal=True
)

if st.button("💾 Simpan Perubahan"):
    # Hapus slot lama
    df.drop(current.index, inplace=True)

    if new_status != "KOSONG":
        # Validasi eksekutif
        if new_status == "EKSEKUTIF":
            count = df[
                (df["Hari"] == hari) &
                (df["Slot"] == slot) &
                (df["Jenis"] == "EKSEKUTIF")
            ].shape[0]

            if count >= 7:
                st.warning("❌ Slot EKSEKUTIF sudah penuh (maks 7)")
                st.stop()

        ksm = df[df["Dokter"] == dokter].iloc[0]["KSM"]
        df.loc[len(df)] = [ksm, dokter, hari, new_status, slot]

    st.success("✅ Slot berhasil diperbarui")
    st.experimental_rerun()
