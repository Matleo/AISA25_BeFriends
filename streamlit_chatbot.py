# --- Intent detection utility ---
import re
def detect_intent(user_input: str) -> str:
    """
    Detects the intent of the user input.
    Returns: 'greeting', 'event_query', 'smalltalk', or 'other'
    """
    user_input = user_input.strip().lower()
    # Robust greeting detection (allow typos, short greetings)
    greetings = ["hi", "hello", "hey", "hallo", "servus", "guten tag", "moin", "grüß dich", "yo"]
    for g in greetings:
        if user_input == g or user_input.startswith(g + " ") or re.fullmatch(rf"{g}[.!?]*", user_input):
            return "greeting"
    # Small talk (simple examples)
    smalltalk_patterns = [
        r"how are you", r"was geht", r"wie geht's", r"alles klar", r"what's up", r"wie läuft's", r"wie geht es dir"
    ]
    for pat in smalltalk_patterns:
        if re.search(pat, user_input):
            return "smalltalk"
    # Event query (use existing logic or keywords)
    event_keywords = [
        "event", "veranstaltung", "konzert", "party", "festival", "happening", "los", "tipps", "wo kann ich", "was kann ich", "wo ist", "wo gibt es", "wo findet", "wo läuft", "wo kann man"
    ]
    for k in event_keywords:
        if k in user_input:
            return "event_query"
    # Fallback to existing event suggestion logic
    if 'is_event_suggestion_request' in globals() and is_event_suggestion_request(user_input):
        return "event_query"
    return "other"
import logging
# Set up logger
logger = logging.getLogger("streamlit_chatbot")
logging.basicConfig(level=logging.DEBUG)

import datetime
import streamlit as st

import json
from pathlib import Path
from components.ui import render_event_recommendations, render_sidebar_filters
from components.chat_ui import (
    render_chat_card_header,
    render_chat_card_container_start,
    render_chat_card_container_end,
    render_spinner,
    render_onboarding_and_quick_replies,
)
from befriends.recommendation.service import RecommendationService
from befriends.catalog.repository import CatalogRepository
from befriends.chatbot_client import ChatbotClient, ChatbotConfig
from befriends.common.config import AppConfig
from befriends.response.formatter import ResponseFormatter
from befriends.response.event_json import events_to_json

# --- Set 'today' for chatbot logic ---
CHATBOT_TODAY = datetime.datetime(2025, 9, 19, 14, 0, 0)

def is_event_suggestion_request(message: str) -> bool:
    keywords = [
        "suggest events", "recommend events", "event suggestions", "show events", "what events", "any events", "find events", "empfehle events", "veranstaltungen", "vorschlagen"
    ]
    message_lower = message.lower()
    return any(kw in message_lower for kw in keywords)

def format_event_recommendations_for_chat(filters, max_events=5, user_query=None):
    logger.debug(f"[DEBUG] format_event_recommendations_for_chat: filters before search: {filters}")
    """Format recommended events for chat using ResponseFormatter. Uses free-text search if user_query is provided."""
    # Always use and update session state filters for consistency
    if "filters" not in st.session_state:
        st.session_state["filters"] = filters or {}
    filters = st.session_state["filters"]
    profile = st.session_state.get("profile", KAROLINA_PROFILE)
    # Ensure date_from is set to today if not already set, to always show upcoming events
    if not filters.get("date_from"):
        filters["date_from"] = CHATBOT_TODAY.date()
    try:
        repo = CatalogRepository()
        recommender = RecommendationService(repo)
        # Only use user_query as free-text if it looks like a keyword/phrase, not a question
        def is_natural_language_question(q):
            if not q:
                return False
            q = q.strip().lower()
            return q.endswith('?') or q.startswith(('what', 'when', 'where', 'who', 'how', 'show', 'any', 'are there', 'is there'))
        search_text = '' if is_natural_language_question(user_query) else user_query
        events = recommender.recommend_events(filters, profile, max_events, today=CHATBOT_TODAY, text=search_text)
        logger.debug(f"[DEBUG] format_event_recommendations_for_chat: events found: {len(events)}")
        # If no events found and city filter is set, relax city filter and try again
        if not events and filters.get("city"):
            filters["city"] = ""
            events = recommender.recommend_events(filters, profile, max_events, today=CHATBOT_TODAY, text=search_text)
            logger.debug(f"[DEBUG] format_event_recommendations_for_chat: events found after relaxing city: {len(events)}")
        formatter = ResponseFormatter()
        lines = ["Here are some recommended events for you:"]
        if events:
            lines.append(formatter.chat_event_list(events))
        else:
            lines.append("(No events found for your query.)")
        return "\n".join(lines)
    except Exception as e:
        return f"(Could not load recommendations: {e})"

def get_event_summaries(filters, profile, limit=10):
    """Get event summaries based on filters and profile."""
    filters = st.session_state.get("filters", filters)
    profile = st.session_state.get("profile", profile)
    try:
        repo = CatalogRepository()
        recommender = RecommendationService(repo)
        events = recommender.recommend_events(filters, profile, limit, today=CHATBOT_TODAY)
        formatter = ResponseFormatter()
        return formatter.chat_event_summary(events)
    except Exception:
        return "(No events available)"
def get_profile_summary(profile):
    return (
        f"Age: {profile['age']}, City: {profile['city']}. "
        f"Interests: {', '.join(profile['interests'])}."
    )
# ...existing code...



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
    config = AppConfig.from_env()
    db_path = config.db_url.replace("sqlite:///", "") if config.db_url.startswith("sqlite:///") else config.db_url
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
    logger.debug(f"[START render_chat_ui] Current session_state.messages: {st.session_state.get('messages')}")
    render_chat_card_container_start()
    # Removed render_chat_card_header() to avoid duplicate heading
    st.markdown("<div class='chat-area-scroll' style='min-height:120px; max-height:340px; overflow-y:auto; margin-bottom:0.4em;'>", unsafe_allow_html=True)

    if st.session_state.messages:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
        if st.session_state.get("chatbot_thinking", False):
            render_spinner()
    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.messages:
        selected_quick = render_onboarding_and_quick_replies()
        logger.debug(f"[UI] No messages yet. Quick reply selected: {selected_quick}")
        if selected_quick:
            logger.info(f"[UI] Appending quick reply to messages: {selected_quick}")
            st.session_state.messages.append({"role": "user", "content": selected_quick})
            logger.debug(f"[UI] Messages after quick reply: {st.session_state.messages}")
            st.rerun()
            st.stop()

    prompt = st.chat_input("Type your message for EventMate…")
    if prompt:
        logger.info(f"[Input] User entered: {prompt}")
        # Append user message immediately on submit, before any backend processing
        if not st.session_state.messages or st.session_state.messages[-1].get("content") != prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            logger.debug(f"[Input] Messages after user input: {st.session_state.messages}")
            st.rerun()
            st.stop()
    # After rerun (e.g. from quick reply), if last message is from user and not yet answered, generate assistant response
    if st.session_state.messages:
        last = st.session_state.messages[-1]
        # Only respond if last message is from user and previous is assistant (or it's the first message)
        if last["role"] == "user" and (len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] == "assistant"):
            user_input = last["content"]
            intent = detect_intent(user_input)
            filters = st.session_state.get("filters", {})
            profile = st.session_state.get("profile", KAROLINA_PROFILE)
            # Respond immediately for greeting/smalltalk
            if intent == "greeting":
                response = "Hey! Schön, von dir zu hören 😊 Wie kann ich dir heute helfen? Suchst du nach Events oder möchtest du einfach plaudern?"
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
                st.stop()
            elif intent == "smalltalk":
                response = "Mir geht's super, danke der Nachfrage! Und wie läuft's bei dir? 😊"
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
                st.stop()
            else:
                # Show spinner before backend call
                if not st.session_state.get("chatbot_thinking", False):
                    st.session_state["chatbot_thinking"] = True
                    st.rerun()
                    st.stop()
                # Now, chatbot_thinking is True, so show spinner and do backend call
                if intent == "event_query" or (len(st.session_state.messages) == 1 and is_event_suggestion_request(user_input)):
                    if not filters.get("date_from"):
                        filters["date_from"] = CHATBOT_TODAY.date()
                    if filters.get("city") and not any(e for e in CatalogRepository().search_text("", filters)):
                        filters["city"] = ""
                    repo = CatalogRepository()
                    recommender = RecommendationService(repo)
                    events = recommender.recommend_events(filters, profile, 10, today=CHATBOT_TODAY)
                    event_json = events_to_json(events, max_events=10)
                    system_prompt = {
                        "role": "system",
                        "content": (
                            "You are <b>EventMate</b>, a warm, approachable, and friendly companion who helps users discover fun events and activities. "
                            + get_profile_summary(profile)
                            + "\nHere is a list of upcoming events as JSON: " + event_json
                        )
                    }
                    messages = [system_prompt] + st.session_state.messages
                    logger.info(f"[Bot] Calling chatbot backend with messages: {messages}")
                    try:
                        response = chatbot_client.get_response(
                            user_id="eventbot-user",
                            messages=messages,
                        )
                    except Exception as e:
                        logger.error(f"[Bot] Error from chatbot backend: {e}")
                        response = f"[Error from chatbot backend: {e}]"
                    st.session_state["chatbot_thinking"] = False
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    logger.debug(f"[Bot] Messages after chatbot backend: {st.session_state.messages}")
                    st.rerun()
                    st.stop()
                else:
                    # For other/unknown intent, use a generic friendly system prompt (no event data)
                    system_prompt = {
                        "role": "system",
                        "content": (
                            "You are <b>EventMate</b>, a warm, approachable, and friendly companion. "
                            + get_profile_summary(profile)
                            + "\nAntworte freundlich und locker auf die Nachricht des Users. Wenn du nicht sicher bist, was gemeint ist, stelle eine Rückfrage."
                        )
                    }
                    messages = [system_prompt] + st.session_state.messages[-2:]  # keep history short
                    logger.info(f"[Bot] Calling chatbot backend (generic intent) with messages: {messages}")
                    try:
                        response = chatbot_client.get_response(
                            user_id="eventbot-user",
                            messages=messages,
                        )
                    except Exception as e:
                        logger.error(f"[Bot] Error from chatbot backend: {e}")
                        response = f"[Error from chatbot backend: {e}]"
                    st.session_state["chatbot_thinking"] = False
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    logger.debug(f"[Bot] Messages after chatbot backend: {st.session_state.messages}")
                    st.rerun()
                    st.stop()
    # else: do nothing if no messages
    render_chat_card_container_end()


def main():
    # --- Chatbot client setup ---
    try:
        config = AppConfig.from_env()
        chatbot_client = ChatbotClient(ChatbotConfig(config))
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
    st.set_page_config(page_title="EventMate", page_icon="�", layout="wide")
    # Load custom CSS from static/eventbot.css
    with open("static/eventbot.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    # Do not render header at the global top; move it into the left column below
    with st.sidebar:
        st.markdown('<div class="harmonized-row2">', unsafe_allow_html=True)
        st.markdown('<div class="harmonized-checkbox2" style="flex:1;">', unsafe_allow_html=True)
        st.session_state.show_debug = st.checkbox("Show debug info", value=st.session_state.show_debug, key="debug_toggle")
        st.markdown('</div><div style="flex:1;display:flex;justify-content:flex-end;">', unsafe_allow_html=True)
        btn_label = "Hide EventBot Filters" if st.session_state.show_sidebar else "Show EventBot Filters"
        if st.button(btn_label, key="toggle_sidebar_main", help=None, use_container_width=False, type="secondary"):
            st.session_state.show_sidebar = not st.session_state.show_sidebar
        st.markdown('</div></div>', unsafe_allow_html=True)

    # EventBot heading removed

    # Header is now loaded from static/header.html

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

    # --- Split main area into two columns: Chatbot (left, wide) | Recommended Events (right, narrow) ---
    col_chat, col_recs = st.columns([1.35, 0.95], gap="large")
    with col_chat:
        # Render header HTML at the top of the chat column
        with open("static/header.html") as f:
            st.markdown(f.read(), unsafe_allow_html=True)
        render_chat_ui(chatbot_client)
    with col_recs:
        st.markdown("<div style='margin-top:1.5em'></div>", unsafe_allow_html=True)
        render_event_recommendations(filters=filters)


# --- Run the app ---
if __name__ == "__main__":
    main()

