import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import Connection
import json
import plotly.express as px
from streamlit_folium import st_folium
from datetime import date

# Define Layers
kabupaten = "assets\geojson\Batas Kabupaten.geojson"
kecamatan = "assets\geojson\Batas Kecamatan.geojson"
nagari = "assets\geojson\Batas Nagari.geojson"
bs = "assets\geojson\Batas BS.geojson"

# Define Data
updatingData = Connection.getDataUpdating()
start_date = date(2025, 2, 1)
end_date = date(2025, 2, 28)

# Cleaning Updating Data
updatingData[["Kode Provinsi", "Kode Kabupaten"]] = updatingData[["Kode Provinsi", "Kode Kabupaten"]].astype(int).astype(str)
updatingData["Kode Kecamatan"] = updatingData["Kode Kecamatan"].apply(lambda x: f"{int(x):03d}")
updatingData["Kode Nagari"] = updatingData["Kode Nagari"].apply(lambda x: f"{int(x):03d}")
updatingData["idkab"] = updatingData["Kode SLS"].str[:4]
updatingData["idkec"] = updatingData["Kode SLS"].str[:7]
updatingData["iddesa"] = updatingData["Kode SLS"].str[:10]
updatingData = updatingData.rename(columns = {"Kode SLS": "idbs"})

updatingData["Tanggal Diterima"] = pd.to_datetime(updatingData["Tanggal Diterima"], errors='coerce', dayfirst=True)
updatingData["Tanggal Entri"] = pd.to_datetime(updatingData["Tanggal Entri"], errors='coerce', dayfirst=True)
updatingData["Tanggal Selesai Entri"] = pd.to_datetime(updatingData["Tanggal Selesai Entri"], errors='coerce', dayfirst=True)

# Tambah selection di sidebar
with st.sidebar:
    st.divider()
    level = st.selectbox(
        "Level Data:",
        ("Kabupaten", "Kecamatan", "Nagari", "Blok Sensus")
    )

    st.write(f"You selected: {level}")

    filter_data = st.selectbox(
        "Filter data:",
        ("Dokumen Masuk IPDS", "Dokumen Clean")
    )

    tanggal_range = st.date_input(
        "Pilih Rentang Tanggal: ", 
        (updatingData["Tanggal Diterima"].min().date(), updatingData["Tanggal Diterima"].max().date())
    )

    if len(tanggal_range) != 2:
        tanggal_awal = updatingData["Tanggal Diterima"].min().date()
        tanggal_akhir = updatingData["Tanggal Diterima"].max().date()
    
    else:
        tanggal_awal, tanggal_akhir = tanggal_range
    
    # Filter data
    updatingDataFiltered = updatingData[
        (updatingData["Tanggal Diterima"] >= pd.to_datetime(tanggal_awal)) & 
        (updatingData["Tanggal Diterima"] <= pd.to_datetime(tanggal_akhir))
    ]

# Fungsi buat agregat data
def show_data(level_data):
    # Seleksi level_data
    if level_data == "Kabupaten":
        total = updatingDataFiltered.groupby("idkab")["Status Dokumen"].count()
        measure = updatingDataFiltered[updatingDataFiltered["Status Dokumen"] == "Clean"].groupby("idkab")["Status Dokumen"].count()

    elif level_data == "Kecamatan":
        total = updatingDataFiltered.groupby("idkec")["Status Dokumen"].count()
        measure = updatingDataFiltered[updatingDataFiltered["Status Dokumen"] == "Clean"].groupby("idkec")["Status Dokumen"].count()

    elif level_data == "Nagari":
        total = updatingDataFiltered.groupby("iddesa")["Status Dokumen"].count()
        measure = updatingDataFiltered[updatingDataFiltered["Status Dokumen"] == "Clean"].groupby("iddesa")["Status Dokumen"].count()

    elif level_data == "Blok Sensus":
        total = updatingDataFiltered.groupby("idbs")["Status Dokumen"].count()
        measure = updatingDataFiltered[updatingDataFiltered["Status Dokumen"] == "Clean"].groupby("idbs")["Status Dokumen"].count()
    
    summary = pd.DataFrame({
        "Total" : total,
        "Measure" : measure
    })

    summary["Persentase"] = (summary["Measure"] / summary["Total"])*100
    summary["Persentase"] = summary["Persentase"].round(2)
    summary = summary.reset_index()
    return summary

# Fungsi buat tampilin peta
def show_map(level_data) :
    # Seleksi level_data
    if level_data == "Kabupaten":
        id = "idkab"
        gdf = gpd.read_file(kabupaten)
        gdf_merged = gdf.merge(show_data(level_data), on = id, how = "left")
        tooltip = folium.GeoJsonTooltip(
            fields=["idkab", "nmkab", "Measure", "Persentase"],
            aliases=["Kode Kabupaten", "Kabupaten", "Data", "Data (%)"]
        )
    elif level_data == "Kecamatan":
        id = "idkec"
        gdf = gpd.read_file(kecamatan)
        gdf_merged = gdf.merge(show_data(level_data), on = id, how = "left")
        tooltip = folium.GeoJsonTooltip(
            fields=["idkec", "nmkec", "Measure", "Persentase"],
            aliases=["Kode Kecamatan", "Kecamatan", "Data", "Data (%)"]
        )
    elif level_data == "Nagari":
        id = "iddesa"
        gdf = gpd.read_file(nagari)
        gdf_merged = gdf.merge(show_data(level_data), on = id, how = "left")
        tooltip = folium.GeoJsonTooltip(
            fields=["iddesa", "nmkec", "nmdesa", "Measure", "Persentase"],
            aliases=["Kode Desa", "Kecamatan", "Desa", "Data", "Data (%)"]
        )
    elif level_data == "Blok Sensus":
        id = "idbs"
        gdf = gpd.read_file(bs)
        gdf_merged = gdf.merge(show_data(level_data), on = id, how = "left")
        tooltip = folium.GeoJsonTooltip(
            fields=["idbs", "nmkec", "nmdesa", "kdbs", "Measure", "Persentase"],
            aliases=["Kode BS", "Kecamatan", "Desa", "BS", "Data", "Data (%)"]
        )
    
    # Tampilkan peta
    m = folium.Map(location=[-1.100, 101.7], zoom_start=9)

    # Tambah Choropleth Map
    folium.Choropleth(
        geo_data = gdf_merged,
        data = show_data(level_data),
        columns = [show_data(level_data).iloc[:,0], "Persentase"],
        key_on = f"feature.properties.{id}",
        bins = [0, 25, 50, 75, 100],
        fill_color = "RdYlGn"
    ).add_to(m)

    # Tambah geojson
    folium.GeoJson(
        data = gdf_merged,
        name = "Tooltip",
        tooltip = tooltip,
        zoom_on_click = True,
        style_function = lambda x: {
            "fillOpacity" : 0,
            "color" : "black",
            "weight" : 0.5
        },
        highlight_function = lambda x: {
            "fillOpacity" : 0.5,
            "color" : "cyan",
            "weight" : 1.5
        }
    ).add_to(m)

    map = st_folium(m)
    return map    

# Add Columns
col1, col2, col3, col4 = st.columns(4, border=True)
col11, col12 = st.columns(2, border = True)

# Hitung data
jumlah_masuk = updatingDataFiltered["Tanggal Diterima"].notna().sum()
jumlah_belum_masuk = len(updatingData) - jumlah_masuk

jumlah_mulai_entri = updatingDataFiltered["Tanggal Entri"].notna().sum()
jumlah_belum_entri = jumlah_masuk - jumlah_mulai_entri

jumlah_selesai_entri = updatingDataFiltered["Tanggal Selesai Entri"].notna().sum()
jumlah_belum_selesai_entri = jumlah_mulai_entri - jumlah_selesai_entri

jumlah_clean = (updatingDataFiltered["Status Dokumen"] == "Clean").sum()
jumlah_error = (updatingDataFiltered["Status Dokumen"] == "Error").sum()

agregat = pd.DataFrame({
    "Kategori" : [
        "Belum Masuk IPDS",
        "Belum Entri",
        "Belum Selesai Entri",
        "Dokumen Clean"
    ],
    "Jumlah" : [
        jumlah_belum_masuk,
        jumlah_belum_entri,
        jumlah_belum_selesai_entri,
        jumlah_clean
    ]
})

# Menampilkan jumlah dokumen diterima IPDS
with col1:
    st.metric(label="Jumlah Dokumen Masuk IPDS", value=jumlah_masuk)

# Menampilkan jumlah dokumen selesai entri
with col2:
    st.metric(label="Jumlah Dokumen Selesai Entri", value=jumlah_selesai_entri)

# Menampilkan jumlah dokumen clean
with col3:
    st.metric(label="Jumlah Dokumen Clean", value=jumlah_clean)

# Menampilkan jumlah dokumen error
with col4:
    st.metric(label="Jumlah Dokumen Error", value=jumlah_error)

# Menampilkan peta
with col11:
    st.write(f"Menampilkan data: {filter_data}, pada Level: {level}")
    show_map(level)

with col12:
    fig = px.pie(
        data_frame = agregat, 
        names="Kategori", 
        values = "Jumlah", 
        title = "Progress Pengolahan Dokumen",
        hole = .3
    )
    st.plotly_chart(fig, use_container_width = True)