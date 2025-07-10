# 0. Import Library
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

@st.cache_resource
def sheetUpdating():
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(
        worksheet="Updating",
        ttl = 1
    )
    return df

def getDataUpdating():
    dfUpdating = pd.DataFrame(sheetUpdating())
    dfUpdating = dfUpdating.drop(["No", "Kd-Provinsi", "Kd-Kabupaten", "Kd-Kecamatan", "Kd-Nagari"], axis=1)
    
    dfUpdating[["Kode Provinsi", "Kode Kabupaten"]] = dfUpdating[["Kode Provinsi", "Kode Kabupaten"]].astype(int).astype(str)
    dfUpdating["Kode Kecamatan"] = dfUpdating["Kode Kecamatan"].apply(lambda x: f"{int(x):03d}")
    dfUpdating["Kode Nagari"] = dfUpdating["Kode Nagari"].apply(lambda x: f"{int(x):03d}")
    dfUpdating["idkab"] = dfUpdating["Kode SLS"].str[:4]
    dfUpdating["idkec"] = dfUpdating["Kode SLS"].str[:7]
    dfUpdating["iddesa"] = dfUpdating["Kode SLS"].str[:10]
    dfUpdating = dfUpdating.rename(columns = {"Kode SLS": "idbs"})

    dfUpdating["Tanggal Diterima"] = pd.to_datetime(dfUpdating["Tanggal Diterima"], errors='coerce', dayfirst=True)
    dfUpdating["Tanggal Entri"] = pd.to_datetime(dfUpdating["Tanggal Entri"], errors='coerce', dayfirst=True)
    dfUpdating["Tanggal Selesai Entri"] = pd.to_datetime(dfUpdating["Tanggal Selesai Entri"], errors='coerce', dayfirst=True)

    return dfUpdating

def sheetPendataan():
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(
        worksheet="Pendataan"
    )
    return df

def getDataPendataan():
    df = pd.DataFrame(sheetPendataan())

    return df
# st.write(getDataUpdating().dtypes)