import streamlit as st
import pandas as pd
import geopandas as gpd
import streamviz
import folium
import Connection
import json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
from datetime import date

# Define Layers
kabupaten = "assets/geojson/Batas Kabupaten.geojson"
kecamatan = "assets/geojson/Batas Kecamatan.geojson"
nagari = "assets/geojson/Batas Nagari.geojson"
bs = "assets/geojson/Batas BS.geojson"

# Define Data
updatingData = Connection.getDataUpdating()
start_date = date(2025, 2, 1)
end_date = date(2025, 2, 28)

# Tambah selection di sidebar
with st.sidebar:
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
def show_data(level_data, filter_data):
    # Seleksi level_data
    if level_data == "Kabupaten":
        index_wilayah = "idkab"

    elif level_data == "Kecamatan":
        index_wilayah = "idkec"

    elif level_data == "Nagari":
        index_wilayah = "iddesa"

    elif level_data == "Blok Sensus":
        index_wilayah = "idbs"
    
    all_index = updatingData[index_wilayah].unique()

    if filter_data == "Dokumen Clean":
        total = updatingData.groupby(index_wilayah).size()
        total = total.reindex(all_index, fill_value=0)

        measure = updatingDataFiltered[updatingDataFiltered["Status Dokumen"] == "Clean"].groupby(index_wilayah)["Status Dokumen"].count()
        measure = measure.reindex(all_index, fill_value = 0)
        
    elif filter_data == "Dokumen Masuk IPDS":
        index_data = "Tanggal Diterima"
        total = updatingData.groupby(index_wilayah).size()
        total = total.reindex(all_index, fill_value=0)

        measure = updatingDataFiltered[updatingDataFiltered[index_data].notnull()].groupby(index_wilayah)[index_data].count()
        measure = measure.reindex(all_index, fill_value = 0)        

    summary = pd.DataFrame({
        "Total" : total,
        "Measure" : measure
    })

    summary["Persentase"] = (summary["Measure"] / summary["Total"].replace(0, pd.NA))*100
    summary["Persentase"] = summary["Persentase"].round(2).fillna(0)
    summary = summary.reset_index()
    return summary

# Fungsi buat tampilin peta
def show_map(level_data, filter_data) :
    data = show_data(level_data, filter_data)
    # Seleksi level_data
    if level_data == "Kabupaten":
        id = "idkab"
        gdf = gpd.read_file(kabupaten)
        gdf_merged = gdf.merge(data, on = id, how = "left")
        tooltip = folium.GeoJsonTooltip(
            fields=["idkab", "nmkab", "Measure", "Persentase"],
            aliases=["Kode Kabupaten", "Kabupaten", "Data", "Data (%)"]
        )
    elif level_data == "Kecamatan":
        id = "idkec"
        gdf = gpd.read_file(kecamatan)
        gdf_merged = gdf.merge(data, on = id, how = "left")
        tooltip = folium.GeoJsonTooltip(
            fields=["idkec", "nmkec", "Measure", "Persentase"],
            aliases=["Kode Kecamatan", "Kecamatan", "Data", "Data (%)"]
        )
    elif level_data == "Nagari":
        id = "iddesa"
        gdf = gpd.read_file(nagari)
        gdf_merged = gdf.merge(data, on = id, how = "left")
        tooltip = folium.GeoJsonTooltip(
            fields=["iddesa", "nmkec", "nmdesa", "Measure", "Persentase"],
            aliases=["Kode Desa", "Kecamatan", "Desa", "Data", "Data (%)"]
        )
    elif level_data == "Blok Sensus":
        id = "idbs"
        gdf = gpd.read_file(bs)
        gdf_merged = gdf.merge(data, on = id, how = "left")
        tooltip = folium.GeoJsonTooltip(
            fields=["idbs", "nmkec", "nmdesa", "kdbs", "Measure", "Persentase"],
            aliases=["Kode BS", "Kecamatan", "Desa", "BS", "Data", "Data (%)"]
        )
    
    # Tampilkan peta
    m = folium.Map(location=[-1.100, 101.7], zoom_start=9)

    # Tambah Choropleth Map
    folium.Choropleth(
        geo_data = gdf_merged,
        data = data,
        columns = [data.iloc[:,0], "Persentase"],
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

    map = st_folium(m, width = "100%", height=500)
    return map   

# Fungsi untuk menampilkan pie chart
def show_chart(data_primer, data_sekunder, label_primer, label_sekunder, warna):
    fig = go.Figure(go.Bar(
        x = [data_primer],
        y = [label_primer],
        orientation = "h",
        name = "",
        marker = dict(color = '#00cc96'),
        hovertemplate = f'{label_primer} : {data_primer}'
    ))

    fig.add_trace(go.Bar(
        x = [updatingData["idbs"].count()],
        y = [label_primer],
        orientation = "h",
        marker = dict(color = warna),
        showlegend = False,
        name = "",
        opacity = 0.3,
        hovertemplate = f'{label_sekunder} : {data_sekunder}'
    ))

    fig.update_layout(
        barmode = "overlay",
        xaxis = dict(range = [0, updatingData["idbs"].count()], showticklabels = False),
        yaxis = dict(showticklabels = False),
        height = 50,
        margin = dict(l=10, r=10, t=0, b=0),
        showlegend = False,
        annotations = [dict(
            x = updatingData["idbs"].count()/2,
            y = 0,
            text = f"{data_primer} - {100*(data_primer/updatingData["idbs"].count()):.2f}%",
            showarrow = False,
            font = dict(size = 20, color = "#31333F"), 
            xanchor = "center",
            yanchor = "middle"
        )]
    )
    return st.plotly_chart(fig, use_container_width=False)

# Add Columns
col1, col2 = st.columns([0.35, 0.65], border=True)

# Hitung data
jumlah_masuk = updatingDataFiltered["Tanggal Diterima"].notna().sum()
jumlah_belum_masuk = len(updatingData) - jumlah_masuk

jumlah_mulai_entri = updatingDataFiltered["Tanggal Entri"].notna().sum()
jumlah_belum_entri = jumlah_masuk - jumlah_mulai_entri

jumlah_selesai_entri = updatingDataFiltered["Tanggal Selesai Entri"].notna().sum()
jumlah_belum_selesai_entri = jumlah_mulai_entri - jumlah_selesai_entri

jumlah_clean = (
    ((updatingDataFiltered["Status Dokumen"] == "Clean") &
    (updatingDataFiltered["Tanggal Selesai Entri"].notna()))
).sum()
jumlah_error = (
    ((updatingDataFiltered["Status Dokumen"] == "Error") &
    (updatingDataFiltered["Tanggal Selesai Entri"].notna()))
).sum()

agregat = pd.DataFrame({
    "Kategori" : [
        "Belum Masuk IPDS",
        "Belum Entri",
        "Belum Selesai Entri",
        "Dokumen Error",
        "Dokumen Clean"
    ],
    "Jumlah" : [
        jumlah_belum_masuk,
        jumlah_belum_entri,
        jumlah_belum_selesai_entri,
        jumlah_error,
        jumlah_clean
    ],
    "Warna" : [
        "#e58606",
        "#5d69b1",
        "#764e9f",
        "#ed645a",
        "#3bc8a3"
    ]
})

# Menampilkan jumlah dokumen diterima IPDS
with col1:
    st.markdown("#### Status Dokumen")

    st.markdown("Dokumen Diterima IPDS")
    show_chart(jumlah_masuk, jumlah_belum_masuk, "Masuk", "Belum Masuk", "#C3C2C2")

    st.markdown("Dokumen Selesai Entri")
    show_chart(jumlah_selesai_entri, jumlah_belum_selesai_entri, "Selesai Entri", "Belum Selesai Entri", "#C3C2C2")
    
    st.markdown("#### Validasi Dokumen")
    show_chart(jumlah_clean, jumlah_error, "Clean", "Error", "#FF6E6E")

    st.divider()

    st.markdown("#### Progress Pengolahan")

    fig = go.Figure()
    for i, row in agregat.iterrows():
        fig.add_trace(go.Bar(
            name = row["Kategori"],
            y = ["Progress"],
            x=[row["Jumlah"]],
            text = row["Jumlah"],
            textposition='auto',
            textfont = dict(size = 14),
            insidetextanchor= "middle",
            orientation = "h",
            hovertemplate=f"{row['Kategori']} : {row['Jumlah']}",
            marker_color = row["Warna"]
        ))

    fig.update_layout(
        barmode = "stack",
        xaxis = dict(range = [0, updatingData["idbs"].count()], showticklabels = False),
        yaxis = dict(showticklabels = False),
        showlegend = True,
        legend = dict(
            orientation = "h",
            yanchor = "bottom",
            y = -0.5,
            xanchor = "auto",
            x = 0.5
        ),
        height = 200,
        margin = dict(l=10, r=10, t=0, b=40),
    )
    st.plotly_chart(fig)

with col2:
    st.markdown("#### Sebaran Dokumen")
    cola, colb = st.columns([1,1], border = True)
    with cola:
        level = st.selectbox(
            "Level Data:",
            ("Kabupaten", "Kecamatan", "Nagari", "Blok Sensus")
        )

    with colb:
        filter_data = st.selectbox(
            "Filter data:",
            ("Dokumen Masuk IPDS", "Dokumen Clean")
        )
    show_map(level, filter_data)