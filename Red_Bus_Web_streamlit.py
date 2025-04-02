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

@st.cache_data(ttl=300)
def get_route_pairs():
    route_query = "SELECT DISTINCT route_name FROM bus_routes ORDER BY route_name"
    route_df = execute_query(route_query)
    route_pairs = [(r.split(' to ')[0].strip(), r.split(' to ')[1].strip()) for r in route_df['route_name'] if ' to ' in r]
    return route_pairs

def get_destinations_for_origin(origin):
    return sorted({dest for src, dest in get_route_pairs() if src == origin})

def get_all_origins():
    return sorted({src for src, dest in get_route_pairs()})

if 'from_location' not in st.session_state:
    st.session_state.from_location = None
if 'to_location' not in st.session_state:
    st.session_state.to_location = None

st.sidebar.header("Filter Options")
st.sidebar.markdown("**Journey Details**")

all_origins = get_all_origins()
from_location = st.sidebar.selectbox("From", all_origins, index=None, placeholder="Select departure city", key='from_location')

to_location = None
if from_location:
    to_location = st.sidebar.selectbox("To", get_destinations_for_origin(from_location), index=None, placeholder="Select arrival city", key='to_location')

st.sidebar.markdown("**Departure Time**")
departure_time = st.sidebar.selectbox("Time of Departure", ["All", "Evening (6PM-12AM)", "Midnight (12AM-6AM)", "Morning (6AM-12PM)", "Afternoon (12PM-6PM)"], index=0)

st.sidebar.markdown("**Bus Type**")
ac_option = st.sidebar.radio("AC Type", ["All", "AC", "Non-AC"], index=0)

st.sidebar.markdown("**Seat Type**")
seat_type = st.sidebar.radio("Seating Type", ["All", "Sleeper", "Seater"], index=0)

st.sidebar.markdown("**Star Rating Range**")
star_min, star_max = st.sidebar.slider("Select star rating range", 1.0, 5.0, (1.0, 5.0), 0.5)

st.sidebar.markdown("**Price Range**")
price_range = st.sidebar.slider("Select price range", 0, 10000, (0, 10000), 100)

def load_filtered_data():
    base_query = "SELECT * FROM bus_routes WHERE 1=1"
    params = []
    
    if st.session_state.from_location:
        base_query += " AND route_name LIKE %s"
        params.append(f"{st.session_state.from_location} to %")
    
    if st.session_state.to_location:
        base_query += " AND route_name LIKE %s"
        params.append(f"% to {st.session_state.to_location}")
    
    time_filters = {
        "Evening (6PM-12AM)": ("18:00:00", "23:59:59"),
        "Midnight (12AM-6AM)": ("00:00:00", "05:59:59"),
        "Morning (6AM-12PM)": ("06:00:00", "11:59:59"),
        "Afternoon (12PM-6PM)": ("12:00:00", "17:59:59"),
    }
    if departure_time in time_filters:
        base_query += " AND CAST(departing_time AS TIME) BETWEEN %s AND %s"
        params.extend(time_filters[departure_time])
    
    if ac_option == "AC":
        base_query += " AND bus_type LIKE %s"
        params.append("%AC%")
    elif ac_option == "Non-AC":
        base_query += " AND bus_type NOT LIKE %s"
        params.append("%AC%")
    
    if seat_type in ["Seater", "Sleeper"]:
        base_query += " AND bus_type LIKE %s"
        params.append(f"%{seat_type}%")
    
    base_query += " AND star_rating BETWEEN %s AND %s AND price BETWEEN %s AND %s"
    params.extend([star_min, star_max, price_range[0], price_range[1]])
    
    return execute_query(base_query, params)

filtered_df = load_filtered_data()

if not filtered_df.empty:
    filtered_df[['From', 'To']] = filtered_df['route_name'].str.split(' to ', n=1, expand=True)
    ac_count = filtered_df['bus_type'].str.contains('AC', case=False).sum()
    non_ac_count = len(filtered_df) - ac_count
    st.write(f"### Available Buses (Showing {len(filtered_df)} buses), {ac_count} AC and {non_ac_count} Non-AC")
    selected_columns = st.multiselect("Select columns to view", filtered_df.columns.tolist(), default=['From', 'To', 'departing_time', 'reaching_time'])
    if selected_columns:
        st.dataframe(filtered_df[selected_columns], use_container_width=True)
    else:
        st.warning("Please select at least one column to display")
else:
    st.warning("No buses found matching your criteria")
