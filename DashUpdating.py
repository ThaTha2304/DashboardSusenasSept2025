import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import Connection
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
updatingData["idkab"] = updatingData["Kode SLS"].str[:4]
updatingData["idkec"] = updatingData["Kode SLS"].str[:7]
updatingData["iddesa"] = updatingData["Kode SLS"].str[:10]
updatingData = updatingData.rename(columns = {"Kode SLS": "idbs"})

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

# Fungsi buat agregat data
def show_data(level_data):
    # Seleksi level_data
    if level_data == "Kabupaten":
        total = updatingData.groupby("idkab")["Status Dokumen"].count()
        measure = updatingData[updatingData["Status Dokumen"] == "Clean"].groupby("idkab")["Status Dokumen"].count()

    elif level_data == "Kecamatan":
        total = updatingData.groupby("idkec")["Status Dokumen"].count()
        measure = updatingData[updatingData["Status Dokumen"] == "Clean"].groupby("idkec")["Status Dokumen"].count()

    elif level_data == "Nagari":
        total = updatingData.groupby("iddesa")["Status Dokumen"].count()
        measure = updatingData[updatingData["Status Dokumen"] == "Clean"].groupby("iddesa")["Status Dokumen"].count()

    elif level_data == "Blok Sensus":
        total = updatingData.groupby("idbs")["Status Dokumen"].count()
        measure = updatingData[updatingData["Status Dokumen"] == "Clean"].groupby("idbs")["Status Dokumen"].count()
    
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