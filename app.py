import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.express as px

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Sistem Jadwal Dokter RS", layout="wide")

FILE_INPUT = "jadwal hafis.xlsx"
FILE_OUTPUT = "jadwal coba.xlsx"

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
# PARSE JAM EXCEL → SLOT 30 MENIT
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
# SLOT → RANGE JAM (UNTUK SAVE EXCEL)
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
# POINT 1 – GRID SEMUA HARI (TAB)
# =====================================================
st.subheader("📊 Jadwal Harian")

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
            st.dataframe(build_grid(df_hari), use_container_width=True, height=450)

# =====================================================
# POINT 2 – EDIT SLOT
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
# POINT 4 – JADWAL MINGGUAN & CETAK
# =====================================================
st.divider()
st.subheader("📅 Jadwal Mingguan")

mode = st.radio("Lihat berdasarkan:", ["Dokter", "KSM / Poli"], horizontal=True)

if mode == "Dokter":
    target = st.selectbox("Pilih Dokter", sorted(df["Dokter"].unique()))
    df_week = df[df["Dokter"] == target]
else:
    target = st.selectbox("Pilih KSM / Poli", sorted(df["KSM"].unique()))
    df_week = df[df["KSM"] == target]

def build_weekly_grid(df_week):
    grid = pd.DataFrame(index=TIME_SLOTS, columns=HARI_LIST)

    for _, r in df_week.iterrows():
        grid.loc[r["Slot"], r["Hari"]] = (
            "R" if r["Jenis"] == "REGULER" else "E"
        )

    grid = grid.fillna("")

    def color(val):
        if val == "R":
            return "background-color:#C6EFCE"
        if val == "E":
            return "background-color:#BDD7EE"
        return "background-color:#F9F9F9"

    return grid.style.applymap(color)

if not df_week.empty:
    st.dataframe(build_weekly_grid(df_week), use_container_width=True, height=450)

    html = build_weekly_grid(df_week).to_html()
    st.download_button(
        "⬇️ Download Jadwal Mingguan (HTML – Siap Cetak)",
        html,
        file_name="jadwal_mingguan.html",
        mime="text/html"
    )
else:
    st.warning("Tidak ada data jadwal.")

# =====================================================
# POINT 5 – ANALITIK BEBAN DOKTER
# =====================================================
st.divider()
st.subheader("📊 Analitik Beban Dokter")

df["Jam"] = 0.5

summary = (
    df.groupby(["Dokter", "Jenis"])
      .agg(Total_Jam=("Jam", "sum"))
      .reset_index()
)

pivot_load = summary.pivot_table(
    index="Dokter",
    columns="Jenis",
    values="Total_Jam",
    fill_value=0
)

pivot_load["TOTAL"] = pivot_load.sum(axis=1)
pivot_load = pivot_load.reset_index()

MAX_JAM = st.slider("Ambang overload (jam/minggu)", 20, 60, 40)

def highlight(row):
    return ["background-color:#F8CBAD" if row["TOTAL"] > MAX_JAM else "" for _ in row]

st.dataframe(
    pivot_load.style.apply(highlight, axis=1),
    use_container_width=True
)

fig = px.bar(
    pivot_load,
    x="Dokter",
    y=["REGULER", "EKSEKUTIF"],
    title="Beban Jam Dokter per Minggu",
    labels={"value": "Jam", "variable": "Jenis"}
)

st.plotly_chart(fig, use_container_width=True)

over = pivot_load[pivot_load["TOTAL"] > MAX_JAM]
if not over.empty:
    st.warning(f"⚠️ {len(over)} dokter melebihi {MAX_JAM} jam/minggu")
else:
    st.success("✅ Tidak ada dokter overload")

# =====================================================
# POINT 2 – SAVE BACK TO EXCEL
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
