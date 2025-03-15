import streamlit as st
import pandas as pd

import psycopg2



try:
    # Connect to PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="red_bus",
        user="postgres",
        password="sample12"
    )
    
    cursor = connection.cursor()

    st.title("Red_Bus")

    data={
    'id':[x for x in range(1,11)],
    'route_name':[x for x in range(1,11)],
    'route_link':[x for x in range(1,11)] ,
    'busname':[x for x in range(1,11)],
    'bustype':[x for x in range(1,11)],
    'departing_time':[x for x in range(1,11)],
    'duration':[x for x in range(1,11)] ,
    'reaching_time':[x for x in range(1,11)],
    'star_rating':[x for x in range(1,11)],
    'price':[x for x in range(1,11)] ,
    'seats_available':[x for x in range(1,11)],

}
    df=pd.DataFrame(data=data)
    st.write(data)

    col=st.sidebar.selectbox (" select a column ",df.columns)
    st.write(col)

    cursor.execute("SELECT * FROM bus_routes")
    results = cursor.fetchall()
    st.write("Data from bus_routes table:")
    st.write(results)




except Exception as e:
    print(f"An error occurred while interacting with the database: {e}")

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()