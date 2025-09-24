import streamlit as st
import plotly.graph_objects as go
import myconfig.Connection as Connection

# Define Data
@st.cache_data
def load_data():
    return Connection.getDataPendataan()
pendataanData = load_data()

def clear_cache():
    st.cache_data.clear()

rekap_pendataan = pendataanData["Nama Pengentri"].value_counts().reset_index()
rekap_pendataan.columns = ["Nama Pengentri", "Jumlah Dokumen"]
rekap_pendataan = rekap_pendataan.sort_values(by = "Jumlah Dokumen")

def count_documents(df):
    df_agregat = df.groupby("NKS").agg(
        jumlah_diterima = ("Tanggal Diterima", lambda x: x.notna().sum()),
        jumlah_selesai_entri = ("Tanggal Selesai Entri", lambda x: x.notna().sum())
    ).reset_index()
    return df_agregat

col1, col2 = st.columns([1,1], border = True)

with st.sidebar:
    if st.button("Refresh Data", type="primary"):
        clear_cache()
        st.rerun()

with col1:
    st.markdown("#### Rekapitulasi Petugas Entri Susenas September 2025")
    st.markdown("##### Entri Dokumen Pendataan")

    figPendataan = go.Figure(
        data = [go.Bar(
            x = rekap_pendataan["Jumlah Dokumen"],
            y = rekap_pendataan["Nama Pengentri"],
            orientation = "h",
            text = rekap_pendataan["Jumlah Dokumen"],
            textposition = "inside",
            insidetextanchor = "middle",
            textfont = dict(
                size = 14
            )
        )]
    )

    figPendataan.update_layout(
        xaxis_title = "Jumlah Dokumen",
        yaxis_title = "Nama Pengentri",
        template = "plotly_white",
        margin = dict(l=10, r=10, t=0, b=0),
    )

    st.plotly_chart(figPendataan)

with col2:
    st.markdown("#### Rekapitulasi Dokumen Susenas September 2025")
    st.markdown("##### Dokumen Tiap SLS")
    # dataframe that shows the number of documents per SLS
    st.dataframe(count_documents(pendataanData), use_container_width=True)

st.divider()

st.markdown("#### Progress Harian Entri Dokumen Susenas September 2025")

df_diterima = pendataanData.groupby("Tanggal Diterima").size().reset_index(name='Jumlah Diterima')
df_selesai_entri = pendataanData.groupby("Tanggal Selesai Entri").size().reset_index(name='Jumlah Selesai Entri')

df_diterima_kumulatif = pendataanData.groupby("Tanggal Diterima").size().cumsum().reset_index(name='Jumlah Diterima Kumulatif')
df_selesai_entri_kumulatif = pendataanData.groupby("Tanggal Selesai Entri").size().cumsum().reset_index(name='Jumlah Selesai Entri Kumulatif')

fig = go.Figure()

# Tambahkan garis untuk Jumlah Dokumen Diterima
fig.add_trace(
    go.Scatter(
        x=df_diterima["Tanggal Diterima"],
        y=df_diterima["Jumlah Diterima"],
        mode='lines+markers',
        name='Jumlah Diterima'
    )
)

# Tambahkan garis untuk Jumlah Selesai Entri
fig.add_trace(
    go.Scatter(
        x=df_selesai_entri["Tanggal Selesai Entri"],
        y=df_selesai_entri["Jumlah Selesai Entri"],
        mode='lines+markers',
        name='Jumlah Selesai Entri'
    )
)

fig.add_trace(
    go.Scatter(
        x=df_diterima_kumulatif["Tanggal Diterima"],
        y=df_diterima_kumulatif["Jumlah Diterima Kumulatif"],
        mode='lines+markers',
        name='Jumlah Diterima Kumulatif'
    )
)

fig.add_trace(
    go.Scatter(
        x=df_selesai_entri_kumulatif["Tanggal Selesai Entri"],
        y=df_selesai_entri_kumulatif["Jumlah Selesai Entri Kumulatif"],
        mode='lines+markers',
        name='Jumlah Selesai Entri Kumulatif'
    )
)

fig.update_layout(
    title='Progress Harian Entri Dokumen',
    xaxis_title='Tanggal',
    yaxis_title='Jumlah Dokumen',
    template='plotly_white',
    margin=dict(l=10, r=10, t=30, b=10),
)


st.plotly_chart(fig, use_container_width=True)