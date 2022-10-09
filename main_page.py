from turtle import color
import streamlit as st
import plotly.express as px
import os
from dotenv import load_dotenv

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.get_data import get_data_from_cockroachdb


load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

st.markdown("# Gas Turbine ")


# all_df, site_df = get_data_from_cockroachdb()


@st.cache
def get_data():
    all_df = pd.read_csv("data/all_data.csv")
    site_df = pd.read_csv("data/site_metadata.csv")
    temp_df = all_df.merge(site_df, on=["CUSTOMER_NAME", "PLANT_NAME"])
    all_df["THRM_EFF"] = temp_df["POWER"] / (temp_df["FUEL_FLOW"] * temp_df["FUEL_LHV"])
    all_df["datetime"] = pd.to_datetime(all_df["datetime"])

    return all_df, site_df


all_df, site_df = get_data()

# group by PLANT_NAME and sum the POWER
power_df = all_df.groupby(["PLANT_NAME"]).sum().reset_index()

# join the power_df with site_df
power_df = power_df.merge(site_df, on="PLANT_NAME")

# plot of map


st.subheader("")

px.set_mapbox_access_token(MAPBOX_TOKEN)

fig = px.scatter_mapbox(
    power_df,
    lat="LATITUDE",
    lon="LONGITUDE",
    hover_name="CONTINENT",
    color="CONTINENT",
    hover_data=["CUSTOMER_NAME"],
    width=500,
    height=500,
    zoom=1.3,
    size="POWER",
)


fig.update_layout(
    title="Gas Turbine Locations and CO2 emissions",
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    showlegend=False,
)


st.plotly_chart(fig, use_container_width=True)

# select box for plant_name in all_df

plant_name = st.selectbox("Select a plant", all_df["PLANT_NAME"].unique(), index=0)

# filter all_df by plant_name
all_df = all_df[all_df["PLANT_NAME"] == plant_name]


fig = px.line(
    all_df,
    x="datetime",
    y="THRM_EFF",
    color="ENGINE_ID",
    title="Power over time for each ENGINE_ID",
)

st.plotly_chart(fig, use_container_width=True)
