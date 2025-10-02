from befriends.recommendation.service import RecommendationService
from befriends.catalog.repository import CatalogRepository
import streamlit as st
import logging
from typing import Dict, Any, List, Optional, Callable
from befriends.response.formatter import ResponseFormatter
def render_event_recommendations(
    filters: Optional[Dict[str, Any]] = None,
    max_events: int = 6
) -> None:
    """
    Fetch and render event recommendations as cards, optionally filtered.

    Args:
        filters (Optional[Dict[str, Any]]): Dictionary of filter values (city, category, date_from, etc.).
        max_events (int): Maximum number of events to show.
    """
    # st.markdown("---")
    st.markdown("##### Recommended for you")
    import json
    formatter = ResponseFormatter()
    # Load user profile (hardcoded fallback for sidebar)
    import datetime
    if filters is None:
        filters = {}
    try:
        with open("karolina_profile.json", "r") as f:
            profile = json.load(f)
    except Exception:
        profile = {"city": "Basel", "interests": []}
    # --- Patch: Always filter by user city (as region) and this week ---
    if profile.get("city") and not filters.get("region"):
        filters["region"] = profile["city"]
        # Only set date_from/date_to to this week (Monday-Sunday) if missing or None
        today = datetime.datetime.now().date()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        if "date_from" not in filters or filters["date_from"] is None:
            filters["date_from"] = start_of_week
        if "date_to" not in filters or filters["date_to"] is None:
            filters["date_to"] = end_of_week
    try:
        repo = CatalogRepository()
        recommender = RecommendationService(repo)
        filtered_events = recommender.recommend_events(filters, profile, max_events)
        # Debug: show number of events found and type
        # Ensure filtered_events are Event objects, not dicts
        from befriends.domain.event import Event
        from befriends.domain.search_models import SearchResult
        if filtered_events and isinstance(filtered_events[0], dict):
            filtered_events = [Event(**e) for e in filtered_events]
        cards = formatter.to_cards(SearchResult(events=filtered_events, total=len(filtered_events)))
        if not cards:
            st.info("No events found for your filters.")
        for i, card in enumerate(cards):
            render_event_card(card, key_prefix=f"rec{i}_")
    except Exception as e:
        st.warning(f"Could not load event recommendations: {e}")
        st.info("No events found for your filters.")
def render_sidebar_filters(default_city=None):
    # Logging removed
    import streamlit as st
    import datetime
    filters = st.session_state.get("filters", {})
    date_from = st.date_input(
        "From",
        value=filters.get("date_from") if filters.get("date_from") else datetime.date.today(),
        key="sidebar_date_from"
    )
    date_to = st.date_input(
        "To",
        value=filters.get("date_to") if filters.get("date_to") else (datetime.date.today() + datetime.timedelta(days=30)),
        key="sidebar_date_to"
    )
    city = st.sidebar.text_input("City", value=default_city, key="sidebar_city")
    category = st.sidebar.selectbox("Category", ["", "Music", "Sports", "Food & Drink", "Theater", "Comedy", "Family", "Outdoors", "Workshops", "Other"], key="sidebar_category")
    price_min = st.sidebar.number_input("Min price", min_value=0.0, value=0.0, step=1.0, key="sidebar_price_min")
    price_max = st.sidebar.number_input("Max price", min_value=0.0, value=0.0, step=1.0, key="sidebar_price_max")
    apply_filters = st.sidebar.button("Apply Filters", key="sidebar_apply_filters")
    reset_filters = st.sidebar.button("Reset Filters", key="sidebar_reset_filters")

    # When returning filters, log them
    sidebar_filters = {
        "city": city,
        "category": category,
        "date_from": date_from,
        "date_to": date_to,
        "price_min": price_min,
        "price_max": price_max,
        "apply_filters": apply_filters,
        "reset_filters": reset_filters,
    }
    return sidebar_filters


def render_event_card(event: Dict[str, Any], key_prefix: str = "") -> None:
    # Use new event schema fields
    thumbnail = event.get("image")  # If you have image URLs in the new schema, otherwise None
    event_name = event.get("title") or event.get("event_name") or "Event"
    # Date/time formatting
    start_dt = event.get("start_datetime")
    end_dt = event.get("end_datetime")
    if start_dt:
        try:
            # Accept both string and datetime
            import datetime
            if isinstance(start_dt, str):
                start_dt_obj = datetime.datetime.fromisoformat(start_dt)
            else:
                start_dt_obj = start_dt
            date_str = start_dt_obj.strftime("%a, %d %b %Y %H:%M")
        except Exception:
            date_str = str(start_dt)
    else:
        date_str = "Date tbd"
    # Location/region
    event_location = event.get("event_location") or event.get("venue") or ""
    region = event.get("region") or ""
    # Event type/category
    event_type = event.get("event_type") or event.get("category") or "Other"
    # Price
    price_min = event.get("price_min")
    price_max = event.get("price_max")
    currency = event.get("currency") or ""
    if price_min is not None and price_max is not None:
        if price_min == 0 and price_max == 0:
            price_label = "Free"
        elif price_min == price_max:
            price_label = f"{price_min} {currency}"
        else:
            price_label = f"{price_min}-{price_max} {currency}"
    elif price_min is not None:
        price_label = f"from {price_min} {currency}"
    else:
        price_label = "?"
    # Pills
    type_pill = f'<span class="pill category {event_type.lower().replace(" ", "-")}">{event_type}</span>'
    price_pill = f'<span class="pill price">{price_label}</span>'
    # Description
    description = event.get("description") or event.get("date_description") or "No description available."
    # Instagram
    instagram = event.get("instagram")
    insta_btn = ""
    if instagram:
        handle = instagram.lstrip("@")
        url = f"https://instagram.com/{handle}"
        insta_btn = f'<a href="{url}" target="_blank" rel="noopener noreferrer"><button class="icon" title="Instagram"><span style="font-size:1.2em;">📸</span></button></a>'
    # HTML
    html = (
        '<div class="event-card">'
        '<div class="event-card-row">'
        + (f'<div class="event-thumb-large">{thumbnail}</div>' if thumbnail else '')
        + '<div class="event-main">'
        + f'<div class="event-title">{event_name}</div>'
        + f'<div class="event-meta">{date_str} • {event_location} {region}</div>'
        + f'<div class="event-pills">{type_pill} {price_pill}</div>'
        + '</div>'
        + '</div>'
        + f'<div class="event-desc">{description}</div>'
        + '<div class="event-footer">'
        + '<button class="primary">View & Book</button>'
        + '<div class="event-footer-actions">'
        + '<button class="icon" title="Save">★</button>'
        + '<button class="icon" title="Share">🔗</button>'
        + f'{insta_btn}'
        + '</div>'
        + '</div>'
        + '</div>'
    )
    try:
        st.markdown(html, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not render event card: {e}")

def render_chips(
    chips: List[Dict[str, str]],
    key_prefix: str = "chip",
    on_select: Optional[Callable[[str], None]] = None
) -> Optional[str]:
    """
    Render horizontally scrolling suggestion chips as Streamlit buttons.

    Args:
        chips (List[Dict[str, str]]): List of chips, each as a dict with 'label' and 'value'.
        key_prefix (str, optional): Prefix for Streamlit widget keys.
        on_select (Optional[Callable[[str], None]], optional): Callback if a chip is selected.

    Returns:
        Optional[str]: The value of the selected chip, or None if no chip was selected.
    """
    cols = st.columns(len(chips))
    for i, chip in enumerate(chips):
        if cols[i].button(chip["label"], key=f"{key_prefix}_{i}"):
            if on_select:
                on_select(chip["value"])
            return chip["value"]
    return None

def inject_styles() -> None:
    """
    Inject custom CSS styles for event cards, chips, and other UI elements into the Streamlit app.
    """
    st.markdown("""
    try:
        repo = CatalogRepository()
        recommender = RecommendationService(repo)
        filtered_events = recommender.recommend_events(filters, profile, max_events)
        from befriends.domain.event import Event
        from befriends.domain.search_models import SearchResult
        if filtered_events and isinstance(filtered_events[0], dict):
            filtered_events = [Event(**e) for e in filtered_events]
        cards = formatter.to_cards(SearchResult(events=filtered_events, total=len(filtered_events)))
        if not cards:
            st.info("No events found for your filters. Showing recent events instead.")
            # Relax filters: show recent events (no filters)
            filtered_events = recommender.recommend_events({}, profile, max_events)
            cards = formatter.to_cards(SearchResult(events=filtered_events, total=len(filtered_events)))
        for i, card in enumerate(cards):
            render_event_card(card, key_prefix=f"rec{i}_")
    except Exception as e:
        st.warning(f"Could not load event recommendations: {e}")
        st.info("No events found for your filters.")
    .event-footer {display: flex; gap: 0.5em;}
    .event-footer .primary {background: #00bcd4; color: #fff; border: none; border-radius: 8px; padding: 0.4em 1.2em; font-weight: 600; cursor: pointer;}
    .event-footer .icon {background: none; border: none; font-size: 1.2em; cursor: pointer;}
    .chip-row {display: flex; overflow-x: auto; gap: 0.5em; margin: 0.5em 0;}
    .chip {background: #fff; border: 1px solid #e0e0e0; border-radius: 999px; padding: 0.4em 1.2em; font-size: 1em; box-shadow: 0 1px 3px #0001; cursor: pointer; transition: box-shadow .2s;}
    .chip:focus, .chip:hover {box-shadow: 0 2px 8px #00bcd455; outline: 2px solid #00bcd4;}
    .stChatMessage {margin-bottom: 0.5em;}
    .header-bar {position: sticky; top: 0; background: #fff; z-index: 10; padding: 1em 0 0.5em 0; border-bottom: 1px solid #eee;}
    </style>
    """, unsafe_allow_html=True)
