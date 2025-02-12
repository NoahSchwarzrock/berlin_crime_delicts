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

loc_df.loc['all'] = df.sum(numeric_only=True)
all_values = loc_df.loc['all'].dropna()

fig = px.pie(names=all_values.index, values=all_values.values, title='Verteilung der Delikte in Berlin')
st.plotly_chart(fig)


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


fig = px.bar(loc_df.iloc[0:12], 
             x=loc_df.iloc[0:12].index,
             y=["gewaltverbrechen", "verkehrsdelikte", "diebstahl"],
             title="Verteilung der Straftaten nach Standort",
             labels={"value": "Anzahl der Straftaten", "location": "Ort"}
             )

fig.update_layout(xaxis_title='Stadtteil')

st.plotly_chart(fig)


df['date'] = pd.to_datetime(df['date'])
df["jahr"] = df["date"].dt.year
df_year = df.groupby(by=['location', "jahr"], as_index=False).agg(verkehrsdelikte=('verkehrsdelikte', 'sum'),
                                       vandalismus=('vandalismus', 'sum'),
                                       sexualdelikte=('sexualdelikte', 'sum'),
                                       drogen=('drogen', 'sum'),
                                       betrug=('betrug', 'sum'),
                                       diebstahl=('diebstahl', 'sum'),
                                       hasskriminalität=('hasskriminalität', 'sum'),
                                       gewaltverbrechen=('gewaltverbrechen', 'sum'),
                                       sonstige=('sonstige', 'sum')
                                       )
 
mitte_df_year = df_year[df_year["location"] == "Mitte"]
 
fig = px.bar(mitte_df_year,
             x="jahr",
             y=["verkehrsdelikte", "vandalismus", "diebstahl", "hasskriminalität", "gewaltverbrechen"],
             title="Verteilung der Straftaten im Bezirk Mitte",
             labels={"value": "Anzahl der Straftaten", "jahr": "Jahre"},
             barmode="group"
             )
 
st.plotly_chart(fig)