import streamlit as st
import pandas as pd
import psycopg2

# Set page to full width
st.set_page_config(page_title="Data Viewer", layout="wide")

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "red_bus",
    "user": "postgres",
    "password": "sample12",
    "host": "localhost",
    "port": "5432",
}

# Function to fetch data from PostgreSQL
@st.cache_data
def get_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = "SELECT * FROM bus_routes"  
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load Data
df = get_data()

# Sidebar multi-select for column selection
selected_columns = st.sidebar.multiselect("Select columns to view", df.columns, default=df.columns[:10])

# Display selected columns
st.write("### Selected Data")
st.dataframe(df[selected_columns],use_container_width=True)

# # Create 5 Tabs
# tab1, tab2, tab3, tab4, tab5,tab6,tab7,tab8,tab9,tab10 = st.tabs(["Tab 1", "Tab 2", "Tab 3", "Tab 4", "Tab 5","Tab 6","Tab 7","Tab 8","Tab 9","Tab 10"])

# # Display different sets of data in each tab
# with tab1:
#     st.write("id")
#     st.dataframe(df[0])

# with tab2:
#     st.write("route_name")
#     st.dataframe(df[1])

# with tab3:
#     st.write("route_link")
#     st.dataframe(df[2])

# with tab4:
#     st.write("busname")
#     st.dataframe(df[3])

# with tab5:
#     st.write("bustype")
#     st.dataframe(df[4])

# with tab6:
#     st.write("departing_time")
#     st.dataframe(df[5])

# with tab7:
#     st.write("bustype")
#     st.dataframe(df[6])

# with tab8:
#     st.write("bustype")
#     st.dataframe(df[7])

# with tab9:
#     st.write("bustype")
#     st.dataframe(df[8])

# with tab10:
#     st.write("bustype")
#     st.dataframe(df[9])

