# 0. Import Library
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def sheetUpdating():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(
        worksheet="Updating",
        ttl = 5
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
        worksheet="Pendataan",
        ttl = 5
    )
    return df

def getDataPendataan():
    dfPendataan = pd.DataFrame(sheetPendataan())
    dfPendataan = dfPendataan.drop(["No", "Kd-Provinsi", "Kd-Kabupaten", "Kd-Kecamatan", "Kd-Nagari"], axis=1)
    dfPendataan[["Kode Provinsi", "Kode Kabupaten"]] = dfPendataan[["Kode Provinsi", "Kode Kabupaten"]].astype(int).astype(str)
    dfPendataan["Kode Kecamatan"] = dfPendataan["Kode Kecamatan"].apply(lambda x: f"{int(x):03d}")
    dfPendataan["Kode Nagari"] = dfPendataan["Kode Nagari"].apply(lambda x: f"{int(x):03d}")
    dfPendataan["idkab"] = dfPendataan["Kode SLS"].str[:4]
    dfPendataan["idkec"] = dfPendataan["Kode SLS"].str[:7]
    dfPendataan["iddesa"] = dfPendataan["Kode SLS"].str[:10]
    dfPendataan = dfPendataan.rename(columns = {"Kode SLS": "idbs"})
    dfPendataan = dfPendataan.rename(columns = {"Dokumen Sudah Clean?": "Status Dokumen"})

    dfPendataan["Tanggal Diterima"] = pd.to_datetime(dfPendataan["Tanggal Diterima"], errors='coerce', dayfirst=True)
    dfPendataan["Tanggal Entri"] = pd.to_datetime(dfPendataan["Tanggal Entri"], errors='coerce', dayfirst=True)
    dfPendataan["Tanggal Selesai Entri"] = pd.to_datetime(dfPendataan["Tanggal Selesai Entri"], errors='coerce', dayfirst=True)
    dfPendataan["Tanggal Validasi (MITRA)"] = pd.to_datetime(dfPendataan["Tanggal Validasi (MITRA)"], errors='coerce', dayfirst=True)
    dfPendataan["Tanggal Selesai Validasi (MITRA)"] = pd.to_datetime(dfPendataan["Tanggal Selesai Validasi (MITRA)"], errors='coerce', dayfirst=True)
    dfPendataan["Tanggal Validasi (ORGANIK)"] = pd.to_datetime(dfPendataan["Tanggal Validasi (ORGANIK)"], errors='coerce', dayfirst=True)

    return dfPendataan