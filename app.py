import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Jadwal Dokter RS", layout="wide")

FILE_INPUT = "jadwal hafis.xlsx"
FILE_OUTPUT = "jadwal coba.xlsx"

HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]

# =====================================================
# TIME SLOT GENERATOR
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
# PARSE RANGE JAM → SLOT
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
# SLOT → RANGE JAM (UNTUK SAVE)
# =====================================================
def slots_to_ranges(slots):
    if not slots:
        return "-"

    times = sorted(datetime.strptime(s, "%H:%M") for s in slots)
    ranges = []

    start = prev = times[0]
    for t in times[1:]:
        if t - prev == timedelta(minutes=30):
            prev = t
        else:
            ranges.append((start, prev + timedelta(minutes=30)))
            start = prev = t
    ranges.append((start, prev + timedelta(minutes=30)))

    return ", ".join(
        f"{s.strftime('%H:%M').replace(':','.')}-"
        f"{e.strftime('%H:%M').replace(':','.')}"
        for s, e in ranges
    )

# =====================================================
# LOAD & PARSE EXCEL
# =====================================================
@st.cache_data
def load_excel():
    if not os.path.exists(FILE_INPUT):
        return None, pd.DataFrame()

    raw = pd.read_excel(FILE_INPUT)
    raw.columns = [c.strip().upper() for c in raw.columns]

    raw["KSM"] = raw["KSM"].ffill()
    raw["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"] = \
        raw["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"].ffill()

    records = []

    for idx, row in raw.iterrows():
        jenis = str(row["POLI"]).upper()
        if jenis not in ["REGULER", "EKSEKUTIF"]:
            continue

        for hari in HARI_LIST:
            if hari in raw.columns:
                for slot in parse_time_ranges(row[hari]):
                    records.append({
                        "RowIndex": idx,
                        "KSM": row["KSM"],
                        "Dokter": row["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"],
                        "Hari": hari,
                        "Jenis": jenis,
                        "Slot": slot
                    })

    return raw, pd.DataFrame(records)

raw_df, df = load_excel()

st.title("📅 Sistem Jadwal Dokter (RS Grade)")

if raw_df is None or df.empty:
    st.error("❌ Data tidak dapat dimuat. Periksa file Excel.")
    st.stop()

# =====================================================
# GRID SEMUA HARI (TAB)
# =====================================================
st.subheader("📊 Jadwal Dokter")

tabs = st.tabs(HARI_LIST)

def build_grid(df_hari):
    pivot = pd.DataFrame(
        index=sorted(df_hari["Dokter"].unique()),
        columns=TIME_SLOTS
    )

    for _, r in df_hari.iterrows():
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

    return pivot.style.applymap(color)

for tab, hari in zip(tabs, HARI_LIST):
    with tab:
        df_hari = df[df["Hari"] == hari]
        if df_hari.empty:
            st.info(f"Tidak ada jadwal {hari}")
        else:
            st.dataframe(
                build_grid(df_hari),
                use_container_width=True,
                height=500
            )

# =====================================================
# EDIT SLOT
# =====================================================
st.divider()
st.subheader("✏️ Edit Slot Jadwal")

c1, c2, c3 = st.columns(3)

dokter = c1.selectbox("Dokter", sorted(df["Dokter"].unique()))
hari = c2.selectbox("Hari", HARI_LIST)
slot = c3.selectbox("Jam", TIME_SLOTS)

current = df[
    (df["Dokter"] == dokter) &
    (df["Hari"] == hari) &
    (df["Slot"] == slot)
]

st.info(
    f"Status saat ini: "
    f"**{current.iloc[0]['Jenis'] if not current.empty else 'KOSONG'}**"
)

new_status = st.radio(
    "Ubah menjadi:",
    ["KOSONG", "REGULER", "EKSEKUTIF"],
    horizontal=True
)

if st.button("💾 Simpan Perubahan Slot"):
    df.drop(current.index, inplace=True)

    if new_status != "KOSONG":
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
        df.loc[len(df)] = [None, ksm, dokter, hari, new_status, slot]

    st.success("✅ Slot berhasil diperbarui")
    st.experimental_rerun()

# =====================================================
# SAVE BACK TO EXCEL
# =====================================================
st.divider()
st.subheader("💾 Simpan ke Excel")

if st.button("📤 Simpan ke jadwal coba.xlsx"):
    out = raw_df.copy()

    for idx, row in out.iterrows():
        jenis = str(row["POLI"]).upper()
        if jenis not in ["REGULER", "EKSEKUTIF"]:
            continue

        dokter = row["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"]

        for hari in HARI_LIST:
            slots = df[
                (df["Dokter"] == dokter) &
                (df["Hari"] == hari) &
                (df["Jenis"] == jenis)
            ]["Slot"].tolist()

            out.at[idx, hari] = slots_to_ranges(slots)

    out.to_excel(FILE_OUTPUT, index=False)
    st.success("✅ Jadwal berhasil disimpan ke jadwal coba.xlsx")
