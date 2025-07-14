import streamlit as st
import plotly.graph_objects as go
import Connection

# Define data
updatingData = Connection.getDataUpdating()
pendataanData = Connection.getDataPendataan()

rekap_updating = updatingData["Nama Pengentri"].value_counts().reset_index()
rekap_updating.columns = ["Nama Pengentri", "Jumlah Dokumen"]
rekap_updating = rekap_updating.sort_values(by = "Jumlah Dokumen")

rekap_pendataan = pendataanData["Nama Pengentri"].value_counts().reset_index()
rekap_pendataan.columns = ["Nama Pengentri", "Jumlah Dokumen"]
rekap_pendataan = rekap_pendataan.sort_values(by = "Jumlah Dokumen")

col1, col2 = st.columns([1,1], border = True)

with col1:
    st.markdown("#### Rekapitulasi Updating Susenas")
    st.markdown("##### Entri Dokumen Updating")

    figUpdating = go.Figure(
        data = [go.Bar(
            x = rekap_updating["Jumlah Dokumen"],
            y = rekap_updating["Nama Pengentri"],
            orientation = "h",
            text = rekap_updating["Jumlah Dokumen"],
            textposition = "inside",
            insidetextanchor = "middle",
            textfont = dict(
                size = 14
            )
        )]
    )

    figUpdating.update_layout(
        xaxis_title = "Jumlah Dokumen",
        yaxis_title = "Nama Pengentri",
        template = "plotly_white",
        margin = dict(l=10, r=10, t=0, b=0),
    )

    st.plotly_chart(figUpdating)

with col2:
    st.markdown("#### Rekapitulasi Updating Susenas")
    st.markdown("##### Entri Dokumen Updating")

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
