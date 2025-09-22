import logging
import datetime
import streamlit as st
import logging

# Setup general logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("streamlit_chatbot")

CHATBOT_TODAY = datetime.datetime(2025, 9, 19, 14, 0, 0)
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
from components.profile_manager import ProfileManager
from components.chat_ui import render_chat_bubble
from components.chatbot_service import ChatbotService
import re
import html
import json
from pathlib import Path
import uuid

# Asset file path constants
CHAT_HEADER_PATH = "assets/chat_header.html"
CHAT_HISTORY_CONTAINER_PATH = "assets/chat_history_container.html"
CHAT_STYLES_PATH = "assets/chat_styles.css"



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

    @staticmethod
    def get_interest_keywords() -> list:
        """Return keywords for filtering or boosting recommendations."""
        return [
            "dance", "zouk", "salsa", "water", "swimming", "Rhine", "music", "guitar", "ukulele",
            "concert", "festival", "jam", "dog", "kids", "outdoor", "social", "dog-friendly", "cultural"
        ]

# Patch: ensure ProfileManager is reloaded and get_default_filters is available
import importlib
import components.profile_manager
importlib.reload(components.profile_manager)
ProfileManager = components.profile_manager.ProfileManager


# --- Chat UI logic extracted for clarity ---
def render_chat_ui(chatbot_client):
    # Only render chat history and input UI. No state mutation or message processing here.
    try:
        with open(CHAT_HEADER_PATH) as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    except Exception:
        st.warning("Could not load chat header asset.")
    render_chat_card_container_start()
    # Render chat history
    try:
        with open(CHAT_HISTORY_CONTAINER_PATH) as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    except Exception:
        st.warning("Could not load chat history container asset.")
    prev_role = None
    for i, msg in enumerate(st.session_state["messages"]):
        role = msg["role"]
        show_label = (i == 0) or (role != prev_role)
        content = msg['content']
        timestamp = msg.get('timestamp', "")
        bubble = render_chat_bubble(role, content, timestamp, show_label)
        st.markdown(bubble, unsafe_allow_html=True)
        prev_role = role
    if st.session_state.get("is_typing"):
        from components.chat_ui import render_spinner
        render_spinner()
    st.markdown("</div>", unsafe_allow_html=True)
    # Inject enhanced CSS for chat layout
    try:
        with open(CHAT_STYLES_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        st.warning("Could not load chat styles asset.")
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
                st.session_state["pending_user_message"] = label
                st.rerun()

    # Standard Streamlit chat input
    st.markdown("<div style='margin-top:1.5em;'></div>", unsafe_allow_html=True)
    user_input = st.text_input("Type your message...", value="", key="chat_input_box")
    send = st.button("Send", key="send_button")
    if send and user_input.strip():
        st.session_state["pending_user_message"] = user_input.strip()
        st.rerun()
    render_chat_card_container_end()

def append_message(role, content):
    import datetime
    now_str = datetime.datetime.now().strftime("%H:%M")
    st.session_state["messages"].append({"role": role, "content": content, "timestamp": now_str})

# --- Main app entrypoint ---
def main():
    # --- Ensure all state machine keys are always present ---
    st.session_state.setdefault("pending_user_message", None)
    st.session_state.setdefault("is_typing", False)
    st.session_state.setdefault("spinner_shown", False)
    st.session_state.setdefault("chatbot_error", None)
    # --- Session state initialization ---
    logger.info("[MAIN] Starting main()")
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False
    if "show_sidebar" not in st.session_state:
        st.session_state.show_sidebar = False
    if "filters" not in st.session_state or not st.session_state.filters:
        st.session_state.filters = ProfileManager.get_default_filters()
    if "apply_filters" not in st.session_state.filters or not st.session_state.filters["apply_filters"]:
        st.session_state.filters["apply_filters"] = True
    # --- Onboarding/welcome message logic ---
    welcome_msg = "👋 Hi! I'm <b>EventMate</b>, your friendly companion for discovering fun things to do. Your preferences are set up and used only for recommendations. Looking for something fun this weekend? Just ask or see my recommendations below!"
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state["messages"] = []
        append_message("assistant", welcome_msg)
    elif st.session_state["messages"][0].get("content") != welcome_msg:
        st.session_state["messages"].insert(0, {"role": "assistant", "content": welcome_msg, "timestamp": datetime.datetime.now().strftime("%H:%M")})

    # --- AppConfig and ChatbotClient setup ---
    try:
        config = AppConfig.from_env()
        chatbot_client = ChatbotClient(ChatbotConfig(config))
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {e}. Please check your configuration and try again.")
        logger.error(f"[MAIN] Failed to initialize chatbot: {e}")
        return

    # --- Layout ---
    st.set_page_config(page_title="EventMate", page_icon="💬", layout="wide")
    # --- Robust error handling for custom CSS ---
    try:
        with open("static/eventbot.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load custom CSS: {e}. The chat UI may look less polished.")

    # Sidebar for filters and debug
    with st.sidebar:
        st.markdown("## EventBot Filters")
        try:
            sidebar_filters = render_sidebar_filters(default_city=ProfileManager.get_default_city())
        except Exception as e:
            st.error(f"Failed to load sidebar filters: {e}")
            sidebar_filters = {}
        # Only update st.session_state['filters'] if Apply or Reset is pressed
        if sidebar_filters.get("apply_filters"):
            st.session_state["filters"].update({
                k: v for k, v in sidebar_filters.items() if k not in ("apply_filters", "reset_filters")
            })
        elif sidebar_filters.get("reset_filters"):
            st.session_state["filters"] = {
                "city": "",
                "category": "",
                "date_from": None,
                "date_to": None,
                "price_min": 0.0,
                "price_max": 0.0,
                "apply_filters": False,
            }
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
        # --- LOG STATE ---
    # logger.debug(f"[STATE] pending_user_message={st.session_state.get('pending_user_message')}, is_typing={st.session_state.get('is_typing')}, spinner_shown={st.session_state.get('spinner_shown')}, messages={len(st.session_state.get('messages', []))}")
        # Robust state machine for chat interaction
        pending_user_message = st.session_state.get("pending_user_message", None)
        is_typing = st.session_state.get("is_typing", False)
        spinner_shown = st.session_state.get("spinner_shown", False)
        error_message = st.session_state.get("chatbot_error", None)

        # Step 1: If there's a pending user message, append it and start typing
        if pending_user_message and not is_typing:
            logger.info(f"[USER] Appending message: {pending_user_message}")
            safe_input = html.escape(pending_user_message)
            append_message("user", safe_input)
            st.session_state["is_typing"] = True
            st.session_state["pending_user_message"] = None
            st.session_state["spinner_shown"] = False
            st.session_state["chatbot_error"] = None
            st.rerun()

        # Step 2: If is_typing and spinner not shown, show spinner
        if st.session_state.get("is_typing", False) and not st.session_state.get("spinner_shown", False):
            # Spinner state, not needed in logs
            st.session_state["spinner_shown"] = True
            render_chat_ui(chatbot_client)
            from components.chat_ui import render_spinner
            render_spinner()
            st.rerun()

        # Step 3: If is_typing and spinner was shown, generate assistant response
        if st.session_state.get("is_typing", False) and st.session_state.get("spinner_shown", False):
            logger.info("[ASSISTANT] Generating response...")
            try:
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
                logger.info(f"[TRACE] (Before error check) Assistant response type: {type(response)}, value: {repr(response)}")
                # Fallback: if response is a dict with 'content', extract it
                if isinstance(response, dict) and "content" in response:
                    response = response["content"]
                # Robust: treat empty or whitespace-only string as invalid
                if not response or not isinstance(response, str) or not response.strip():
                    error_id = str(uuid.uuid4())
                    logger.error(f"[ERROR {error_id}] Empty or invalid assistant response. Response: {repr(response)}, Type: {type(response)}, Messages: {st.session_state['messages']}")
                    raise ValueError(f"Empty or invalid assistant response (error_id={error_id})")
                st.session_state["chatbot_error"] = None
            except Exception as e:
                response = f"[System error: {e}]"
                st.session_state["chatbot_error"] = str(e)
                logger.error(f"[ASSISTANT] Error: {e}")
            logger.info(f"[TRACE] (After error check, before append) Assistant response type: {type(response)}, value: {repr(response)}")
            append_message("assistant", response)
            logger.info(f"[TRACE] (After append) st.session_state['messages']: {st.session_state['messages']}")
            st.session_state["is_typing"] = False
            st.session_state["spinner_shown"] = False
            st.rerun()

        # Step 4: Render chat UI (normal state)
        render_chat_ui(chatbot_client)
        # If there was an error, show it visibly in the UI
        if st.session_state.get("chatbot_error"):
            st.error(f"Assistant error: {st.session_state['chatbot_error']}")
    with col_recs:
    # logger.debug(f"[DEBUG] Rendering recommendations with filters: {st.session_state['filters']}")
        try:
            from components.recommendation_panel import RecommendationPanel
            RecommendationPanel.render(filters=st.session_state["filters"])
        except Exception as e:
            st.error(f"Failed to load recommendations: {e}")
    logger.info("[MAIN] Finished main()")

# Call main only after its definition
if __name__ == "__main__":
    main()




