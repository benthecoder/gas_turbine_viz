import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
PASSWORD = os.getenv("COCKROACH_PW")

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

    sql1 = """
    DROP TABLE IF EXISTS ENGINE
    CREATE TABLE ENGINE(
        location_id INT,
        datetime TIMESTAMP,
        CMP_SPEED FLOAT,
        POWER FLOAT,
        FUEL_FLOW FLOAT,
        CO2 FLOAT,
        CUSTOMER_NAME VARCHAR,
        PLANT_NAME VARCHAR,
        ENGINE_ID INT
    );
    """

    cur.execute(sql1)

    sql2 = """
        DROP TABLE IF EXISTS SITE
        CREATE TABLE SITE(
            CUSTOMER_NAME VARCHAR,
            PLANT_NAME VARCHAR,
            LATITUDE FLOAT,
            LONGITUDE FLOAT,
            ELEVATION FLOAT,
            FUEL_N2_MOL_PCT FLOAT,
            FUEL_MW FLOAT,
            FUEL_LHV FLOAT,
            CO2_FUEL_RATIO FLOAT,
            CONTINENT VARCHAR,
            COUNTRY_CODE VARCHAR,
            COUNTRY VARCHAR
    );
    """

    cur.execute(sql2)

    # res = cur.execute("SELECT * FROM ENGINE LIMIT 10")

    # res = cur.fetchall()
    conn.commit()
    # print(res)
