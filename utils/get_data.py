import streamlit as st
import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd


load_dotenv()
PASSWORD = os.getenv("COCKROACH_PW")


def convert_to_numeric(cols, df):
    df[cols] = df[cols].apply(pd.to_numeric)

    return df


@st.cache
def get_data_from_cockroachdb():
    conn = psycopg2.connect(
        host="free-tier14.aws-us-east-1.cockroachlabs.cloud",
        port=26257,
        user="benedict",
        password=PASSWORD,
        sslmode="require",
        sslrootcert="./root.crt",
        database="defaultdb",
        options="--cluster=shard-oyster-5558",
    )

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM public.site")
        res = cur.fetchall()
        conn.commit()
        site_df = pd.DataFrame.from_records(res)

        cur.execute("SELECT * FROM public.engine LIMIT 100")
        res = cur.fetchall()
        conn.commit()
        all_df = pd.DataFrame.from_records(res)

    # set first row as column names
    all_df, all_df.columns = all_df[1:], [
        "location_id",
        "datetime",
        "CMP_SPEED",
        "POWER",
        "FUEL_FLOW",
        "CO2",
        "CUSTOMER_NAME",
        "PLANT_NAME",
        "ENGINE_ID",
    ]
    site_df, site_df.columns = site_df[1:], site_df.iloc[0]

    # convert to numeric
    site_cols = [
        "LATITUDE",
        "LONGITUDE",
        "ELEVATION",
        "FUEL_N2_MOL_PCT",
        "FUEL_MW",
        "FUEL_LHV",
        "CO2_FUEL_RATIO",
    ]
    site_df = convert_to_numeric(site_cols, site_df)

    all_cols = ["CMP_SPEED", "POWER", "FUEL_FLOW", "CO2"]

    all_df = convert_to_numeric(all_cols, all_df)

    # calculate thermal efficiency
    temp_df = all_df.merge(site_df, on=["CUSTOMER_NAME", "PLANT_NAME"])
    all_df["THRM_EFF"] = temp_df["POWER"] / (temp_df["FUEL_FLOW"] * temp_df["FUEL_LHV"])

    del temp_df

    return all_df, site_df
