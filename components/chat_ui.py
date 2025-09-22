import streamlit as st
import html
from typing import Optional

def render_chat_card_header():
    st.markdown(
        """
        <div class='chat-card-header' style='display:flex; align-items:center; gap:0.7em; margin-bottom:0em; min-height:0;'>
            <span style='font-size:2.1rem; font-weight:700; line-height:1;'>🤗 Meet <span style="color:#1976d2">EventMate</span></span>
            <div style='flex:1;'></div>
            <button onclick="window.location.reload()" style='background:none; border:none; cursor:pointer; font-size:1.3em; margin-left:auto;' title='Clear Conversation'>🗑️</button>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_chat_card_container_start():
    st.markdown(
        """
        <div class='chat-card' style='margin:0 !important; box-shadow:0 4px 24px #0001; border-radius:18px; background:#fff; padding:0.5em 2em 0.5em 2em; border:2.5px solid #1976d2; display:flex; flex-direction:column; gap:0;'>
        """,
        unsafe_allow_html=True,
    )

def render_chat_card_container_end():
    st.markdown("</div>", unsafe_allow_html=True)

def render_spinner():
        st.markdown(
                """
                <div style='display:flex;align-items:center;gap:0.7em;margin:0.1em 0 0.1em 0;'>
                        <span style='font-size:1.5em;'>🤗</span>
                        <span style='font-size:1.1em;color:#1976d2;'>EventMate is thinking</span>
                        <span class='dot-flashing'></span>
                </div>
                <style>
                .dot-flashing {
                    position: relative;
                    width: 10px;
                    height: 10px;
                    border-radius: 5px;
                    background-color: #1976d2;
                    color: #1976d2;
                    animation: dotFlashing 1s infinite linear alternate;
                    animation-delay: .5s;
                    margin-left: 0.5em;
                }
                @keyframes dotFlashing {
                    0% { opacity: 1; }
                    50%, 100% { opacity: 0.2; }
                }
                </style>
                """,
                unsafe_allow_html=True,
        )
import logging
logger = logging.getLogger(__name__)

def render_onboarding_and_quick_replies():
    logger.info("Entered render_onboarding_and_quick_replies")
    try:
        logger.info(f"streamlit module: {st}")
    except Exception as e:
        logger.error(f"streamlit import error: {e}")
    st.chat_message("assistant").write(
        "👋 Hi! I'm <b>EventMate</b>, your friendly companion for discovering fun things to do. "
        "What are you in the mood for? Try one of these or ask me anything!",
        unsafe_allow_html=True
    )
    quick_replies = [
        {"label": "Find something fun tonight!", "value": "What's happening tonight?"},
        {"label": "Surprise me with an event!", "value": "Surprise me with a random event."},
        {"label": "Best free events nearby", "value": "Show me the best free events near me."},
        {"label": "Family or kids activities", "value": "What can I do with my family or kids this weekend?"},
        {"label": "Meet new people", "value": "Show me social events where I can meet new people."},
    ]
    st.markdown("<div class='quick-reply-row' style='margin-top:0.5em;'>", unsafe_allow_html=True)
    cols = st.columns(len(quick_replies))
    for i, chip in enumerate(quick_replies):
        if cols[i].button(chip["label"], key=f"quickreply_{i}", help=chip["value"], use_container_width=True):
            st.session_state["pending_user_message"] = chip["value"]
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    quick_replies = [
        {"label": "Find something fun tonight!", "value": "What's happening tonight?"},
        {"label": "Surprise me with an event!", "value": "Surprise me with a random event."},
        {"label": "Best free events nearby", "value": "Show me the best free events near me."},
        {"label": "Family or kids activities", "value": "What can I do with my family or kids this weekend?"},
        {"label": "Meet new people", "value": "Show me social events where I can meet new people."},
    ]
    st.markdown("<div class='quick-reply-row' style='margin-top:0.5em;'>", unsafe_allow_html=True)
    cols = st.columns(len(quick_replies))
    import html
    from typing import Optional
    st.markdown("</div>", unsafe_allow_html=True)

def strip_html(text: Optional[str]) -> str:
    if not isinstance(text, str):
        return ""
    import re
    return re.sub(r'<[^>]+>', '', html.unescape(text))

def render_chat_bubble(role: str, content: str, timestamp: str, show_label: bool) -> str:
    """
    Returns HTML for a single chat bubble.
    """
    avatar = "🧑" if role == "user" else "🤖"
    label = "You" if role == "user" else "EventMate"
    avatar_html = f'<div class="avatar">{avatar}</div>' if show_label else ''
    label_html = f'<div class="sender-label">{label}</div>' if show_label else ''
    content = strip_html(content)
    bubble = f'''
<div class='chat-row {role}'>
    {avatar_html}
    <div class='bubble-group'>
        {label_html}
        <div class='chat-bubble {role}'>{content}</div>
        <div class='timestamp'>{timestamp}</div>
    </div>
</div>
    '''
    return bubble
