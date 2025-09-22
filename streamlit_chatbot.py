import re
import logging
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
class ChatbotService:
    def __init__(self, chatbot_client, profile):
        self.chatbot_client = chatbot_client
        self.profile = profile

    @staticmethod
    def detect_intent(user_input: str) -> str:
        user_input = user_input.strip().lower()
        greetings = ["hi", "hello", "hey", "hallo", "servus", "guten tag", "moin", "grüß dich", "yo"]
        for g in greetings:
            if user_input == g or user_input.startswith(g + " ") or re.fullmatch(rf"{g}[.!?]*", user_input):
                return "greeting"
        smalltalk_patterns = [
            r"how are you", r"was geht", r"wie geht's", r"alles klar", r"what's up", r"wie läuft's", r"wie geht es dir"
        ]
        for pat in smalltalk_patterns:
            if re.search(pat, user_input):
                return "smalltalk"
        event_keywords = [
            "event", "veranstaltung", "konzert", "party", "festival", "happening", "los", "tipps", "wo kann ich", "was kann ich", "wo ist", "wo gibt es", "wo findet", "wo läuft", "wo kann man"
        ]
        for k in event_keywords:
            if k in user_input:
                return "event_query"
        if 'is_event_suggestion_request' in globals() and is_event_suggestion_request(user_input):
            return "event_query"
        return "other"

    def get_response(self, user_input, messages, filters, intent, today, repo, recommender, events_to_json, get_profile_summary):
        # Respond immediately for greeting/smalltalk
        if intent == "greeting":
            return "Hey! Schön, von dir zu hören 😊 Wie kann ich dir heute helfen? Suchst du nach Events oder möchtest du einfach plaudern?"
        elif intent == "smalltalk":
            return "Mir geht's super, danke der Nachfrage! Und wie läuft's bei dir? 😊"
        # Event query or fallback
        if intent == "event_query" or (len(messages) == 1 and is_event_suggestion_request(user_input)):
            if not filters.get("date_from"):
                filters["date_from"] = today.date()
            if filters.get("city") and not any(e for e in repo.search_text("", filters)):
                filters["city"] = ""
            events = recommender.recommend_events(filters, self.profile, 10, today=today)
            event_json = events_to_json(events, max_events=10)
            system_prompt = {
                "role": "system",
                "content": (
                    "You are <b>EventMate</b>, a warm, approachable, and friendly companion who helps users discover fun events and activities. "
                    + get_profile_summary(self.profile)
                    + "\nHere is a list of upcoming events as JSON: " + event_json
                )
            }
            full_messages = [system_prompt] + messages
            try:
                response = self.chatbot_client.get_response(
                    user_id="eventbot-user",
                    messages=full_messages,
                )
            except Exception as e:
                response = f"[Error from chatbot backend: {e}]"
            return response
        # Other/unknown intent
        system_prompt = {
            "role": "system",
            "content": (
                "You are <b>EventMate</b>, a warm, approachable, and friendly companion. "
                + get_profile_summary(self.profile)
                + "\nAntworte freundlich und locker auf die Nachricht des Users. Wenn du nicht sicher bist, was gemeint ist, stelle eine Rückfrage."
            )
        }
        short_history = messages[-2:] if len(messages) > 1 else messages
        full_messages = [system_prompt] + short_history
        try:
            response = self.chatbot_client.get_response(
                user_id="eventbot-user",
                messages=full_messages,
            )
        except Exception as e:
            response = f"[Error from chatbot backend: {e}]"

# Set up logger
logger = logging.getLogger("streamlit_chatbot")
logging.basicConfig(level=logging.DEBUG)

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

# Setup general logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
# ...existing code...




# --- Profile management ---
class ProfileManager:
    DEFAULT_PROFILE = {
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

    @staticmethod
    def load_profile(profile_path: str = "karolina_profile.json") -> dict:
        profile_file = Path(profile_path)
        try:
            if profile_file.exists():
                with open(profile_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            st.warning(f"Profile file {profile_path} not found. Using fallback profile.")
        except Exception as e:
            st.warning(f"Could not load profile: {e}. Using fallback profile.")
        return ProfileManager.DEFAULT_PROFILE.copy()

    @staticmethod
    def ensure_profile_in_session():
        if "profile" not in st.session_state:
            st.session_state["profile"] = ProfileManager.load_profile()
        return st.session_state["profile"]

KAROLINA_PROFILE = ProfileManager.ensure_profile_in_session()

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
    # Only render chat history and input UI. No state mutation or message processing here.
    st.markdown("""
    <div style='margin-top:2.5em;'>
        <h2 style='margin-bottom:0.2em; color:#1976d2; font-weight:800; letter-spacing:-1px;'>EventMate</h2>
        <div style='font-size:1.1em; color:#444; margin-bottom:0.7em;'>Your friendly companion for discovering fun things to do</div>
    </div>
    """, unsafe_allow_html=True)
    render_chat_card_container_start()
    # Render chat history
    def get_avatar(role):
        return "🧑" if role == "user" else "🤖"
    def get_label(role):
        return "You" if role == "user" else "EventMate"
    def get_time():
        return datetime.datetime.now().strftime("%H:%M")

    st.markdown("""
    <div class="chat-history-scrollable">
    """, unsafe_allow_html=True)
    prev_role = None
    import re
    def strip_html(text):
        # Remove all HTML tags
        return re.sub(r'<[^>]+>', '', text)
    for i, msg in enumerate(st.session_state["messages"]):
        role = msg["role"]
        show_label = (i == 0) or (role != prev_role)
        avatar_html = f'<div class="avatar">{get_avatar(role)}</div>' if show_label else ''
        label_html = f'<div class="sender-label">{get_label(role)}</div>' if show_label else ''
        # Only strip HTML for assistant messages
        content = msg['content']
        if role == "assistant":
            content = strip_html(content)
        bubble = f"""
<div class='chat-row {role}'>
    {avatar_html}
    <div class='bubble-group'>
        {label_html}
        <div class='chat-bubble {role}'>{content}</div>
        <div class='timestamp'>{get_time()}</div>
    </div>
</div>
        """
        st.markdown(bubble, unsafe_allow_html=True)
        prev_role = role

    if st.session_state.get("is_typing"):
        from components.chat_ui import render_spinner
        render_spinner()
    st.markdown("</div>", unsafe_allow_html=True)
    # Inject enhanced CSS for chat layout
    st.markdown("""
    <style>
    .chat-history-scrollable {
        max-height: 420px;
        overflow-y: auto;
        padding-bottom: 1em;
        margin-bottom: 0.5em;
        background: #f7f8fa;
        border-radius: 16px;
        border: 1px solid #e3e6ee;
    }
    .chat-row {
        display: flex;
        align-items: flex-end;
        margin-bottom: 0.2em;
    }
    .chat-row.user { flex-direction: row-reverse; }
    .chat-row .avatar {
        font-size: 1.7em;
        margin: 0 0.5em;
        align-self: flex-end;
    }
    .bubble-group {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        max-width: 80%;
    }
    .chat-row.user .bubble-group { align-items: flex-end; }
    .sender-label {
        font-size: 0.9em;
        color: #1976d2;
        font-weight: 600;
        margin-bottom: 0.1em;
    }
    .chat-bubble {
        padding: 0.7em 1.2em;
        border-radius: 18px;
        margin-bottom: 0.1em;
        font-size: 1.08em;
        box-shadow: 0 1px 4px #0001;
        word-break: break-word;
    }
    .chat-bubble.user {
        background: #e3f2fd;
        color: #1976d2;
        border-bottom-right-radius: 6px;
    }
    .chat-bubble.assistant {
        background: #fff;
        color: #222;
        border-bottom-left-radius: 6px;
    }
    .timestamp {
        font-size: 0.75em;
        color: #b0b0b0;
        margin-top: -0.2em;
        margin-bottom: 0.2em;
        margin-left: 0.2em;
    }
    </style>
    """, unsafe_allow_html=True)
    # --- Chat input area ---
    # Show quick reply buttons if only the welcome message is present
    if (
        len(st.session_state["messages"]) == 1
        and st.session_state["messages"][0]["role"] == "assistant"
    ):
        st.markdown("<div style='margin-top:1.5em;'></div>", unsafe_allow_html=True)
        quick_replies = [
            "What's happening this weekend?",
            "Concerts nearby",
            "Dance socials",
            "Dog-friendly events",
            "Outdoor activities this weekend",
        ]
        cols = st.columns(len(quick_replies))
        for i, label in enumerate(quick_replies):
            if cols[i].button(label, key=f"quickreply_{i}"):
                # Only append plain text to chat history
                st.session_state["messages"].append({"role": "user", "content": str(label)})
                st.session_state["chat_input"] = str(label)
                st.rerun()

    # Standard Streamlit chat input
    st.markdown("<div style='margin-top:1.5em;'></div>", unsafe_allow_html=True)
    user_input = st.text_input("Type your message...", value="", key="chat_input_box")
    send = st.button("Send", key="send_button")
    if send and user_input.strip():
        # Only append plain text to chat history
        st.session_state["messages"].append({"role": "user", "content": user_input.strip()})
        st.session_state["chat_input"] = user_input.strip()
        st.rerun()
    render_chat_card_container_end()

# --- Main app entrypoint ---
def main():
    # --- Session state initialization ---
    logger.info("[MAIN] Starting main()")
    logger.debug(f"[DEBUG] Initial session state: {st.session_state}")
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False
    if "show_sidebar" not in st.session_state:
        st.session_state.show_sidebar = False
    if "filters" not in st.session_state or not st.session_state.filters:
        st.session_state.filters = get_default_filters()
    if "apply_filters" not in st.session_state.filters or not st.session_state.filters["apply_filters"]:
        st.session_state.filters["apply_filters"] = True
    # --- Onboarding/welcome message logic ---
    welcome_msg = "👋 Hi! I'm <b>EventMate</b>, your friendly companion for discovering fun things to do. Your preferences are set up and used only for recommendations. Looking for something fun this weekend? Just ask or see my recommendations below!"
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state["messages"] = [{"role": "assistant", "content": welcome_msg}]
    elif st.session_state["messages"][0].get("content") != welcome_msg:
        st.session_state["messages"].insert(0, {"role": "assistant", "content": welcome_msg})

    # --- AppConfig and ChatbotClient setup ---
    try:
        config = AppConfig.from_env()
        chatbot_client = ChatbotClient(ChatbotConfig(config))
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {e}")
        logger.error(f"[MAIN] Failed to initialize chatbot: {e}")
        return

    # --- Layout ---
    st.set_page_config(page_title="EventMate", page_icon="💬", layout="wide")
    # --- Robust error handling for custom CSS ---
    try:
        with open("static/eventbot.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load custom CSS: {e}")

    # Sidebar for filters and debug
    with st.sidebar:
        st.markdown("## EventBot Filters")
        filters = render_sidebar_filters(default_city=get_default_city())
        st.session_state.filters.update(filters)
        if st.session_state.show_debug:
            st.markdown("---")
            st.markdown("### Debug Info")
            st.write({
                "messages": st.session_state.get("messages"),
                "filters": st.session_state.get("filters"),
                "show_sidebar": st.session_state.get("show_sidebar"),
            })

    # Main layout: chat and recommendations
    col_chat, col_recs = st.columns([1.35, 0.95], gap="large")
    with col_chat:
        logger.debug("[DEBUG] Rendering chat UI")

        # --- Chat message handling logic ---
        # If user has submitted a message (via custom input or quick reply)
        user_input = st.session_state.get("chat_input", "").strip()
        if user_input:
            # Append user message
            st.session_state["messages"].append({"role": "user", "content": user_input})
            # Set typing indicator
            st.session_state["is_typing"] = True
            # Clear input
            st.session_state["chat_input"] = ""
            st.rerun()

        # If is_typing, show spinner and get bot response
        if st.session_state.get("is_typing"):
            render_chat_ui(chatbot_client)  # Show spinner
            # Generate assistant response
            chatbot_service = ChatbotService(chatbot_client, st.session_state["profile"])
            last_user_message = st.session_state["messages"][-1]["content"]
            intent = chatbot_service.detect_intent(last_user_message)
            response = chatbot_service.get_response(
                last_user_message,
                st.session_state["messages"],
                st.session_state["filters"],
                intent,
                CHATBOT_TODAY,
                CatalogRepository(),
                RecommendationService(CatalogRepository()),
                events_to_json,
                get_profile_summary,
            )
            st.session_state["messages"].append({"role": "assistant", "content": response})
            st.session_state["is_typing"] = False
            st.rerun()

        # Otherwise, just render the chat UI
        render_chat_ui(chatbot_client)

    with col_recs:
        logger.debug(f"[DEBUG] Rendering recommendations with filters: {st.session_state.filters}")
        from components.recommendation_panel import RecommendationPanel
        RecommendationPanel.render(filters=st.session_state.filters)
    logger.info("[MAIN] Finished main()")

# Call main only after its definition
if __name__ == "__main__":
    main()




