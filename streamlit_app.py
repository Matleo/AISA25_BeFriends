import streamlit as st
import requests

API_URL = "https://your-api-url.com/events/search"  # Replace with your FastAPI endpoint

st.set_page_config(page_title="Event Search", page_icon="🎉", layout="wide")
st.title("🔎 Event Search Portal")

with st.form("search_form"):
    search_text = st.text_input("Search for events", "")
    city = st.text_input("City", "")
    category = st.text_input("Category", "")
    date_from = st.date_input("From date", None)
    date_to = st.date_input("To date", None)
    submitted = st.form_submit_button("Search")

params = {}
if search_text:
    params["text"] = search_text
if city:
    params["city"] = city
if category:
    params["category"] = category
if date_from:
    params["date_from"] = str(date_from)
if date_to:
    params["date_to"] = str(date_to)

if submitted:
    with st.spinner("Searching events..."):
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            events = response.json()
        except Exception as e:
            st.error(f"Error fetching events: {e}")
            events = []
    if events:
        st.success(f"Found {len(events)} event(s)")
        for event in events:
            with st.container():
                st.markdown(f"### {event.get('name', 'No Name')}")
                st.write(f"**Date:** {event.get('date', 'N/A')}")
                st.write(f"**City:** {event.get('city', 'N/A')}")
                st.write(f"**Category:** {event.get('category', 'N/A')}")
                st.write(f"**Description:** {event.get('description', 'N/A')}")
                st.write(f"**Tags:** {', '.join(event.get('tags', [])) if event.get('tags') else 'N/A'}")
                st.divider()
    else:
        st.info("No events found for your search.")
else:
    st.info("Enter search criteria and click 'Search' to find events.")
