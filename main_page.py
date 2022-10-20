from traceback import print_exc
import streamlit as st
import plotly.express as px
import os
from dotenv import load_dotenv

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.get_data import get_data_from_cockroachdb

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")


st.set_page_config(layout="wide", page_title="Gas Turbine", page_icon="💨")


@st.cache
def get_data():
    all_df = pd.read_parquet(
        "https://hackathonfiles123.s3.amazonaws.com/all_df.parquet"
    )
    site_df = pd.read_csv(
        "https://hackathonfiles123.s3.amazonaws.com/site_metadata.csv"
    )
    temp_df = all_df.merge(site_df, on=["CUSTOMER_NAME", "PLANT_NAME"])
    all_df["THRM_EFF"] = temp_df["POWER"] / (temp_df["FUEL_FLOW"] * temp_df["FUEL_LHV"])
    all_df["datetime"] = pd.to_datetime(all_df["datetime"])

    return all_df, site_df


st.markdown("# 💨 Gas Turbine Analysis 💨 ")
st.subheader("Analytics and Insights for Gas Turbine Data")
st.image("media/turbine.jpeg", width=1000, use_column_width=True)
st.markdown(
    """
    This app provides an overview of gas turbine engine data around the world. 
    
    Some of the main question we aimed to answer are:

    - Which plants produce more CO2 around the world, by country, by continent?
    - Which plant has produced more kWh and with what overall efficiency?
    - Which plant has had the most shutdowns or downtime?
    - Which engine is degrading the most?
"""
)


st.subheader("The data")

st.caption("data pulled straight from cockroach DB :)")

# sample_all_df, sample_site_df = get_data_from_cockroachdb()

# with st.expander("See data"):
#    st.dataframe(data=sample_all_df, use_container_width=True)
#    st.dataframe(data=sample_site_df, use_container_width=True)

all_df, site_df = get_data()


plant_df = (
    all_df.groupby(["PLANT_NAME"])
    .agg(
        {
            "CMP_SPEED": "sum",
            "POWER": "sum",
            "CO2": "sum",
            "THRM_EFF": "mean",
            "FUEL_FLOW": "mean",
        }
    )
    .reset_index()
)

plant_df = plant_df.merge(site_df, on="PLANT_NAME")


cols = [
    "CMP_SPEED",
    "POWER",
    "FUEL_FLOW",
    "CO2",
    "THRM_EFF",
    "FUEL_N2_MOL_PCT",
    "FUEL_MW",
    "FUEL_LHV",
    "CO2_FUEL_RATIO",
]

size_col = st.sidebar.selectbox("Select a metric", cols, index=0)

continent_df = (
    plant_df.groupby("CONTINENT")
    .sum()
    .reset_index()
    .sort_values(by=size_col, ascending=True)
)

country_df = (
    plant_df.groupby("COUNTRY")
    .sum()
    .reset_index()
    .sort_values(by=size_col, ascending=True)
    .head(10)
)

st.subheader(f"Global Overview of `{size_col}` for all Power Plants")


# plot of map
px.set_mapbox_access_token(MAPBOX_TOKEN)
fig = px.scatter_mapbox(
    plant_df,
    lat="LATITUDE",
    lon="LONGITUDE",
    hover_name=size_col,
    hover_data=["COUNTRY"],
    color="CONTINENT",
    width=800,
    height=500,
    zoom=1,
    size=size_col,
)

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)


col1, col2 = st.columns(2)

continent_bar = px.bar(
    continent_df,
    y="CONTINENT",
    x=size_col,
    color="THRM_EFF",
    title=f"Total {size_col} by Continent",
)

# remove axis titles
continent_bar.update_xaxes(title_text="")
continent_bar.update_yaxes(title_text="")


country_bar = px.bar(
    country_df,
    y="COUNTRY",
    x=size_col,
    color="THRM_EFF",
    title=f"Total {size_col} by Continent",
)
country_bar.update_xaxes(title_text="")
country_bar.update_yaxes(title_text="")

with col1:
    st.plotly_chart(continent_bar, use_container_width=True)

with col2:
    st.plotly_chart(country_bar, use_container_width=True)


st.subheader("Analysis of Each Plant")
plant_name = st.sidebar.selectbox(
    "Select a plant", all_df["PLANT_NAME"].unique(), index=0
)
# filter all_df by plant_name
all_df_filtered = all_df[all_df["PLANT_NAME"] == plant_name]
fig = px.line(
    all_df_filtered,
    x="datetime",
    y="THRM_EFF",
    color="ENGINE_ID",
    title="Thermal efficiency over time for each ENGINE_ID",
)

st.plotly_chart(fig, use_container_width=True)

# group by month average thermal efficiency for each engine in all_df_filtered
engine_df = (
    all_df_filtered.groupby(["ENGINE_ID", pd.Grouper(key="datetime", freq="M")])
    .agg({"THRM_EFF": "mean"})
    .reset_index()
)

fig = px.line(
    engine_df,
    x="datetime",
    y="THRM_EFF",
    color="ENGINE_ID",
    title="Average thermal efficiency over time for each ENGINE_ID",
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Downtime and Availability of Plants")
avail_df = (
    all_df.groupby(["PLANT_NAME", "ENGINE_ID"])[["CMP_SPEED"]]
    .agg(lambda x: x.eq(0).sum())
    .reset_index()
)

avail_df = avail_df.sort_values(by=["CMP_SPEED"], ascending=False)

fig = px.bar(
    x=avail_df["PLANT_NAME"],
    y=avail_df["CMP_SPEED"],
    color=avail_df["ENGINE_ID"],
    orientation="v",
)

# sort by CMP_SPEED
fig.update_layout(
    xaxis={"categoryorder": "total descending"},
    title="Total Downtime for each Plant",
)

fig.update_xaxes(title_text="Plant Name")
fig.update_yaxes(title_text="Down Time (Hours)")

st.plotly_chart(fig, use_container_width=True)
st.markdown(
    """
From this plot, we can see that the AQUAMARINE-KANGAROO plant has the highest downtime among all and that corrective measures can be implemented to increase the efficiency of the plant. 

On the other hand, the COBALT-CATFISH plant has the lowest downtime and can be used as a benchmark for other plants.
"""
)


st.subheader("Power Generation vs Thermal Efficiency")
power_df = (
    all_df.groupby(["PLANT_NAME"])[["POWER", "THRM_EFF"]]
    .agg({"POWER": sum, "THRM_EFF": "mean"})
    .reset_index()
)
# plot side by side bar chart of power and thrm_eff for each plant
power_df.sort_values(by=["THRM_EFF"], ascending=True, inplace=True)
power_df["THRM_EFF"] = power_df["THRM_EFF"] * 100
fig = make_subplots(
    rows=1,
    cols=2,
    specs=[[{}, {}]],
    shared_xaxes=False,
    shared_yaxes=True,
    horizontal_spacing=0,
)

fig.append_trace(
    go.Bar(
        x=power_df["POWER"],
        y=power_df["PLANT_NAME"],
        text=power_df["POWER"].map(
            "{:,.0f}".format
        ),  # Display the numbers with thousands separators in hover-over tooltip
        textposition="inside",
        orientation="h",
        width=0.7,
        showlegend=False,
        marker_color="#4472c4",
    ),
    1,
    1,
)  # 1,1 represents row 1 column 1 in the plot grid

fig.append_trace(
    go.Bar(
        x=power_df["THRM_EFF"],
        y=power_df["PLANT_NAME"],
        text=power_df["THRM_EFF"].map("{:,.0f}".format),
        textposition="inside",
        orientation="h",
        width=0.7,
        showlegend=False,
        marker_color="#ed7d31",
    ),
    1,
    2,
)  # 1,2 represents row 1 column 2 in the plot grid


fig.update_xaxes(
    showticklabels=False,
    title_text="Power Generation",
    row=1,
    col=1,
    range=[730000000, 0],
)
fig.update_xaxes(
    showticklabels=False, title_text="Thermal Efficiency", row=1, col=2, range=[0, 50]
)

fig.update_layout(
    height=700,
    xaxis1={"side": "top"},
    xaxis2={"side": "top"},
)

st.plotly_chart(fig, use_container_width=True)
st.markdown(
    """
Thermal Efficiency of PREHISTORIC-PEACOCK plant is the highest among all plants.
However, the POWER generated by this plant is the lowest among all plants. This can be due to the fact that the plant is not operating at full capacity.
On the other hand, the POWER generated by the ABORIGINAL-PICULET plant is the highest among all plants and the Thermal Efficiency is on par with the highest efficiency plant,
hence this plant can be treated as a benchmark for other plants.
"""
)
