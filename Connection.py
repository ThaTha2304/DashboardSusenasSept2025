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
    
    return dfUpdating

# st.write(getDataUpdating().dtypes)