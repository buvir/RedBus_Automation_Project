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

# Sidebar: First Dropdown - Select Route Name
route_names = df["route_name"].unique().tolist()
selected_route = st.sidebar.selectbox("Select Route Name", route_names)

# Filter data based on selected route
filtered_df = df[df["route_name"] == selected_route]

# Sidebar: Second Dropdown - Select Route (if applicable)
selected_route_detail = None  # Default to None

if "route" in df.columns and not filtered_df.empty:  # Ensure 'route' column exists & data is available
    routes = filtered_df["route"].unique().tolist()
    
    if routes:  # Check if there are routes available
        selected_route_detail = st.sidebar.selectbox("Select Route", routes)
        filtered_df = filtered_df[filtered_df["route"] == selected_route_detail]

# Sidebar multi-select for additional column selection
selected_columns = st.sidebar.multiselect("Select columns to view", df.columns, default=df.columns)

# Display filtered Data
if selected_route_detail:  # Only show route detail if selected
    st.write(f"### Selected Data for {selected_route} - {selected_route_detail}")
else:
    st.write(f"### Selected Data for {selected_route}")

st.dataframe(filtered_df[selected_columns], use_container_width=True)
# # Sidebar multi-select for column selection
# selected_columns = st.sidebar.multiselect("Select columns to view", df.columns, default=df.columns[:10])

# # Display selected columns
# st.write("### Selected Data")
# st.dataframe(df[selected_columns],use_container_width=True)
