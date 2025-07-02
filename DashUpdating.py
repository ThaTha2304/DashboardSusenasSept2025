import streamlit as st
import pandas as pd
import Connection
import folium
import json
from streamlit_folium import st_folium

# Define Layers
kabupaten = "assets\geojson\Batas Kabupaten.geojson"
kecamatan = "assets\geojson\Batas Kecamatan.geojson"
nagari = "assets\geojson\Batas Nagari.geojson"
bs = "assets\geojson\Batas BS.geojson"

# Define Data
updatingData = Connection.getDataUpdating()

# Cleaning Updating Data
updatingData[["Kode Provinsi", "Kode Kabupaten"]] = updatingData[["Kode Provinsi", "Kode Kabupaten"]].astype(int).astype(str)
updatingData["Kode Kecamatan"] = updatingData["Kode Kecamatan"].apply(lambda x: f"{int(x):03d}")
updatingData["Kode Nagari"] = updatingData["Kode Nagari"].apply(lambda x: f"{int(x):03d}")
updatingData["idKab"] = updatingData["Kode SLS"].str[:4]
updatingData["idKec"] = updatingData["Kode SLS"].str[:7]
updatingData["idNag"] = updatingData["Kode SLS"].str[:10]

# Tambah selection di sidebar
with st.sidebar:
    st.divider()
    level = st.selectbox(
        "Level Data:",
        ("Kabupaten", "Kecamatan", "Nagari")
    )

    st.write(f"You selected: {level}")

    filter_data = st.selectbox(
        "Filter data:",
        ("Dokumen Masuk IPDS", "Dokumen Clean")
    )

# Fungsi buat agregat data
def show_data(level_data):
    # Seleksi level_data
    if level_data == "Kabupaten":
        total = updatingData.groupby("idKab")["Status Dokumen"].count()

        clean = updatingData[updatingData["Status Dokumen"] == "Clean"].groupby("idKab")["Status Dokumen"].count()

        summary = pd.DataFrame({
            "Total" : total,
            "Clean" : clean
        })

        summary["Persentase Clean"] = (summary["Clean"] / summary["Total"])*100
        summary["Persentase Clean"] = summary["Persentase Clean"].round(2)
        summary = summary.reset_index()

    elif level_data == "Kecamatan":
        temp = updatingData[updatingData["Status Dokumen"] == "Clean"]
        summary = temp.groupby("idKec")["Status Dokumen"].count()

    elif level_data == "Nagari":
        temp = updatingData[updatingData["Status Dokumen"] == "Clean"]
        summary = temp.groupby("idNag")["Status Dokumen"].count()
    
    return summary

# Fungsi buat tampilin peta
def show_map(level_data) :
    # Seleksi level_data
    if level_data == "Kabupaten":
        with open(kabupaten, encoding="utf-8") as f:
            geojson = json.load(f)
    elif level_data == "Kecamatan":
        with open(kecamatan, encoding="utf-8") as f:
            geojson = json.load(f)
    elif level_data == "Nagari":
        with open(nagari, encoding="utf-8") as f:
            geojson = json.load(f)
    
    # Tampilkan peta
    m = folium.Map(location=[-1.100, 101.7], zoom_start=7)

    x = "idkab"
    # Tambah Choropleth Map
    folium.Choropleth(
        geo_data=geojson,
        data=show_data(level_data),
        columns=["idKab", "Persentase Clean"],
        key_on=f"feature.properties.{x}"
    ).add_to(m)

    map = st_folium(m, width=725)
    return map    

st.write(f"Data: {filter_data}, Level: {level}")

# Add Columns
col1, col2, col3, col4 = st.columns(4, border=True)
col11, col12 = st.columns(2, border = True)


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


# Menampilkan peta
with col11:
    st.write(f"Menampilkan data: {filter_data}, pada Level: {level}")
    show_map(level)

st.write(updatingData)