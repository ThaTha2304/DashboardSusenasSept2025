# Dashboard Monitoring Pengolahan Susenas Maret 2025
# BPS Kabupaten Dharmasraya
# Dalam Rangka Pelaksanaan Aktualisasi Latsar CPNS BPS 2025
# Taufiq Agung Kurniawan - 200204232024121002

import streamlit as st

st.set_page_config(layout="wide")

# Define pages
dash_updating = st.Page("DashUpdating.py", title="Updating", icon="📝")
dash_pendataan = st.Page("DashPendataan.py", title="Pendataan", icon="📊")
dash_petugas = st.Page("DashPetugas.py", title="Rekapitulasi Petugas", icon="😃")

# Set up navigation (Section)
pg = st.navigation({
    "Pengolahan": [dash_updating, dash_pendataan],
    "Rekap Petugas" : [dash_petugas]
})
st.logo("assets/img/logo-bps-oke.png", size="large")
st.title("Dashboard Pengolahan Susenas Maret 2025")
st.subheader("BPS Kabupaten Dharmasraya")

st.sidebar.button("Reset")

pg.run()