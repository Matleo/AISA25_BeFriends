
import streamlit as st
st.set_page_config(page_title="EventMate", page_icon="💬", layout="wide")
import logging
# Setup logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("streamlit_chatbot")
logger.setLevel(logging.INFO)

# --- Imports ---
import html
import uuid
import datetime
import json
from pathlib import Path
from components.ui import render_sidebar_filters
from components.chat_ui import (
    render_chat_card_header,
    render_chat_card_container_start,
    render_chat_card_container_end,
    render_spinner,
    render_onboarding_and_quick_replies,
    render_chat_bubble,
)
from befriends.recommendation.service import RecommendationService
from befriends.catalog.repository import CatalogRepository
from befriends.chatbot_client import ChatbotClient, ChatbotConfig
from befriends.common.config import AppConfig
from befriends.response.formatter import ResponseFormatter
from befriends.response.event_json import events_to_json
from components.profile_manager import ProfileManager
from components.chatbot_service import ChatbotService

# --- Constants ---
CHAT_HEADER_PATH = "assets/chat_header.html"
CHAT_HISTORY_CONTAINER_PATH = "assets/chat_history_container.html"
CHAT_STYLES_PATH = "assets/chat_styles.css"

# --- Utility Functions ---
def get_chatbot_today():
    return datetime.datetime.now()



def get_event_summaries(filters, profile, limit=10):
    """Get event summaries for recommendations."""
    filters = st.session_state.get("filters", filters)
    profile = st.session_state.get("profile", profile)
    if "region" in filters and "region_standardized" not in filters:
        filters["region_standardized"] = filters["region"]
        del filters["region"]
    try:
        repo = CatalogRepository()
        recommender = RecommendationService(repo)
        events = recommender.recommend_events(filters, profile, limit, today=get_chatbot_today())
        formatter = ResponseFormatter()
        return formatter.chat_event_summary(events)
    except Exception:
        return "(No events available)"
def get_profile_summary(profile):
    """Format profile summary for display."""
    return (
        f"Age: {profile['age']}, City: {profile['city']}. "
        f"Interests: {', '.join(profile['interests'])}."
    )


# --- Chat UI Rendering ---
def render_chat_ui(chatbot_client):
    """Render chat history, input, and spinner if needed."""
    try:
        with open(CHAT_HEADER_PATH) as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    except Exception:
        st.warning("Could not load chat header asset.")
    render_chat_card_container_start()
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
    st.markdown("</div>", unsafe_allow_html=True)
    try:
        with open(CHAT_STYLES_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        st.warning("Could not load chat styles asset.")
    if len(st.session_state["messages"]) == 0:
        render_onboarding_and_quick_replies()
    # Chat input area CSS
    st.markdown("""
    <style>
    .chat-input-bar { display: flex; align-items: center; background: #f7f8fa; border-radius: 2em; box-shadow: 0 2px 8px #0001; border: 1.5px solid #e3f2fd; padding: 0.1em 1.2em 0.1em 1.2em; margin: 0.5em 0 0.2em 0; min-height: 3.2em; }
    .chat-input-bar input { flex: 1; border: none; background: transparent; outline: none; font-size: 1.08em; padding: 0.6em 0; min-width: 0; }
    .chat-input-bar input:focus { outline: none; }
    .chat-send-btn { background: #1976d2; border: none; border-radius: 50%; width: 2.4em; height: 2.4em; display: flex; align-items: center; justify-content: center; margin-left: 0.4em; transition: background 0.2s, box-shadow 0.2s; box-shadow: 0 2px 8px #1976d220; cursor: pointer; }
    .chat-send-btn:disabled { background: #b0b8c1; cursor: not-allowed; }
    .chat-send-btn:hover:not(:disabled) { background: #1565c0; box-shadow: 0 4px 12px #1976d240; }
    .chat-send-btn svg { color: #fff; font-size: 1.15em; }
    .chat-mic-btn { background: none; border: none; margin-left: 0.2em; color: #b0b8c1; font-size: 1.35em; cursor: not-allowed; transition: color 0.2s; padding: 0; }
    .chat-mic-btn[title]:hover { color: #1976d2; }
    </style>
    """, unsafe_allow_html=True)
    # Clear input if flag is set
    if st.session_state.get("clear_input", False):
        st.session_state["chat_input_box"] = ""
        st.session_state["clear_input"] = False
    # Chat input form
    with st.form(key="chat_input_form_unique"):
        cols = st.columns([10,1])
        with cols[0]:
            user_input = st.text_input(
                "Ask a question",  # Non-empty label for accessibility
                key="chat_input_box",
                placeholder="Ask me anything about events, concerts, or activities...",
                label_visibility="collapsed"
            )
        with cols[1]:
            send = st.form_submit_button(
                label="Send",
                use_container_width=True
            )
        if send:
            if user_input.strip():
                st.session_state["pending_user_message"] = user_input.strip()
                st.session_state["clear_input"] = True
                logger.info("[TRACE] Form submitted, message sent.")
                st.rerun()
            else:
                st.warning("Please enter a message before sending.")

def append_message(role, content):
    """Append a message to chat history."""
    now_str = datetime.datetime.now().strftime("%H:%M")
    st.session_state["messages"].append({"role": role, "content": content, "timestamp": now_str})

# --- Main app entrypoint ---
def main():
    logger.info("Streamlit EventMate app started.")
    logger.info(f"Session state: {dict(st.session_state)}")
    """Main entrypoint for Streamlit chatbot app."""
    # --- State Initialization ---
    # Robust session state initialization
    for key, default in [
        ("pending_user_message", None),
        ("is_typing", False),
        ("spinner_shown", False),
        ("chatbot_error", None),
        ("show_debug", False),
        ("show_sidebar", False),
        ("messages", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default
    if "filters" not in st.session_state or not st.session_state.filters:
        st.session_state.filters = ProfileManager.get_default_filters()
    if "region" in st.session_state.filters and "region_standardized" not in st.session_state.filters:
        st.session_state.filters["region_standardized"] = st.session_state.filters["region"]
        del st.session_state.filters["region"]
    if "apply_filters" not in st.session_state.filters or not st.session_state.filters["apply_filters"]:
        st.session_state.filters["apply_filters"] = True
    if not st.session_state["messages"]:
        today = datetime.datetime.now().date()
        one_month_later = today + datetime.timedelta(days=30)
        st.session_state["filters"]["date_from"] = today
        st.session_state["filters"]["date_to"] = one_month_later

    # --- AppConfig and ChatbotClient setup ---
    chatbot_client = None
    chatbot_init_error = None
    try:
        config = AppConfig.from_env()
        chatbot_client = ChatbotClient(ChatbotConfig(config))
        logger.info("ChatbotClient initialized.")
    except Exception as e:
        chatbot_init_error = e
        logger.error(f"Chatbot init error: {e}")

    # --- Layout ---
    try:
        with open("static/eventbot.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load custom CSS: {e}. The chat UI may look less polished.")

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("## EventBot Filters")
        try:
            sidebar_filters = render_sidebar_filters(default_city=ProfileManager.get_default_city())
        except Exception as e:
            st.error(f"Failed to load sidebar filters: {e}")
            logger.error(f"Sidebar filter error: {e}")
            sidebar_filters = {}
        if sidebar_filters.get("apply_filters"):
            logger.info("Sidebar: Apply filters pressed.")
            st.session_state["filters"] = sidebar_filters.copy()
        elif sidebar_filters.get("reset_filters"):
            logger.info("Sidebar: Reset filters pressed.")
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
                "region_standardized": st.session_state.get("filters", {}).get("region_standardized"),
            })

    # --- Main Chat and Recommendations Layout ---
    col_chat, col_recs = st.columns([1.35, 0.95], gap="large")
    logger.info("[TRACE] Entered main UI rendering block.")
    pending_user_message = st.session_state.get("pending_user_message", None)
    is_typing = st.session_state.get("is_typing", False)
    spinner_shown = st.session_state.get("spinner_shown", False)
    error_message = st.session_state.get("chatbot_error", None)
    logger.info(f"[TRACE] State: pending_user_message={pending_user_message}, is_typing={is_typing}, spinner_shown={spinner_shown}, error_message={error_message}")

    if chatbot_init_error:
        logger.info("[TRACE] chatbot_init_error detected, rendering error UI.")
        with col_chat:
            st.error(f"Failed to initialize chatbot: {chatbot_init_error}. Please check your configuration and try again.")
            logger.error(f"Chatbot init error: {chatbot_init_error}")
    else:
        # State machine: only mutate state and rerun
        logger.info("[TRACE] Entered state machine block.")
        if pending_user_message and not is_typing:
            logger.info(f"[TRACE] State: User submitted message, triggering rerun.")
            safe_input = html.escape(pending_user_message)
            append_message("user", safe_input)
            st.session_state["is_typing"] = True
            st.session_state["pending_user_message"] = None
            st.session_state["spinner_shown"] = True
            st.session_state["chatbot_error"] = None
            logger.info(f"[TRACE] State updated, calling st.rerun().")
            st.rerun()
        elif is_typing and spinner_shown:
            logger.info("[TRACE] State: Backend call should run.")
            if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
                try:
                    logger.info("Chatbot: Backend call started.")
                    chatbot_service = ChatbotService(chatbot_client, st.session_state["profile"])
                    last_user_message = st.session_state["messages"][-1]["content"]
                    intent = chatbot_service.detect_intent(last_user_message)
                    response = chatbot_service.get_response(
                        last_user_message,
                        st.session_state["messages"],
                        st.session_state["filters"],
                        intent,
                        get_chatbot_today(),
                        CatalogRepository(),
                        RecommendationService(CatalogRepository()),
                        events_to_json,
                        get_profile_summary,
                    )
                    logger.info(f"Chatbot: Backend call finished. Response: {response}")
                    if isinstance(response, dict) and "content" in response:
                        response = response["content"]
                    if not response or not isinstance(response, str) or not response.strip():
                        error_id = str(uuid.uuid4())
                        logger.error(f"Chatbot: Empty/invalid assistant response (error_id={error_id})")
                        raise ValueError(f"Empty or invalid assistant response (error_id={error_id})")
                    st.session_state["chatbot_error"] = None
                except Exception as e:
                    response = f"[System error: {e}]"
                    st.session_state["chatbot_error"] = str(e)
                    logger.error(f"Chatbot: Backend error: {e}")
                append_message("assistant", response)
                st.session_state["is_typing"] = False
                st.session_state["spinner_shown"] = False
                logger.info(f"[TRACE] Backend call complete, calling st.rerun().")
                st.rerun()
    logger.info("[TRACE] Rendering chat UI block.")
    with col_chat:
        logger.info(f"[TRACE] About to render_chat_ui. session_state: {dict(st.session_state)}")
        render_chat_ui(chatbot_client)
        logger.info(f"[TRACE] Chat UI rendered. is_typing={is_typing}")
        if is_typing:
            logger.info("[TRACE] Rendering spinner UI.")
            render_spinner()
        if error_message:
            logger.error(f"Chatbot: Assistant error: {error_message}")
            st.error(f"Assistant error: {error_message}")
    logger.info(f"[TRACE] Rendering recommendations UI block. filters={st.session_state.get('filters')}")
    with col_recs:
        try:
            from components.recommendation_panel import RecommendationPanel
            logger.info(f"[TRACE] About to render RecommendationPanel. filters={st.session_state.get('filters')}")
            RecommendationPanel.render(filters=st.session_state["filters"])
            logger.info("[TRACE] Recommendations UI rendered.")
        except Exception as e:
            logger.error(f"Recommendations: Failed to load: {e}")
            st.error(f"Failed to load recommendations: {e}")

if __name__ == "__main__":
    main()
