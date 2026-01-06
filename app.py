import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from io import BytesIO
import os

# =====================================================
# CONFIG PRODUKSI
# =====================================================
st.set_page_config(
    page_title="Sistem Jadwal Dokter RS",
    layout="wide"
)

FILE_INPUT = "jadwal hafis.xlsx"
HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]

# =====================================================
# TIME SLOT
# =====================================================
def generate_time_slots(start="07:00", end="14:00", step=30):
    slots = []
    t = datetime.strptime(start, "%H:%M")
    end_t = datetime.strptime(end, "%H:%M")
    while t < end_t:
        slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=step)
    return slots

TIME_SLOTS = generate_time_slots()

# =====================================================
# PARSE JAM EXCEL
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
# SLOT → RANGE JAM (UNTUK EXPORT)
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
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    if not os.path.exists(FILE_INPUT):
        return None, pd.DataFrame()

    raw = pd.read_excel(FILE_INPUT)
    raw.columns = [c.strip().upper() for c in raw.columns]

    raw["KSM"] = raw["KSM"].ffill()
    raw["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"] = raw[
        "NAMA DOKTER SPESIALIS/ SUB SPESIALIS"
    ].ffill()

    records = []

    for _, row in raw.iterrows():
        jenis = str(row["POLI"]).upper()
        if jenis not in ["REGULER", "EKSEKUTIF"]:
            continue

        for hari in HARI_LIST:
            if hari in raw.columns:
                for slot in parse_time_ranges(row[hari]):
                    records.append({
                        "KSM": row["KSM"],
                        "Dokter": row["NAMA DOKTER SPESIALIS/ SUB SPESIALIS"],
                        "Hari": hari,
                        "Jenis": jenis,
                        "Slot": slot
                    })

    return raw, pd.DataFrame(records)

raw_df, df = load_data()

st.title("📅 Sistem Jadwal Dokter RS")

if raw_df is None or df.empty:
    st.error("❌ File jadwal hafis.xlsx tidak ditemukan atau data kosong.")
    st.stop()

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
st.sidebar.title("📋 Menu")

menu = st.sidebar.radio(
    "Navigasi",
    [
        "Dashboard",
        "Jadwal Harian",
        "📺 Mode TV / Fullscreen",
        "Jadwal Mingguan",
        "✏️ Edit Jadwal",
        "📤 Export / Cetak"
    ]
)

# =====================================================
# GRID HELPER
# =====================================================
def build_grid(df_hari):
    grid = pd.DataFrame(
        index=sorted(df_hari["Dokter"].unique()),
        columns=TIME_SLOTS
    )

    for _, r in df_hari.iterrows():
        grid.loc[r["Dokter"], r["Slot"]] = (
            "R" if r["Jenis"] == "REGULER" else "E"
        )

    grid = grid.fillna("")

    def color(v):
        if v == "R": return "background-color:#C6EFCE"
        if v == "E": return "background-color:#BDD7EE"
        return "background-color:#F2F2F2"

    return grid.style.applymap(color)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.subheader("📊 Ringkasan Jadwal")

    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Dokter", df["Dokter"].nunique())
    c2.metric("Slot Reguler", (df["Jenis"] == "REGULER").sum())
    c3.metric("Slot Eksekutif", (df["Jenis"] == "EKSEKUTIF").sum())

    chart = df.groupby(["Hari", "Jenis"]).size().reset_index(name="Slot")
    fig = px.bar(chart, x="Hari", y="Slot", color="Jenis")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# JADWAL HARIAN
# =====================================================
elif menu == "Jadwal Harian":
    st.subheader("📅 Jadwal Harian")

    tabs = st.tabs(HARI_LIST)
    for tab, hari in zip(tabs, HARI_LIST):
        with tab:
            st.dataframe(
                build_grid(df[df["Hari"] == hari]),
                use_container_width=True,
                height=420
            )

# =====================================================
# MODE TV + AUTO REFRESH
# =====================================================
elif menu == "📺 Mode TV / Fullscreen":

    if "tv_last_refresh" not in st.session_state:
        st.session_state.tv_last_refresh = datetime.now()

    def auto_refresh(seconds):
        if (datetime.now() - st.session_state.tv_last_refresh).seconds >= seconds:
            st.session_state.tv_last_refresh = datetime.now()
            st.experimental_rerun()

    st.markdown("""
        <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    hari_tv = c1.selectbox("Hari", HARI_LIST)
    refresh = c2.selectbox("Auto Refresh", [30, 60, 120], index=1)

    st.markdown(
        f"<h1 style='text-align:center;'>📺 JADWAL DOKTER – {hari_tv}</h1>",
        unsafe_allow_html=True
    )

    st.dataframe(
        build_grid(df[df["Hari"] == hari_tv]),
        use_container_width=True,
        height=600
    )

    st.info("🟩 Reguler | 🟦 Eksekutif")
    auto_refresh(refresh)

# =====================================================
# JADWAL MINGGUAN
# =====================================================
elif menu == "Jadwal Mingguan":
    st.subheader("🗓 Jadwal Mingguan")

    dokter = st.selectbox("Pilih Dokter", sorted(df["Dokter"].unique()))
    df_d = df[df["Dokter"] == dokter]

    grid = pd.DataFrame(index=TIME_SLOTS, columns=HARI_LIST)
    for _, r in df_d.iterrows():
        grid.loc[r["Slot"], r["Hari"]] = (
            "R" if r["Jenis"] == "REGULER" else "E"
        )

    st.dataframe(grid.fillna(""), use_container_width=True)

# =====================================================
# EDIT JADWAL
# =====================================================
elif menu == "✏️ Edit Jadwal":
    st.subheader("✏️ Edit Slot Jadwal")

    d = st.selectbox("Dokter", sorted(df["Dokter"].unique()))
    h = st.selectbox("Hari", HARI_LIST)
    s = st.selectbox("Jam", TIME_SLOTS)

    current = df[(df["Dokter"] == d) & (df["Hari"] == h) & (df["Slot"] == s)]
    st.info(f"Status: {current.iloc[0]['Jenis'] if not current.empty else 'KOSONG'}")

    new = st.radio("Ubah menjadi", ["KOSONG", "REGULER", "EKSEKUTIF"], horizontal=True)

    if st.button("💾 Simpan"):
        df.drop(current.index, inplace=True)

        if new != "KOSONG":
            if new == "EKSEKUTIF":
                if df[(df["Hari"] == h) & (df["Slot"] == s) & (df["Jenis"] == "EKSEKUTIF")].shape[0] >= 7:
                    st.warning("Slot EKSEKUTIF penuh")
                    st.stop()

            ksm = df[df["Dokter"] == d].iloc[0]["KSM"]
            df.loc[len(df)] = [ksm, d, h, new, s]

        st.success("Slot diperbarui")
        st.experimental_rerun()

# =====================================================
# EXPORT GRID EXCEL
# =====================================================
elif menu == "📤 Export / Cetak":
    st.subheader("📤 Export Jadwal (Grid)")

    hari = st.selectbox("Hari", HARI_LIST)

    grid = build_grid(df[df["Hari"] == hari]).data

    buffer = BytesIO()
    grid.to_excel(buffer)
    buffer.seek(0)

    st.download_button(
        "⬇️ Download Excel",
        data=buffer,
        file_name=f"jadwal_{hari}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
