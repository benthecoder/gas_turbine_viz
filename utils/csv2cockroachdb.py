import os
import psycopg2

conn = psycopg2.connect(os.environ["DATABASE_URL"])

with conn.cursor() as cur:

    sql1 = """
    CREATE TABLE ENGINE(
        location_id VARCHAR,
        datetime VARCHAR,
        CMP_SPEED VARCHAR,
        POWER VARCHAR,
        FUEL_FLOW VARCHAR,
        CO2 VARCHAR,
        CUSTOMER_NAME VARCHAR,
        PLANT_NAME VARCHAR,
        ENGINE_ID VARCHAR
    );
    """

    # cur.execute(sql1)

    sql2 = """
        CREATE TABLE SITE(
            CUSTOMER_NAME VARCHAR,
            PLANT_NAME VARCHAR,
            LATITUDE VARCHAR,
            LONGITUDE VARCHAR,
            ELEVATION VARCHAR,
            FUEL_N2_MOL_PCT VARCHAR,
            FUEL_MW VARCHAR,
            FUEL_LHV VARCHAR,
            CO2_FUEL_RATIO VARCHAR
    );
    """

    cur.execute(sql2)

    # res = cur.execute("SELECT * FROM ENGINE LIMIT 10")

    # res = cur.fetchall()
    conn.commit()
    # print(res)
