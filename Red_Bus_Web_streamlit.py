import streamlit as st
import pandas as pd
import psycopg2
from PIL import Image
from datetime import time

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
    st.markdown("<h1 style='color: red;'>RedBus Booking</h1>", unsafe_allow_html=True)

# PostgreSQL connection
DB_CONFIG = {
    "dbname": "red_bus",
    "user": "postgres",
    "password": "sample12",
    "host": "localhost",
    "port": "5432",
}

@st.cache_data(ttl=300)
def execute_query(query, params=None):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        return pd.DataFrame(results, columns=columns)
    finally:
        cursor.close()
        conn.close()

@st.cache_data(ttl=3600)  # Cache longer since this rarely changes
def get_route_pairs():
    route_query = "SELECT DISTINCT route_name FROM bus_routes ORDER BY route_name"
    route_df = execute_query(route_query)
    route_pairs = [(r.split(' to ')[0].strip(), r.split(' to ')[1].strip()) for r in route_df['route_name'] if ' to ' in r]
    return route_pairs

def get_destinations_for_origin(origin):
    return sorted({dest for src, dest in get_route_pairs() if src == origin})

def get_all_origins():
    return sorted({src for src, dest in get_route_pairs()})

# Initialize session state
if 'from_location' not in st.session_state:
    st.session_state.from_location = None
if 'to_location' not in st.session_state:
    st.session_state.to_location = None
if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

# Sidebar filters
st.sidebar.header("Filter Options")
st.sidebar.markdown("**Journey Details**")

all_origins = get_all_origins()
from_location = st.sidebar.selectbox(
    "From", 
    all_origins, 
    index=None,
    placeholder="Select departure city",
    key='from_location_select'
)

to_location = None
if st.session_state.from_location_select:
    destinations = get_destinations_for_origin(st.session_state.from_location_select)
    to_location = st.sidebar.selectbox(
        "To", 
        destinations, 
        index=None,
        placeholder="Select arrival city",
        key='to_location_select'
    )

# Only show other filters when route is selected
if st.session_state.from_location_select and st.session_state.to_location_select:
    st.sidebar.markdown("**Departure Time**")
    departure_time = st.sidebar.selectbox(
        "Time of Departure", 
        ["All", "Evening (6PM-12AM)", "Midnight (12AM-6AM)", "Morning (6AM-12PM)", "Afternoon (12PM-6PM)"], 
        index=0
    )

    st.sidebar.markdown("**Bus Type**")
    ac_option = st.sidebar.radio("AC Type", ["All", "AC", "Non-AC"], index=0)

    st.sidebar.markdown("**Seat Type**")
    seat_type = st.sidebar.radio("Seating Type", ["All", "Sleeper", "Seater"], index=0)

    st.sidebar.markdown("**Star Rating Range**")
    star_min, star_max = st.sidebar.slider("Select star rating range", 1.0, 5.0, (1.0, 5.0), 0.5)

    st.sidebar.markdown("**Price Range**")
    price_range = st.sidebar.slider("Select price range", 0, 10000, (0, 10000), 100)

    # Search button
    if st.sidebar.button("Search Buses"):
        st.session_state.from_location = st.session_state.from_location_select
        st.session_state.to_location = st.session_state.to_location_select
        st.session_state.search_clicked = True

# Main content area
if st.session_state.search_clicked:
    @st.cache_data(ttl=300, show_spinner="Loading bus data...")
    def load_filtered_data(from_loc, to_loc):
        base_query = """
        SELECT 
            id,
            route_name,
            bus_name,
            bus_type,
            departing_time::time as departing_time,
            reaching_time::time as reaching_time,
            duration,
            seats_available,
            price,
            star_rating
        FROM bus_routes
        WHERE route_name = %s
        """
        route_name = f"{from_loc} to {to_loc}"
        params = [route_name]
        
        # Add time filter if selected
        if departure_time != "All":
            time_filters = {
                "Evening (6PM-12AM)": ("18:00:00", "23:59:59"),
                "Midnight (12AM-6AM)": ("00:00:00", "05:59:59"),
                "Morning (6AM-12PM)": ("06:00:00", "11:59:59"),
                "Afternoon (12PM-6PM)": ("12:00:00", "17:59:59"),
            }
            time_range = time_filters[departure_time]
            base_query += " AND departing_time::time BETWEEN %s AND %s"
            params.extend(time_range)
        
        # Add AC filter
        if ac_option == "AC":
            base_query += " AND bus_type LIKE %s"
            params.append("%AC%")
        elif ac_option == "Non-AC":
            base_query += " AND bus_type NOT LIKE %s"
            params.append("%AC%")
        
        # Add seat type filter
        if seat_type in ["Seater", "Sleeper"]:
            base_query += " AND bus_type LIKE %s"
            params.append(f"%{seat_type}%")
        
        # Add rating and price filters
        base_query += " AND star_rating BETWEEN %s AND %s AND price BETWEEN %s AND %s"
        params.extend([star_min, star_max, price_range[0], price_range[1]])
        
        return execute_query(base_query, params)

    # Load initial data
    filtered_df = load_filtered_data(st.session_state.from_location, st.session_state.to_location)

    if not filtered_df.empty:
        # Display results
        ac_count = filtered_df['bus_type'].str.contains('AC', case=False).sum()
        non_ac_count = len(filtered_df) - ac_count
        
        total_available_seats = filtered_df['seats_available'].sum()
        sleeper_buses = filtered_df['bus_type'].str.contains('Sleeper', case=False)
        sleeper_available = filtered_df[sleeper_buses]['seats_available'].sum()
        seater_available = total_available_seats - sleeper_available
        
        st.write(f"### Available Buses from {st.session_state.from_location} to {st.session_state.to_location}")
        st.write(f"**Showing {len(filtered_df)} buses**")
        st.write(f"- AC Buses: {ac_count} | Non-AC Buses: {non_ac_count}")
        st.write(f"- Total Available Seats: {total_available_seats:,}")
        st.write(f"- Sleeper Seats: {sleeper_available:,} | Seater Seats: {seater_available:,}")
        
        # Display options
        default_columns = [
            'bus_name', 'bus_type', 'departing_time', 
            'reaching_time', 'duration', 'seats_available', 
            'price', 'star_rating'
        ]
        
        selected_columns = st.multiselect(
            "Select columns to view", 
            filtered_df.columns.tolist(), 
            default=default_columns
        )
        
        if selected_columns:
            display_df = filtered_df[selected_columns].copy()
            if 'price' in display_df.columns:
                display_df['price'] = display_df['price'].apply(lambda x: f"₹{x:,.2f}")
            if 'seats_available' in display_df.columns:
                display_df['seats_available'] = display_df['seats_available'].apply(lambda x: f"{x:,}")
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Please select at least one column to display")
    else:
        st.warning("No buses available for this route with selected filters")
else:
    st.info("Please select your journey details and click 'Search Buses'")