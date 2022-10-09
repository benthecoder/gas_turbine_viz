import streamlit as st
import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd


load_dotenv()
PASSWORD = os.getenv("COCKROACH_PW")
URI = f"postgresql://benedict:{PASSWORD}@free-tier14.aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Dshard-oyster-5558"


def convert_to_numeric(cols, df):
    df[cols] = df[cols].apply(pd.to_numeric)

    return df


@st.cache
def get_data_from_cockroachdb():
    conn = psycopg2.connect(URI)

    with conn.cursor() as cur: 
        cur.execute("SELECT * FROM public.site")
        print('run here already 2')
        res = cur.fetchall()
        conn.commit()

        cur.execute("SELECT * FROM public.engine")
        res = cur.fetchall()
        conn.commit()
        print('run here already')
        all_df = pd.DataFrame.from_records(res)


        site_df = pd.DataFrame.from_records(res)

    # set first row as column names
    all_df, all_df.columns = all_df[1:], all_df.iloc[0]
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

if __name__ == "__main__":
    get_data_from_cockroachdb()
