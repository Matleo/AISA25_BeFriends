from components.ui import render_event_recommendations, get_best_recommended_events
def is_event_suggestion_request(message: str) -> bool:
    keywords = [
        "suggest events", "recommend events", "event suggestions", "show events", "what events", "any events", "find events", "empfehle events", "veranstaltungen", "vorschlagen"
    ]
    message_lower = message.lower()
    return any(kw in message_lower for kw in keywords)



def format_event_recommendations_for_chat(filters, max_events=5):
    # Always use the latest filters and profile from session state for consistency
    filters = st.session_state.get("filters", filters)
    profile = st.session_state.get("profile", KAROLINA_PROFILE)
    try:
        events = get_best_recommended_events(filters, profile, max_events)
    except Exception as e:
        return f"(Could not load recommendations: {e})"
    lines = ["Here are some recommended events for you:"]
    for i, event in enumerate(events, 1):
        lines.append(f"{i}. {event.name} ({event.date}, {event.city or 'n/a'}, {event.category or 'n/a'})")
        if event.description:
            lines.append(f"   - {event.description[:120]}{'...' if len(event.description) > 120 else ''}")
    return "\n".join(lines)
def get_event_summaries(filters, profile, limit=10):
    # Always use the latest filters and profile from session state for consistency
    filters = st.session_state.get("filters", filters)
    profile = st.session_state.get("profile", profile)
    try:
        events = get_best_recommended_events(filters, profile, limit)
    except Exception:
        return "(No events available)"
    if not events:
        return "(No events available)"
    lines = []
    for e in events:
        line = f"- {e.name} ({e.date}, {e.city or 'n/a'}, {e.category or 'n/a'})"
        lines.append(line)
    return "Upcoming events include:\n" + "\n".join(lines)
def get_profile_summary(profile):
    return (
        f"Age: {profile['age']}, City: {profile['city']}. "
        f"Interests: {', '.join(profile['interests'])}."
    )
# ...existing code...


import streamlit as st
import datetime
import json
from pathlib import Path
from components.ui import (
    render_event_card,
    render_chips,
    inject_styles,
    render_sidebar_filters,
    render_event_recommendations,
)
from befriends.chatbot_client import ChatbotClient, ChatbotConfig

# --- Karolina's profile ---
def load_profile(profile_path: str = "karolina_profile.json") -> dict:
    """Load user profile from JSON file, or return fallback profile if not found."""
    profile_file = Path(profile_path)
    if profile_file.exists():
        with open(profile_file, "r", encoding="utf-8") as f:
            return json.load(f)
    st.warning(f"Profile file {profile_path} not found. Using fallback profile.")
    return {
        "name": "Karolina",
        "age": 33,
        "city": "Basel",
        "address": "Dornacherstr.",
        "interests": [
            "dance (zouk, salsa)",
            "water sports",
            "swimming in the Rhine",
            "being around water",
            "music (guitar, ukulele)",
            "concerts",
            "festivals",
            "jam sessions",
            "dogs",
            "kids",
            "fun social activities",
            "outdoor activities",
            "dog-friendly gatherings",
            "cultural festivals"
        ]
    }

KAROLINA_PROFILE = load_profile()
# Store profile in session state for consistency and possible future editing
if "profile" not in st.session_state:
    st.session_state["profile"] = KAROLINA_PROFILE

def get_onboarding_message() -> str:
    """Return the onboarding message for new users."""
    return (
        "👋 Hi! I'm EventBot. Your preferences are set up and used only for recommendations. "
        "Looking for something fun this weekend? Just ask or see my recommendations below!"
    )

def get_default_city() -> str:
    """Get the default city from the user profile."""
    return KAROLINA_PROFILE["city"]

def get_default_filters() -> dict:
    """Return default filter values for event recommendations."""
    # Less restrictive: no date or price filter by default
    # Data-aware: if no cities in DB, set city filter to empty
    import sqlite3
    db_path = "events.db"
    city_value = KAROLINA_PROFILE["city"]
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM events WHERE city IS NOT NULL AND city != "";')
            city_count = cur.fetchone()[0]
            if city_count == 0:
                city_value = ""
    except Exception:
        city_value = ""
    return {
        "city": city_value,
        "category": "",
        "date_from": None,
        "date_to": None,
        "price_min": None,
        "price_max": None,
        "apply_filters": True,
    }

def get_interest_keywords() -> list:
    """Return keywords for filtering or boosting recommendations."""
    return [
        "dance", "zouk", "salsa", "water", "swimming", "Rhine", "music", "guitar", "ukulele",
        "concert", "festival", "jam", "dog", "kids", "outdoor", "social", "dog-friendly", "cultural"
    ]


# --- Chat UI logic extracted for clarity ---
def render_chat_ui(chatbot_client):
    st.markdown("""
    <div class='chat-card' style='margin-top:2.5em; margin-bottom:2.5em; box-shadow:0 4px 24px #0001; border-radius:18px; background:#fff; padding:2.2em 2.5em 1.5em 2.5em; border:2.5px solid #d1e3f8;'>
      <div style='display:flex; align-items:center; gap:1em; margin-bottom:0.5em;'>
        <span style='font-size:2.1rem; font-weight:700;'>💬 Chat with EventBot</span>
        <div style='flex:1;'></div>
        <button onclick="window.location.reload()" style='background:none; border:none; cursor:pointer; font-size:1.3em; margin-left:auto;' title='Clear Conversation'>🗑️</button>
      </div>
    """, unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        st.markdown("<div class='chat-area-scroll' style='min-height:120px; max-height:340px; overflow-y:auto; margin-bottom:1.2em;'>", unsafe_allow_html=True)
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
        st.markdown("</div>", unsafe_allow_html=True)
    prompt = st.chat_input("Type your message…")
    if prompt:
        # Show user message immediately in chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Always use current filters and profile
        filters = st.session_state.get("filters", {})
        profile = st.session_state.get("profile", KAROLINA_PROFILE)
        # If user asks for event suggestions, bypass LLM and use backend recommendations
        if is_event_suggestion_request(prompt):
            response = format_event_recommendations_for_chat(filters)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        # Otherwise, use the LLM as before
        event_summaries = get_event_summaries(filters, profile, limit=10)
        system_prompt = {
            "role": "system",
            "content": (
                "You are EventBot, a helpful event assistant. "
                + get_profile_summary(profile)
                + "\n" + event_summaries
            )
        }
        messages = [system_prompt] + st.session_state.messages
        try:
            response = chatbot_client.get_response(
                user_id="eventbot-user",
                messages=messages,
            )
        except Exception as e:
            response = f"[Error from chatbot backend: {e}]"
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    # Do not rerun after every message append; only after user input
    selected_quick = None
    if not st.session_state.messages:
        quick_replies = [
            {"label": "What's happening this weekend?", "value": "What's happening this weekend?"},
            {"label": "Concerts nearby", "value": "Show me concerts nearby"},
            {"label": "Dance socials", "value": "Any dance socials?"},
            {"label": "Dog-friendly events", "value": "Dog-friendly events"},
            {"label": "Outdoor activities", "value": "Outdoor activities this weekend"},
        ]
        st.markdown("<div class='quick-reply-row' style='margin-top:1.2em;'>", unsafe_allow_html=True)
        cols = st.columns(len(quick_replies))
        for i, chip in enumerate(quick_replies):
            if cols[i].button(chip["label"], key=f"quickreply_{i}", help=chip["value"], use_container_width=True):
                selected_quick = chip["value"]
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if selected_quick:
        st.session_state.messages.append({"role": "user", "content": selected_quick})
        filters = st.session_state.get("filters", {})
        profile = st.session_state.get("profile", KAROLINA_PROFILE)
        if is_event_suggestion_request(selected_quick):
            response = format_event_recommendations_for_chat(filters)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        event_summaries = get_event_summaries(filters, profile, limit=10)
        system_prompt = {
            "role": "system",
            "content": (
                "You are EventBot, a helpful event assistant. "
                + get_profile_summary(profile)
                + "\n" + event_summaries
            )
        }
        messages = [system_prompt] + st.session_state.messages
        try:
            response = chatbot_client.get_response(
                user_id="eventbot-user",
                messages=messages,
            )
        except Exception as e:
            response = f"[Error from chatbot backend: {e}]"
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


def main():
    # --- Chatbot client setup ---
    try:
        chatbot_client = ChatbotClient(ChatbotConfig())
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {e}")
        return
    # --- Session state initialization ---
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_sidebar" not in st.session_state:
        st.session_state.show_sidebar = False
    if "filters" not in st.session_state or not st.session_state.filters:
        st.session_state.filters = get_default_filters()
    # Always ensure apply_filters is True on first load to trigger recommendations
    if "apply_filters" not in st.session_state.filters or not st.session_state.filters["apply_filters"]:
        st.session_state.filters["apply_filters"] = True

    # --- UI setup ---
    st.set_page_config(page_title="EventBot", page_icon="🤖", layout="wide")
    with open("static/eventbot.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown('<div class="harmonized-row2">', unsafe_allow_html=True)
        st.markdown('<div class="harmonized-checkbox2" style="flex:1;">', unsafe_allow_html=True)
        st.session_state.show_debug = st.checkbox("Show debug info", value=st.session_state.show_debug, key="debug_toggle")
        st.markdown('</div><div style="flex:1;display:flex;justify-content:flex-end;">', unsafe_allow_html=True)
        btn_label = "Hide EventBot Filters" if st.session_state.show_sidebar else "Show EventBot Filters"
        if st.button(btn_label, key="toggle_sidebar_main", help=None, use_container_width=False, type="secondary"):
            st.session_state.show_sidebar = not st.session_state.show_sidebar
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style='display: flex; align-items: center; gap: 1.2em; margin-bottom: 0.2em;'>
        <span style='font-size:2.5rem; font-weight:800; letter-spacing:-2px;'>🤖 EventBot</span>
        <span style='color:#1976d2; background:#e3f2fd; border-radius:999px; padding:0.3em 1.1em; font-size:1.1em; font-weight:600; margin-left:0.5em;'>your local events concierge</span>
    </div>
    """, unsafe_allow_html=True)

    # Onboarding message (top, only if no chat yet)
    if not st.session_state.messages:
        st.info(get_onboarding_message())

    # Filters logic
    if st.session_state.show_sidebar:
        with st.sidebar:
            st.markdown("## EventBot Filters")
            # Removed blue info box
            filters = render_sidebar_filters(default_city=get_default_city())
            st.session_state.filters.update(filters)
    filters = st.session_state.filters

    # Debug info in sidebar
    if st.session_state.show_debug:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### Debug Info")
            st.write({
                "messages": st.session_state.get("messages"),
                "filters": st.session_state.get("filters"),
                "show_sidebar": st.session_state.get("show_sidebar"),
            })

    # --- Split main area into two columns: Chat (left, wide) | Recommendations (right, narrow) ---
    col_chat, col_recs = st.columns([1.35, 0.95], gap="large")
    with col_chat:
        render_chat_ui(chatbot_client)
    with col_recs:
        st.markdown("<div style='margin-top:1.5em'></div>", unsafe_allow_html=True)
        render_event_recommendations(filters=filters)


# --- Run the app ---
if __name__ == "__main__":
    main()

