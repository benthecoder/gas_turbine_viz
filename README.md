# Gas Turbine Data Visualization

## Cockroach DB ingestion

### connect to cockroach

```sql
cockroach sql --url "postgresql://benedict<PASSWORD>@free-tier14.aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Dshard-oyster-5558"
```

### import data from s3 csv files

```sql
IMPORT INTO ENGINE(location_id,datetime,CMP_SPEED,POWER, FUEL_FLOW,CO2,CUSTOMER_NAME,PLANT_NAME,ENGINE_ID)
CSV DATA ('https://hackathonfiles123.s3.amazonaws.com/all_data.csv');
```

```sql
IMPORT INTO SITE(CUSTOMER_NAME,PLANT_NAME,LATITUDE,LONGITUDE,ELEVATION,FUEL_N2_MOL_PCT,FUEL_MW,FUEL_LHV,CO2_FUEL_RATIO) CSV DATA ('https://hackathonfiles123.s3.amazonaws.com/site_metadata.csv');
```
