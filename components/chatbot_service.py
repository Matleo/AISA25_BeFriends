import re
import copy

import logging

# Move is_event_suggestion_request here to avoid circular import
import re
def is_event_suggestion_request(user_input: str) -> bool:
    """Detect if the user is asking for event suggestions in a generic way."""
    user_input = user_input.strip().lower()
    patterns = [
        r"what's happening( this weekend)?",
        r"any events( this weekend)?",
        r"was geht( am wochenende)?",
        r"tipps?",
        r"irgendwas los",
    ]
    return any(re.search(pat, user_input) for pat in patterns)

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
        logger = logging.getLogger("chatbot_service")
        filters = copy.deepcopy(filters)
        if intent == "greeting":
            return "Hey! Schön, von dir zu hören 😊 Wie kann ich dir heute helfen? Suchst du nach Events oder möchtest du einfach plaudern?"
        elif intent == "smalltalk":
            return "Mir geht's super, danke der Nachfrage! Und wie läuft's bei dir? 😊"
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
                logger.info(f"[DEBUG] ChatbotClient response type: {type(response)}, value: {repr(response)}")
            except Exception as e:
                logger.error(f"[ERROR] Exception in chatbot_client.get_response: {e}")
                response = f"[Error from chatbot backend: {e}]"
            if not response or not isinstance(response, str):
                logger.error(f"[ERROR] Invalid response in get_response: {repr(response)}, type: {type(response)}, messages: {messages}")
                return "I'm here to help! Could you please rephrase your question or ask about events, concerts, or activities? 😊"
            return response
        else:
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
                logger.info(f"[DEBUG] ChatbotClient response type: {type(response)}, value: {repr(response)}")
            except Exception as e:
                logger.error(f"[ERROR] Exception in chatbot_client.get_response: {e}")
                response = f"[Error from chatbot backend: {e}]"
            if not response or not isinstance(response, str):
                logger.error(f"[ERROR] Invalid response in get_response: {repr(response)}, type: {type(response)}, messages: {messages}")
                return "I'm here to help! Could you please rephrase your question or ask about events, concerts, or activities? 😊"
            return response
