import streamlit as st
import plotly.express as px
import os
from dotenv import load_dotenv

from utils.get_data import get_data_from_cockroachdb


load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

st.markdown("# Gas Turbine ")
st.sidebar.markdown("test")


all_df, site_df = get_data_from_cockroachdb()


px.set_mapbox_access_token(MAPBOX_TOKEN)

fig = px.scatter_mapbox(
    site_df,
    lat="LATITUDE",
    lon="LONGITUDE",
    hover_name="CUSTOMER_NAME",
    hover_data=["CUSTOMER_NAME", "PLANT_NAME", "LATITUDE", "LONGITUDE"],
    zoom=1,
    width=1000,
    height=1000,
)

fig.update_layout(
    title="Gas Turbine Locations",
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
)

st.plotly_chart(fig, use_container_width=True)
