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
    
    # Ensure 'bustype' is a string and strip spaces
    if "bustype" in df.columns:
        df["bustype"] = df["bustype"].astype(str).str.strip()
    
    # Ensure 'price' is numeric
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    
    return df

# Load Data
df = get_data()

# Sidebar: Select Route Name
route_names = df["route_name"].unique().tolist()
selected_route = st.sidebar.selectbox("Select Route Name", route_names)

# Filter data based on selected route
filtered_df = df[df["route_name"] == selected_route]

# Sidebar: Select Route (if applicable)
if "route" in df.columns and not filtered_df.empty:
    routes = filtered_df["route"].dropna().unique().tolist()
    if routes:
        selected_route_detail = st.sidebar.selectbox("Select Route", routes)
        filtered_df = filtered_df[filtered_df["route"] == selected_route_detail]

# Sidebar: Select Star Rating (if applicable)
if "star_rating" in df.columns and not filtered_df.empty:
    star_ratings = sorted(filtered_df["star_rating"].dropna().unique().tolist())
    if star_ratings:
        selected_star_rating = st.sidebar.selectbox("Select Star Rating", star_ratings)
        filtered_df = filtered_df[filtered_df["star_rating"] == selected_star_rating]

# Sidebar: Select Bustype (if applicable)
# Sidebar: Select Bustype (if applicable)
if "bus_type" in df.columns and not filtered_df.empty:  # ✅ Corrected empty check
    bustypes = sorted(filtered_df["bus_type"].dropna().unique().tolist())  # Drop NaN values and sort

    # Debugging: Check available bustypes
    # if not bustypes:
    #     st.sidebar.warning("No bustype data available for the selected filters.")
    # else:
    #     st.sidebar.write("Available Bustypes:", bustypes)  # Debugging print

    if bustypes:  # Ensure values exist
        selected_bustype = st.sidebar.selectbox("Select Bustype", bustypes)

        # Debugging: Check what is being selected
        st.sidebar.write(f"Selected Bustype: {selected_bustype}")

        # Apply filter
        filtered_df = filtered_df[filtered_df["bus_type"] == selected_bustype]
else:
    st.sidebar.warning("Bustype column missing or no data available.")


# Sidebar: Price Slider (if applicable)
# Sidebar: Price Slider (if applicable)
if "price" in filtered_df.columns and not filtered_df["price"].dropna().empty:
    min_price = int(filtered_df["price"].min())
    max_price = int(filtered_df["price"].max())

    # Ensure valid min/max values
    if min_price == max_price:  # If only one unique price, adjust range
        min_price = max(0, min_price - 100)  # Set a reasonable minimum
        max_price = min_price + 200  # Set a reasonable range

    selected_price_range = st.sidebar.slider(
        "Select Price Range", min_price, max_price, (min_price, max_price)
    )

    # Filter Data Based on Price Range
    filtered_df = filtered_df[
        (filtered_df["price"] >= selected_price_range[0]) & 
        (filtered_df["price"] <= selected_price_range[1])
    ]
else:
    st.sidebar.warning("No price data available for filtering.")

# Sidebar: Column Selection
selected_columns = st.sidebar.multiselect("Select columns to view", df.columns, default=df.columns)

# Display Data
st.write(f"### Selected Data for {selected_route}")
st.dataframe(filtered_df[selected_columns], use_container_width=True)


# if r=="selected_route_detail":
#     progress=st.progress(0)
#     for i in range(100):
#         time.sleep(0.1)
#         progress.progress(i+1)
#     #st.balloons()
#     st.write('about us page')
#     st.success("super!")
#     st.error("error!")
#     st.exception("exception?")
#     st.warning("warning")
#     st.info("info")

# # Sidebar multi-select for column selection
# selected_columns = st.sidebar.multiselect("Select columns to view", df.columns, default=df.columns[:10])

# # Display selected columns
# st.write("### Selected Data")
# st.dataframe(df[selected_columns],use_container_width=True)
