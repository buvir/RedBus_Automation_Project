
import pandas as pd
from sqlalchemy import create_engine
host="localhost"
port='5432'
database="sampledb"
user="postgres"
password="sample12"
engine_string = f"postgresql://{user}: {password}@{host}:{port}/{database}"

engine=create_engine(engine_string)

data= pd.read_csv("iris_data.csv")
table_name = "new_table"

data.to_sql(table_name, engine, if_exists='replace', index=False)