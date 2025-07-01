import streamlit as st
import pandas as pd
import Connection

# Add Columns
col1, col2, col3, col4 = st.columns(4, border=True)
col11, col12 = st.columns(2, border = True)

updatingData = Connection.getDataUpdating()

updatingData[["Kode Provinsi", "Kode Kabupaten"]] = updatingData[["Kode Provinsi", "Kode Kabupaten"]].astype(int).astype(str)

updatingData["Kode Kecamatan"] = updatingData["Kode Kecamatan"].apply(lambda x: f"{int(x):03d}")
updatingData["Kode Nagari"] = updatingData["Kode Nagari"].apply(lambda x: f"{int(x):03d}")

# Menampilkan jumlah dokumen diterima IPDS
jumlah_masuk = updatingData["Tanggal Diterima"].notna().sum()
with col1:
    st.metric(label="Jumlah Dokumen Masuk IPDS", value=jumlah_masuk)

# Menampilkan jumlah dokumen selesai entri
jumlah_sudah_entri = updatingData["Tanggal Selesai Entri"].notna().sum()
with col2:
    st.metric(label="Jumlah Dokumen Selesai Entri", value=jumlah_sudah_entri)

# Menampilkan jumlah dokumen clean
jumlah_clean = (updatingData["Status Dokumen"] == "Clean").sum()

with col3:
    st.metric(label="Jumlah Dokumen Clean", value=jumlah_clean)

# Menampilkan jumlah dokumen error
jumlah_error = (updatingData["Status Dokumen"] == "Error").sum()
with col4:
    st.metric(label="Jumlah Dokumen Error", value=jumlah_error)

st.write((updatingData["Tanggal Selesai Entri"].notnull().sum()))
st.write()