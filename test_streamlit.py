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

    st.title("Red Bus Database Viewer")

    # Fetch data from the database
    cursor.execute("SELECT * FROM bus_routes")
    results = cursor.fetchall()

    # Get column names from cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Convert to DataFrame
    df = pd.DataFrame(results, columns=column_names)

    # Display DataFrame
    st.write("### Bus Routes Data:")
    st.dataframe(df)  # Use st.dataframe() for better display

    # Sidebar column selector
    selected_column = st.sidebar.selectbox("Select a column to view", df.columns)
    st.write(f"### Displaying Column: {selected_column}")
    st.write(df[selected_column])

except Exception as e:
    st.error(f"An error occurred: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
