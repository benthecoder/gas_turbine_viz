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

st.markdown("# 💨 Gas Turbine Analysis 💨 ")
st.markdown("""
This dashboard provided an overview of gas turbine data around the world. Some of the main question we aimed to answer are
- Which engine is degrading the most?
- Which plant has produced more kWh and with what overall efficiency?
- Which plant has better availability, or has had the most shutdowns or downtime so we can steer maintenance policies to drive better outcomes in the lowest performers?
- Which plants produce more CO2 around the world, by country, by continent?
""")

sample_all_df, sample_site_df = get_data_from_cockroachdb()

@st.cache
def get_data():
    all_df = pd.read_csv("data/all_data.csv")
    site_df = pd.read_csv("data/site_metadata.csv")
    temp_df = all_df.merge(site_df, on=["CUSTOMER_NAME", "PLANT_NAME"])
    all_df["THRM_EFF"] = temp_df["POWER"] / (temp_df["FUEL_FLOW"] * temp_df["FUEL_LHV"])
    all_df["datetime"] = pd.to_datetime(all_df["datetime"])

    return all_df, site_df

st.subheader("Overview of the Engine Data analysed")
st.dataframe(data=sample_all_df, use_container_width=True)

st.subheader("Overview of the Site Data analysed")
st.dataframe(data=sample_site_df, use_container_width=True)

all_df, site_df = get_data()

# group by PLANT_NAME and sum the POWER
power_df = all_df.groupby(["PLANT_NAME"]).sum().reset_index()

# join the power_df with site_df
power_df = power_df.merge(site_df, on="PLANT_NAME")
# plot of map

st.subheader("Global Overview of Power Plants")

px.set_mapbox_access_token(MAPBOX_TOKEN)

fig = px.scatter_mapbox(
    power_df,
    lat="LATITUDE",
    lon="LONGITUDE",
    # hover_name="CONTINENT",
    # color="CONTINENT",
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

st.subheader("Analysis by Each Plant")
st.text("Select a plant using the selection box below!")

plant_name = st.selectbox("Select a plant", all_df["PLANT_NAME"].unique(), index=0)

# filter all_df by plant_name
all_df_filtered = all_df[all_df["PLANT_NAME"] == plant_name]

fig = px.line(
    all_df_filtered,
    x="datetime",
    y="THRM_EFF",
    color="ENGINE_ID",
    title="Power over time for each ENGINE_ID",
)


st.plotly_chart(fig, use_container_width=True)
fig = px.line(all_df_filtered, x="datetime", y="THRM_EFF", color="ENGINE_ID", title=f"Thermal Efficiency over time for each engine in {plant_name}")
st.plotly_chart(fig, use_container_width=True)
st.subheader("Downtime and Availability of Plants")
avail_df = all_df.groupby(["PLANT_NAME", "ENGINE_ID"])[['CMP_SPEED']] \
  .agg(lambda x: x.eq(0).sum()).reset_index()

avail_df['CMP_SPEED'] = avail_df['CMP_SPEED'] / 7

# for each plant name, plot a horizontal grouped bar chart on CMP_SPEED
fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=False,
                    shared_yaxes=True, horizontal_spacing=0)     
fig.append_trace(go.Bar(x=avail_df['PLANT_NAME'],
                      y=avail_df['CMP_SPEED'],      
                      text=avail_df["CMP_SPEED"].map('{:,.0f}'.format), #Display the numbers with thousands separators in hover-over tooltip
                      textposition='inside',
                      orientation='v',
                      showlegend=False,
                      marker_color='#82DE94'),
                      1, 1) # 1,1 represents row 1 column 1 in the plot grid
fig.update_xaxes(showticklabels=False, title_text="Plant Name", row=1, col=1)
fig.update_xaxes(showticklabels=False, title_text="CMP_SPEED", row=1, col=2)

fig.update_layout(title_text="Average Downtime in Hours per week for each plant",
                  xaxis1={'side': 'top'},
                  xaxis2={'side': 'top'},)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
From here we can see that the THERAPEUTIC-LIONFISH plant has the highest downtime among all and that
corrective measures can be implemented to increase the efficiency of the plant. On the other hand, 
the SPRITUAL-POLECAT plant has the lowest downtime and can be used as a benchmark for other plants.
""")