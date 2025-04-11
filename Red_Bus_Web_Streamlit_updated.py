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

@st.cache_data(ttl=3600)
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
if 'seats_required' not in st.session_state:
    st.session_state.seats_required = 1

# Sidebar filters
st.sidebar.header("Filter Options")
st.sidebar.markdown("**Journey Details**")

all_origins = get_all_origins()
from_location = st.sidebar.selectbox(
    "From", 
    all_origins, 
    index=None,
    placeholder="Select departure",
    key='from_location_select'
)

to_location = None
if st.session_state.from_location_select:
    destinations = get_destinations_for_origin(st.session_state.from_location_select)
    to_location = st.sidebar.selectbox(
        "To", 
        destinations, 
        index=None,
        placeholder="Select arrival",
        key='to_location_select'
    )

def filter_and_display_buses():
    if st.session_state.from_location_select and st.session_state.to_location_select:
        route_name = f"{st.session_state.from_location_select} to {st.session_state.to_location_select}"
        
        # Get all buses for this route first
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
        all_buses = execute_query(base_query, [route_name])
        
        if all_buses.empty:
            st.warning(f"No buses available for route: {route_name}")
            return None
        
        # Apply filters step by step and show counts
        filtered = all_buses.copy()
        filter_messages = []
        
        # Time filter - fixed comparison
        if departure_time != "All":
            time_filters = {
                "Evening (6PM-12AM)": (time(18, 0), time(23, 59, 59)),
                "Midnight (12AM-6AM)": (time(0, 0), time(5, 59, 59)),
                "Morning (6AM-12PM)": (time(6, 0), time(11, 59, 59)),
                "Afternoon (12PM-6PM)": (time(12, 0), time(17, 59, 59)),
            }
            time_start, time_end = time_filters[departure_time]
            
            # Convert pandas Series to datetime.time for comparison
            filtered['departing_time'] = filtered['departing_time'].apply(lambda x: x if isinstance(x, time) else time(x.hour, x.minute, x.second))
            
            time_mask = filtered['departing_time'].apply(
                lambda x: time_start <= x <= time_end
            )
            filtered = filtered[time_mask]
            filter_messages.append(f"⏰ {len(filtered)} buses available for {departure_time}")
        
        # Rest of the filters remain the same...
        # AC filter
        if ac_option != "All":
            if ac_option == "AC":
                ac_mask = filtered['bus_type'].str.contains('AC', case=False)
                filtered = filtered[ac_mask]
                filter_messages.append(f"❄️ {len(filtered)} AC buses available")
            else:
                ac_mask = ~filtered['bus_type'].str.contains('AC', case=False)
                filtered = filtered[ac_mask]
                filter_messages.append(f"☀️ {len(filtered)} Non-AC buses available")
        
        # Seat type filter
        if seat_type != "All":
            seat_mask = filtered['bus_type'].str.contains(seat_type, case=False)
            filtered = filtered[seat_mask]
            filter_messages.append(f"🛏️ {len(filtered)} {seat_type} buses available")
        
        # Star rating filter
        star_mask = (filtered['star_rating'] >= star_min) & (filtered['star_rating'] <= star_max)
        filtered = filtered[star_mask]
        filter_messages.append(f"⭐ {len(filtered)} buses with rating {star_min}-{star_max}")
        
        # Price filter
        price_mask = (filtered['price'] >= price_range[0]) & (filtered['price'] <= price_range[1])
        filtered = filtered[price_mask]
        filter_messages.append(f"💰 {len(filtered)} buses in price range ₹{price_range[0]}-₹{price_range[1]}")
        
        # Seats required filter
        seats_mask = filtered['seats_available'] >= st.session_state.seats_required
        filtered = filtered[seats_mask]
        filter_messages.append(f"🧑 {len(filtered)} buses with {st.session_state.seats_required}+ seats available")
        
        # Show filter progression
        with st.expander("Filter Progress", expanded=True):
            for msg in filter_messages:
                st.write(msg)
        
        return filtered
    return None

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
    star_min, star_max = st.sidebar.slider("Select star rating range",0.0, 5.0, (0.0, 5.0), 0.5)

    st.sidebar.markdown("**Price Range**")
    price_range = st.sidebar.slider("Select price range", 0, 10000, (0, 10000), 100)

    st.sidebar.markdown("**Passenger Details**")
    seats_required = st.sidebar.number_input(
        "Seats Required", 
        min_value=1, 
        max_value=20, 
        value=1,
        help="Number of seats you want to book"
    )

    # Search button
    if st.sidebar.button("Search Buses"):
        st.session_state.from_location = st.session_state.from_location_select
        st.session_state.to_location = st.session_state.to_location_select
        st.session_state.seats_required = seats_required
        st.session_state.search_clicked = True

# Main content area
if st.session_state.search_clicked:
    filtered_df = filter_and_display_buses()

    if filtered_df is not None and not filtered_df.empty:
        # Calculate statistics
        ac_count = filtered_df['bus_type'].str.contains('AC', case=False).sum()
        non_ac_count = len(filtered_df) - ac_count
        total_available_seats = filtered_df['seats_available'].sum()
        sleeper_buses = filtered_df['bus_type'].str.contains('Sleeper', case=False)
        sleeper_available = filtered_df[sleeper_buses]['seats_available'].sum()
        seater_available = total_available_seats - sleeper_available
        
        st.write(f"### Available Buses from {st.session_state.from_location} to {st.session_state.to_location}")
        st.write(f"**Found {len(filtered_df)} matching buses**")
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
    elif filtered_df is not None and filtered_df.empty:
        st.warning("No buses available matching all your selected filters. Please adjust your filters.")
    else:
        st.warning("No buses available for this route")
else:
    st.info("Please select your journey details and click 'Search Buses'")