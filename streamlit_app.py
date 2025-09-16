
import streamlit as st
import requests
from datetime import date as dt_date

# Set to your local FastAPI endpoint
API_URL = "http://localhost:8000/search"

st.set_page_config(page_title="Event Search", page_icon="🎉", layout="wide")
st.title("🔎 Event Search Portal")

# Example options for selectboxes (replace with dynamic fetch if needed)
CITIES = ["", "Berlin", "Basel", "Vienna", "Zurich"]
CATEGORIES = ["", "Music", "Clubnacht / Tanzparty", "Theater", "Art", "Workshop"]

@st.cache_data(show_spinner=False)
def fetch_events(params):
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

with st.form("search_form"):
    search_text = st.text_input("Search for events", "")
    city = st.selectbox("City", CITIES)
    category = st.selectbox("Category", CATEGORIES)
    col1, col2 = st.columns(2)
    with col1:
        date_from = st.date_input("From date", None)
    with col2:
        date_to = st.date_input("To date", None)
    submitted = st.form_submit_button("Search")

params = {}
if search_text:
    params["query_text"] = search_text
if city:
    params["city"] = city
if category:
    params["category"] = category
if date_from and date_from != dt_date.today():
    params["date_from"] = str(date_from)
if date_to and date_to != dt_date.today():
    params["date_to"] = str(date_to)


if submitted:
    with st.spinner("Searching events..."):
        try:
            events = fetch_events(params)
        except Exception as e:
            st.error(f"Error fetching events: {e}")
            events = None
    st.write("Raw API response:", events)
    st.write("Type of events:", type(events))
    # Handle if events is a dict with a key (e.g., 'results', 'cards')
    if isinstance(events, dict):
        # Try common keys including 'cards'
        for key in ("results", "data", "events", "cards"):
            if key in events and isinstance(events[key], list):
                events = events[key]
                break
    # Handle if events is a string (error or message)
    if isinstance(events, str):
        st.error(f"API returned a string: {events}")
        events = None
    # Now only show error if events is not a list and not None
    if events is None:
        pass  # error already shown above
    elif not isinstance(events, list):
        st.error(f"API did not return a list of events. Type: {type(events)} Value: {events}")
    elif len(events) == 0:
        st.info("No events found for your search.")
    else:
        st.success(f"Found {len(events)} event(s)")
        for event in events:
            if not isinstance(event, dict):
                st.warning(f"Skipping non-dict event: {event}")
                continue
            # Prefer 'name', fallback to 'title', then 'No Name'
            event_name = event.get('name') or event.get('title') or 'No Name'
            with st.expander(f"{event_name} ({event.get('date', 'N/A')})", expanded=False):
                cols = st.columns([2, 1, 1])
                cols[0].markdown(f"**Description:** {event.get('description', 'N/A')}")
                cols[1].markdown(f"**City:** {event.get('city', 'N/A')}")
                cols[2].markdown(f"**Category:** {event.get('category', 'N/A')}")
                st.markdown(f"**Venue:** {event.get('venue', 'N/A')}")
                st.markdown(f"**Price:** {event.get('price', 'N/A')}")
                tags = event.get('tags', [])
                st.markdown(f"**Tags:** {', '.join(tags) if tags else 'N/A'}")
else:
    st.info("Enter search criteria and click 'Search' to find events.")
