
import streamlit as st
import uuid
import datetime
import os
import re
import traceback
from befriends.chatbot_client import ChatbotConfig, ChatbotClient


# Helper to load HTML templates from file
def load_html_templates(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# Helper to extract template by id from HTML file
def get_template(html, template_id):
    pattern = rf'<script type="text/template" id="{template_id}">(.*?)</script>'
    match = re.search(pattern, html, re.DOTALL)
    return match.group(1).strip() if match else None


# Path to HTML templates
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "assets", "chat_bubbles.html")
HTML_TEMPLATES = load_html_templates(TEMPLATE_PATH)
SYSTEM_BUBBLE = get_template(HTML_TEMPLATES, "system-bubble")
USER_BUBBLE = get_template(HTML_TEMPLATES, "user-bubble")
ASSISTANT_BUBBLE = get_template(HTML_TEMPLATES, "assistant-bubble")
TYPING_BUBBLE = get_template(HTML_TEMPLATES, "typing-bubble")

st.set_page_config(page_title="Chatbot Conversation", page_icon="💬", layout="centered")
st.title("🤖 Chat with EventBot")
st.subheader("Conversation")

# Generate a unique user_id per session and hide from UI
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())
user_id = st.session_state["user_id"]

# Chat history state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {
            "role": "assistant",
            "content": (
                "👋 Hi! I'm EventBot. Ask me anything about events or just say hello!"
            ),
            "timestamp": datetime.datetime.now().strftime("%H:%M"),
        }
    ]

# Rerun flag to avoid infinite rerun
if "pending_rerun" not in st.session_state:
    st.session_state["pending_rerun"] = False

# Show chat history section with welcome message, icons, and timestamps
st.markdown("---")
st.subheader("Conversation")

# Render chat history
for msg in st.session_state["chat_history"]:
    timestamp = msg.get("timestamp")
    if not timestamp and msg["role"] != "system":
        timestamp = datetime.datetime.now().strftime("%H:%M")
        msg["timestamp"] = timestamp
    if msg["role"] == "user":
        html = USER_BUBBLE.replace("{{content}}", msg["content"])
        html = html.replace("{{timestamp}}", timestamp)
        st.markdown(html, unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        html = ASSISTANT_BUBBLE.replace("{{content}}", msg["content"])
        html = html.replace("{{timestamp}}", timestamp)
        st.markdown(html, unsafe_allow_html=True)

# If waiting for bot, show a placeholder message bubble for EventBot above the input (single line)
if st.session_state.get("waiting_for_bot", False):
    st.markdown(TYPING_BUBBLE, unsafe_allow_html=True)


# Only show input form if not waiting for bot
if not st.session_state.get("waiting_for_bot", False):
    with st.form(key="chat_form", clear_on_submit=True):
        user_message = st.text_input(
            "Your message",
            key="user_message_input",
            disabled=False,
        )
        submitted = st.form_submit_button("Send", disabled=False)
        if submitted and user_message:
            # Add user message immediately with timestamp
            st.session_state["chat_history"].append(
                {
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.datetime.now().strftime("%H:%M"),
                }
            )
            # Set waiting flag and trigger rerun for bot response
            st.session_state["waiting_for_bot"] = True
            st.rerun()

if st.session_state.get("waiting_for_bot", False):
    # Only process if last message is from user and no assistant response yet
    history = st.session_state["chat_history"]
    if len(history) > 0 and history[-1]["role"] == "user":
        try:
            config = ChatbotConfig()
            client = ChatbotClient(config)
            response = client.get_response(user_id, history)
            st.session_state["chat_history"].append(
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.datetime.now().strftime("%H:%M"),
                }
            )
        except Exception as e:
            # Always show a visible assistant bubble for errors
            tb = traceback.format_exc()
            error_msg = (
                "😔 Sorry, I couldn't answer that. Please try rephrasing your question or ask "
                "something simpler. (Error: {} )".format(str(e))
            )
            st.session_state["chat_history"].append(
                {
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.datetime.now().strftime("%H:%M"),
                }
            )
            # Optionally, show the traceback in the Streamlit error area for debugging
            st.error(f"Backend error: {e}\n\n{tb}")
        finally:
            st.session_state["waiting_for_bot"] = False
            st.rerun()

if st.button("Clear Conversation"):
    st.session_state["chat_history"] = []
    st.session_state["user_message_input"] = ""
