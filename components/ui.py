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
    # --- Patch: Always filter by user city (as region_standardized) and this week ---
    if profile.get("city") and not filters.get("region_standardized"):
        filters["region_standardized"] = profile["city"]
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
    # Use selectbox for region, not free text
    import sqlite3
    db_path = "events.db"
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT region_standardized FROM events WHERE region_standardized IS NOT NULL AND region_standardized != '' ORDER BY region_standardized ASC;")
            region_options = [row[0] for row in cur.fetchall()]
    except Exception:
        region_options = ["Basel (CH)"]
    def trigger_apply_filter():
        st.session_state["region_changed"] = True

    region_standardized = st.sidebar.selectbox(
        "Region",
        options=region_options,
        index=region_options.index(default_city) if default_city in region_options else 0,
        key="sidebar_region_standardized",
        on_change=trigger_apply_filter
    )
    category = st.sidebar.selectbox("Category", ["", "Music", "Sports", "Food & Drink", "Theater", "Comedy", "Family", "Outdoors", "Workshops", "Other"], key="sidebar_category")
    price_min = st.sidebar.number_input("Min price", min_value=0.0, value=0.0, step=1.0, key="sidebar_price_min")
    price_max = st.sidebar.number_input("Max price", min_value=0.0, value=999.0, step=1.0, key="sidebar_price_max")
    apply_filters = st.sidebar.button("Apply Filters", key="sidebar_apply_filters") or st.session_state.get("region_changed", False)
    if "region_changed" in st.session_state:
        st.session_state["region_changed"] = False
    reset_filters = st.sidebar.button("Reset Filters", key="sidebar_reset_filters")

    # When returning filters, log them
    sidebar_filters = {
        "region_standardized": region_standardized,
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
    import logging
    description = event.get("description")
    logging.info(f"[UI] render_event_card: event_name={event.get('event_name')}, description={description}")
    if not description:
        logging.warning(f"[UI] No description available for event: {event.get('event_name')}")
        description = "No description available."
    # Instagram
    instagram = event.get("instagram")
    insta_btn = ""
    if instagram:
        if instagram.startswith("http"):
            url = instagram
        else:
            handle = instagram.lstrip("@")
            url = f"https://instagram.com/{handle}"
        # Use Instagram SVG logo for better appearance
        insta_btn = f'<a href="{url}" target="_blank" rel="noopener noreferrer"><button class="icon" title="Instagram"><span style="font-size:1.2em; vertical-align:middle;">'
        insta_btn += '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" style="vertical-align:middle;"><path fill="#E4405F" d="M12 2.2c3.2 0 3.6 0 4.9.1 1.2.1 2 .2 2.5.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.5.3 1.3.4 2.5.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c-.1 1.2-.2 2-.4 2.5-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.5.2-1.3.3-2.5.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2-.1-2-.2-2.5-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.5-.3-1.3-.4-2.5C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c.1-1.2.2-2 .4-2.5.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.5-.2 1.3-.3 2.5-.4C8.4 2.2 8.8 2.2 12 2.2zm0-2.2C8.7 0 8.3 0 7 .1c-1.3.1-2.2.2-3 .5-.8.3-1.5.7-2.1 1.3-.6.6-1 1.3-1.3 2.1-.3.8-.4 1.7-.5 3C.1 8.3 0 8.7 0 12c0 3.3.1 3.7.1 5 .1 1.3.2 2.2.5 3 .3.8.7 1.5 1.3 2.1.6.6 1.3 1 2.1 1.3.8.3 1.7.4 3 .5 1.3.1 1.7.1 5 .1s3.7-.1 5-.1c1.3-.1 2.2-.2 3-.5.8-.3 1.5-.7 2.1-1.3.6-.6 1-1.3 1.3-2.1.3-.8.4-1.7.5-3 .1-1.3.1-1.7.1-5s0-3.7-.1-5c-.1-1.3-.2-2.2-.5-3-.3-.8-.7-1.5-1.3-2.1-.6-.6-1.3-1-2.1-1.3-.8-.3-1.7-.4-3-.5C15.7.1 15.3 0 12 0z"/><circle fill="#E4405F" cx="12" cy="12" r="3.2"/><circle fill="#E4405F" cx="18.4" cy="5.6" r="1.1"/></svg>'
        insta_btn += '</span></button></a>'
    # Event Link
        event_link = event.get("event_link")
        import logging
        logging.info(f"[UI] render_event_card: event_name={event.get('event_name')}, event_link={event_link}")
        event_link_btn = ""
        if not event_link:
            logging.warning(f"[UI] No event_link for event: {event.get('event_name')}")
        else:
            event_link_btn = f'<a href="{event_link}" target="_blank" rel="noopener noreferrer"><button class="icon" title="Event Link"><span style="font-size:1.2em;">🔗</span></button></a>'
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
    # Only show one button: 'View & Book' with link if present
    + (f'<a href="{event_link}" target="_blank" rel="noopener noreferrer"><button class="primary">View & Book</button></a>' if event_link else '<button class="primary">View & Book</button>')
        + '<div class="event-footer-actions">'
    # Removed star button
    # Removed duplicate button with no link
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
