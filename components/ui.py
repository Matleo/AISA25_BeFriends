from befriends.recommendation.service import RecommendationService
from befriends.catalog.repository import CatalogRepository
import datetime
import streamlit as st
from typing import Dict, Any, List, Optional, Callable
from befriends.catalog.repository import CatalogRepository
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
    st.markdown("---")
    st.markdown("##### Recommended for you")
    try:
        import json
        formatter = ResponseFormatter()
        # Load user profile (hardcoded fallback for sidebar)
        if filters is None:
            filters = {}
        try:
            with open("karolina_profile.json", "r") as f:
                profile = json.load(f)
        except Exception:
            profile = {"city": "Basel", "interests": []}
        repo = CatalogRepository()
        recommender = RecommendationService(repo)
        filtered_events = recommender.recommend_events(filters, profile, max_events)
        # Wrap in a dummy SearchResult-like object for formatter
        class DummyResult:
            def __init__(self, events):
                self.events = events
                self.total = len(events)
        cards = formatter.to_cards(DummyResult(filtered_events))
        if not cards:
            st.info("No events found for your filters.")
        for i, card in enumerate(cards):
            render_event_card(card, key_prefix=f"rec{i}_")
    except Exception as e:
        st.warning(f"Could not load event recommendations: {e}")
def render_sidebar_filters(default_city: str = "Vienna") -> Dict[str, Any]:
    """
    Render sidebar filter widgets and return a dict of filter values.

    Args:
        default_city (str): Default city to prefill in the city input.

    Returns:
        dict: Dictionary with keys: city, category, date_from, date_to, price_min, price_max, apply_filters
    """
    city = st.sidebar.text_input("City", value=default_city, key="sidebar_city")
    category = st.sidebar.selectbox("Category", ["", "Music", "Sports", "Food & Drink", "Theater", "Comedy", "Family", "Outdoors", "Workshops", "Other"], key="sidebar_category")
    date_from = st.sidebar.date_input("From date", value=None, key="sidebar_date_from")
    date_to = st.sidebar.date_input("To date", value=None, key="sidebar_date_to")
    price_min = st.sidebar.number_input("Min price", min_value=0.0, value=0.0, step=1.0, key="sidebar_price_min")
    price_max = st.sidebar.number_input("Max price", min_value=0.0, value=0.0, step=1.0, key="sidebar_price_max")
    apply_filters = st.sidebar.button("Apply Filters", key="sidebar_apply_filters")
    return {
        "city": city,
        "category": category,
        "date_from": date_from,
        "date_to": date_to,
        "price_min": price_min,
        "price_max": price_max,
        "apply_filters": apply_filters,
    }


def render_event_card(event: Dict[str, Any], key_prefix: str = "") -> None:
    """
    Render a single event as a rich card.

    Args:
        event (Dict[str, Any]): Event data to render.
        key_prefix (str, optional): Prefix for Streamlit widget keys to avoid collisions.
    """
    # Fallback emoji by category
    emoji_map = {
        "Music": "🎶", "Sports": "🏅", "Food & Drink": "🍽️", "Theater": "🎭", "Comedy": "😂",
        "Family": "👨‍👩‍👧", "Outdoors": "🌳", "Workshops": "🛠️", "Other": "🎫"
    }
    category = event.get("category", "Other")
    emoji = emoji_map.get(category, "🎫")
    thumbnail = event.get("image") or emoji
    title = event.get("title", "Event")
    date = event.get("date", "")
    venue = event.get("venue", "")
    distance = event.get("distance_km")
    price = event.get("price", "")
    price_label = "Free" if price == 0 else f"{price}"
    category_pill = f'<span class="pill category {category.lower()}">{category}</span>'
    price_pill = f'<span class="pill price">{price_label}</span>'
    dist_badge = f'<span class="distance-badge">{distance:.1f} km</span>' if distance else ""
    description = event.get("description") or event.get("short_description") or "No description available."
    instagram = event.get("instagram")
    insta_btn = ""
    if instagram:
        handle = instagram.lstrip("@")
        url = f"https://instagram.com/{handle}"
        insta_btn = f'<a href="{url}" target="_blank" rel="noopener noreferrer"><button class="icon" title="Instagram"><span style="font-size:1.2em;">📸</span></button></a>'
    try:
        st.markdown(f"""
        <div class="event-card">
            <div class="event-thumb">{thumbnail}</div>
            <div class="event-main">
                <div class="event-title"><b>{title}</b></div>
                <div class="event-meta">{date} • {venue} {dist_badge}</div>
                <div class="event-desc" style="color:#444;font-size:0.98em;margin-bottom:0.4em;">{description}</div>
                <div class="event-pills">{category_pill} {price_pill}</div>
            </div>
            <div class="event-footer">
                <button class="primary">View & Book</button>
                <button class="icon">★</button>
                <button class="icon">🔗</button>
                {insta_btn}
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not render event card: {e}")
    # Remove any accidental print or st.write of '</div>' after this line
    # Ensure there is no stray </div> after this line

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
    <style>
    .event-card {background: var(--secondary-background-color,#f7f8fa); border-radius: 18px; box-shadow: 0 2px 8px #0001; padding: 1rem; margin-bottom: 1rem; display: flex; flex-direction: column; transition: box-shadow .2s;}
    .event-card:hover {box-shadow: 0 4px 16px #0002; transform: translateY(-2px);}
    .event-thumb {font-size: 2.2rem; margin-bottom: 0.5rem;}
    .event-title {font-size: 1.1rem; margin-bottom: 0.2rem;}
    .event-meta {color: #555; font-size: 0.95rem; margin-bottom: 0.3rem;}
    .event-pills {margin-bottom: 0.5rem;}
    .pill {display: inline-block; border-radius: 999px; padding: 0.2em 0.8em; font-size: 0.85em; margin-right: 0.3em; background: #e0f7fa; color: #00796b;}
    .pill.price {background: #e3e3e3; color: #222;}
    .pill.category.music {background: #e0f7fa; color: #00796b;}
    .pill.category.sports {background: #fff3e0; color: #ef6c00;}
    .pill.category.food\ \&\ drink {background: #fce4ec; color: #ad1457;}
    .pill.category.theater {background: #ede7f6; color: #5e35b1;}
    .pill.category.comedy {background: #fffde7; color: #fbc02d;}
    .pill.category.family {background: #e8f5e9; color: #388e3c;}
    .pill.category.outdoors {background: #e0f2f1; color: #00695c;}
    .pill.category.workshops {background: #f3e5f5; color: #8e24aa;}
    .distance-badge {background: #e0e0e0; color: #333; border-radius: 8px; padding: 0.1em 0.5em; font-size: 0.8em; margin-left: 0.5em;}
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
