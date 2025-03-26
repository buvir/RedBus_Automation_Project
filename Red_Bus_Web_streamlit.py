# RedBus Model Website in Streamlit

# Commands to run:
# .venv\Scripts\activate
# pip install requests pillow streamlit psycopg2 pandas
# streamlit run C:\Users\USER\Desktop\RedBus_Automation_Project\Red_Bus_Web_streamlit.py

import streamlit as st
import pandas as pd
import psycopg2
from PIL import Image

# Set page to full width
st.set_page_config(page_title="RED BUS.IN", layout="wide")

# Load local logo
LOCAL_LOGO_PATH = r"C:\Users\USER\Desktop\RedBus_Automation_Project\red bus logo.png"

try:
    logo = Image.open(LOCAL_LOGO_PATH)
    logo = logo.resize((250, 250))
except Exception as e:
    st.error(f"Failed to load logo: {str(e)}")
    logo = None

# Create header
col1, col2 = st.columns([1, 5])
with col1:
    if logo:
        st.image(logo)
with col2:
    st.markdown("<h1 style='color: red;'>RedBus Data Booking</h1>", unsafe_allow_html=True)

# PostgreSQL connection
DB_CONFIG = {
    "dbname": "red_bus",
    "user": "postgres",
    "password": "sample12",
    "host": "localhost",
    "port": "5432",
}

@st.cache_data
def get_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = "SELECT * FROM bus_routes"  
    df = pd.read_sql(query, conn)
    conn.close()
    
    if "bustype" in df.columns:
        df["bustype"] = df["bustype"].astype(str).str.strip()
    
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    
    return df

# Load Data
df = get_data()

# Sidebar filters
st.sidebar.header("Filter Options")

# 1. Route Name Filter
route_names = df["route_name"].unique().tolist()
route_options = ["All"] + route_names
selected_routes = st.sidebar.multiselect(
    "Select Route Name(s)", 
    route_options,
    default=None,
    help="Select 'All' to include all routes"
)

# 2. Star Rating Filter
if "star_rating" in df.columns:
    star_ratings = sorted(df["star_rating"].dropna().unique().tolist())
    star_options = ["All"] + star_ratings
    selected_stars = st.sidebar.multiselect(
        "Select Star Rating(s)",
        star_options,
        default=None,
        help="Select 'All' to include all ratings"
    )

# 3. Bus Type Filter  
if "bus_type" in df.columns:
    bus_types = sorted(df["bus_type"].dropna().unique().tolist())
    bus_options = ["All"] + bus_types
    selected_types = st.sidebar.multiselect(
        "Select Bus Type(s)",
        bus_options,
        default=None,
        help="Select 'All' to include all bus types"
    )

# 4. Price Range Slider
if "price" in df.columns:
    price_min = int(df["price"].min())
    price_max = int(df["price"].max())
    price_range = st.sidebar.slider(
        "Select Price Range",
        price_min, price_max,
        (price_min, price_max),
        help="Drag to set price range"
    )

# Apply Filters with proper "All" handling
filtered_df = df.copy()

# Route filter
if selected_routes:
    if "All" in selected_routes:
        pass  # Show all routes
    else:
        filtered_df = filtered_df[filtered_df["route_name"].isin(selected_routes)]

# Star rating filter
if "star_rating" in df.columns and selected_stars:
    if "All" in selected_stars:
        pass  # Show all ratings
    else:
        filtered_df = filtered_df[filtered_df["star_rating"].isin(selected_stars)]

# Bus type filter  
if "bus_type" in df.columns and selected_types:
    if "All" in selected_types:
        pass  # Show all bus types
    else:
        filtered_df = filtered_df[filtered_df["bus_type"].isin(selected_types)]

# Price filter (always applies unless at full range)
if "price" in df.columns:
    if price_range != (price_min, price_max):
        filtered_df = filtered_df[
            (filtered_df["price"] >= price_range[0]) & 
            (filtered_df["price"] <= price_range[1])
        ]

# Column Selection
selected_columns = st.sidebar.multiselect(
    "Select columns to view", 
    df.columns, 
    default=df.columns
)

# Display Data
st.write(f"### Filtered Bus Data (Showing {len(filtered_df)} of {len(df)} records)")
# Custom CSS
st.markdown("""
<style>
    /* Red headers */
    .stDataFrame thead tr th {
        background-color: #ff0000 !important;
        color: white !important;
    }
    
    /* Red border */
    .stDataFrame {
        border: 2px solid #ff0000 !important;
        border-radius: 5px !important;
    }
</style>
""", unsafe_allow_html=True)
st.dataframe(filtered_df[selected_columns], use_container_width=True)

# Show unfiltered count when filters are active
if (len(filtered_df) != len(df)):
    st.sidebar.markdown(f"**Filtered:** {len(filtered_df)}/{len(df)} buses")