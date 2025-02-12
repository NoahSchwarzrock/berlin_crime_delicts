import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots

# Streamlit-Layout auf Wide setzen
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1000px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Beispiel-Daten (ersetze diese mit echten Daten)
einwohnerzahlen = {
    "Mitte": 397134,
    "Friedrichshain-Kreuzberg": 293454,
    "Pankow": 424307,
    "Charlottenburg-Wilmersdorf": 343081,
    "Spandau": 257091,
    "Steglitz-Zehlendorf": 310446,
    "Tempelhof-Schöneberg": 355868,
    "Neukölln": 330017,
    "Treptow-Köpenick": 294081,
    "Marzahn-Hellersdorf": 291948,
    "Lichtenberg": 311881,
    "Reinickendorf": 268792
}

# Daten einlesen
df = pd.read_csv('./data/oh_encoded_categories.csv', index_col=0)
df = df[~df["location"].str.contains(r"[0-9]", regex=True)]

# Gruppierung nach Stadtteil
loc_df = df.groupby(by='location').agg(verkehrsdelikte=('verkehrsdelikte', 'sum'),
                                       vandalismus=('vandalismus', 'sum'),
                                       sexualdelikte=('sexualdelikte', 'sum'),
                                       drogen=('drogen', 'sum'),
                                       betrug=('betrug', 'sum'),
                                       diebstahl=('diebstahl', 'sum'),
                                       hasskriminalität=('hasskriminalität', 'sum'),
                                       gewaltverbrechen=('gewaltverbrechen', 'sum'),
                                       sonstige=('sonstige', 'sum')
                                       )

# Berechnung der absoluten und relativen Verbrechen
loc_df['gesamt'] = loc_df.sum(axis=1)
loc_df["relative_sum"] = loc_df["gesamt"] / loc_df.index.map(einwohnerzahlen)

# Streamlit-UI
st.title("Verbrechen in Berliner Stadtteilen")

# Checkbox für relative Werte
show_relative = st.checkbox("Relative Verbrechen pro Einwohner anzeigen")

# Subplot mit zwei Achsen erstellen
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Absolute Verbrechen (linke Y-Achse)
fig.add_trace(
    go.Bar(x=loc_df.index, y=loc_df['gesamt'], name='Absolute Verbrechen', marker_color='blue'),
    secondary_y=False
)

# Relative Verbrechen (rechte Y-Achse) nur hinzufügen, wenn Checkbox aktiv ist
if show_relative:
    fig.add_trace(
        go.Scatter(x=loc_df.index, y=loc_df['relative_sum'], name='Relative Verbrechen pro Einwohner',
                   mode='lines+markers', marker_color='green'),
        secondary_y=True
    )

# Layout anpassen
fig.update_layout(
    title="Absolute und relative Verbrechen in Berliner Stadtteilen",
    xaxis_title="Stadtteil",
    yaxis_title="Anzahl der Verbrechen",
    yaxis2_title="Relative Verbrechen pro Einwohner" if show_relative else None,
    xaxis_tickangle=-45,
    height=600,
    width=1000,
    showlegend=False
)

# Plot anzeigen
st.plotly_chart(fig)


loc_df.loc['all'] = df.sum(numeric_only=True)
all_values = loc_df.loc['all'].dropna()

fig = px.pie(names=all_values.index, values=all_values.values, title='Verteilung der Delikte in Berlin')
st.plotly_chart(fig)

