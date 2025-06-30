# Dashboard Monitoring Pengolahan Susenas Maret 2025
# BPS Kabupaten Dharmasraya
# Dalam Rangka Pelaksanaan Aktualisasi Latsar CPNS BPS 2025
# Taufiq Agung Kurniawan - 200204232024121002

# 0. Import Library
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    worksheet="Updating",
    ttl = 1
)

# Print results
st.dataframe(df)
