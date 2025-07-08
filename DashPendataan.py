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
pendataanData = Connection.getDataPendataan()

st.write(pendataanData)