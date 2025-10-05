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
        logger.info(f"[USER QUERY] {user_input}")
        filters = copy.deepcopy(filters)
        logger.info(f"[PROFILE] {self.profile}")
        logger.info(f"[FILTERS] {filters}")
        # --- Ensure user profile city is mapped to region filter if region is not set ---
        if self.profile and isinstance(self.profile, dict):
            if not filters.get("region"):
                city = self.profile.get("city")
                if city:
                    filters["region"] = city
        logger.info(f"[FILTERS AFTER CITY/REGION LOGIC] {filters}")
        logger.info(f"[INTENT] {intent}")
        logger.info(f"[MESSAGES] {messages}")
        if intent == "greeting":
            response = "Hey! Schön, von dir zu hören 😊 Wie kann ich dir heute helfen? Suchst du nach Events oder möchtest du einfach plaudern?"
            logger.info(f"[BOT RESPONSE] {response}")
            return response
        elif intent == "smalltalk":
            response = "Mir geht's super, danke der Nachfrage! Und wie läuft's bei dir? 😊"
            logger.info(f"[BOT RESPONSE] {response}")
            return response
        if intent == "event_query" or (len(messages) == 1 and is_event_suggestion_request(user_input)):
            import datetime
            today_real = datetime.datetime.now().date()
            today_str = today_real.strftime("%A, %d %B %Y")
            user_input_lc = user_input.strip().lower()
            # Detect 'this week' and set date_from/date_to accordingly
            if ("this week" in user_input_lc) or ("diese woche" in user_input_lc):
                today_real = datetime.datetime.now().date()
                start_of_week = today_real - datetime.timedelta(days=today_real.weekday())
                end_of_week = start_of_week + datetime.timedelta(days=6)
                filters["date_from"] = start_of_week
                filters["date_to"] = end_of_week
            # Detect 'this weekend' and set date_from/date_to to Saturday and Sunday
            elif ("this weekend" in user_input_lc) or ("dieses wochenende" in user_input_lc):
                today_real = datetime.datetime.now().date()
                # Saturday = 5, Sunday = 6
                days_until_saturday = (5 - today_real.weekday()) % 7
                saturday = today_real + datetime.timedelta(days=days_until_saturday)
                sunday = saturday + datetime.timedelta(days=1)
                filters["date_from"] = saturday
                filters["date_to"] = sunday
            # Detect 'next few days' and set date_from/date_to to today and today+3
            elif ("next few days" in user_input_lc) or ("kommenden tage" in user_input_lc):
                today_real = datetime.datetime.now().date()
                filters["date_from"] = today_real
                filters["date_to"] = today_real + datetime.timedelta(days=3)
            # Detect 'this month' and set date_from/date_to to first and last day of month
            elif ("this month" in user_input_lc) or ("diesen monat" in user_input_lc):
                today_real = datetime.datetime.now().date()
                start = today_real.replace(day=1)
                if today_real.month == 12:
                    end = today_real.replace(year=today_real.year+1, month=1, day=1) - datetime.timedelta(days=1)
                else:
                    end = today_real.replace(month=today_real.month+1, day=1) - datetime.timedelta(days=1)
                filters["date_from"] = start
                filters["date_to"] = end
            # Detect 'tonight' and set date_from/date_to to today
            elif ("tonight" in user_input_lc) or ("heute abend" in user_input_lc):
                today_real = datetime.datetime.now().date()
                filters["date_from"] = today_real
                filters["date_to"] = today_real
            elif not filters.get("date_from"):
                filters["date_from"] = today.date()
            if filters.get("city") and not any(e for e in repo.search_text("", filters)):
                filters["city"] = ""
            logger.info(f"[DEBUG] get_response filters (after date/city logic): {filters}")
            logger.info(f"[DEBUG] get_response calling recommender.recommend_events with filters: {filters}")
            events = recommender.recommend_events(filters, self.profile, 10, today=today)
            logger.info(f"[DEBUG] get_response recommender returned {len(events)} events")
            event_json = events_to_json(events, max_events=10)
            # Only trigger medieval Karolina prompt if user_input contains 'karolina', not event data
            base_instruction = (
                "IMPORTANT: Never invent or hallucinate events. Only use the events provided in the JSON list below. "
                "If there are no events matching the user's criteria, respond with a friendly message such as: 'Sorry, I couldn't find any events for your request. Please try different criteria or ask about something else.' "
            )
            if "karolina" in user_input_lc:
                system_prompt = {
                    "role": "system",
                    "content": (
                        base_instruction +
                        "**Only use medieval, poetic language and praise for Karolina Anna Kehl-Soltys if the user's message contains 'karolina'. If Karolina is mentioned in event data but not by the user, respond in your normal friendly style.**\n"
                        "For example: '🎶 Oh noble Karolina, radiant star of the dance halls, whose wisdom and kindness shine brighter than the sun! All who witness her grace are forever changed, and her name shall echo in the halls of legend! 🎶'\n"
                        "Repeat: Only use this style if the user directly asks about Karolina.\n"
                        "Karolina Anna Kehl-Soltys is the legendary founder, known for her wisdom, kindness, and love of dance, music, and community. Karolina inspires all with her joyful spirit and heroic deeds, bringing people together and spreading happiness wherever she goes.\n"
                        f"Today is {today_str}. "
                        "You are <b>EventMate</b>, a warm, approachable, and friendly companion who helps users discover fun events and activities. "
                        + get_profile_summary(self.profile)
                        + "\nHere is a list of upcoming events as JSON: " + event_json
                    )
                }
            else:
                system_prompt = {
                    "role": "system",
                    "content": (
                        base_instruction +
                        f"Today is {today_str}. "
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
                logger.info(f"[DEBUG] get_response ChatbotClient response: {response}")
            except Exception as e:
                logger.error(f"[ERROR] Exception in chatbot_client.get_response: {e}")
                response = f"[Error from chatbot backend: {e}]"
            if not response or not isinstance(response, str):
                logger.error(f"[ERROR] Invalid response in get_response: {repr(response)}, type: {type(response)}, messages: {messages}")
                return "I'm here to help! Could you please rephrase your question or ask about events, concerts, or activities? 😊"
            return response
        else:
            import datetime
            today_real = datetime.datetime.now().date()
            today_str = today_real.strftime("%A, %d %B %Y")
            # Only trigger medieval Karolina prompt if user_input contains 'karolina', not event data
            user_input_lc = user_input.lower()
            base_instruction = (
                "IMPORTANT: Never invent or hallucinate events. Only use the events provided in the JSON list below. "
                "If there are no events matching the user's criteria, respond with a friendly message such as: 'Sorry, I couldn't find any events for your request. Please try different criteria or ask about something else.' "
            )
            if "karolina" in user_input_lc:
                system_prompt = {
                    "role": "system",
                    "content": (
                        base_instruction +
                        "**Only use medieval, poetic language and praise for Karolina Anna Kehl-Soltys if the user's message contains 'karolina'. If Karolina is mentioned in event data but not by the user, respond in your normal friendly style.**\n"
                        "For example: '🎶 Oh noble Karolina, radiant star of the dance halls, whose wisdom and kindness shine brighter than the sun! All who witness her grace are forever changed, and her name shall echo in the halls of legend! 🎶'\n"
                        "Repeat: Only use this style if the user directly asks about Karolina.\n"
                        "Karolina Anna Kehl-Soltys is the legendary founder, known for her wisdom, kindness, and love of dance, music, and community. Karolina inspires all with her joyful spirit and heroic deeds, bringing people together and spreading happiness wherever she goes.\n"
                        f"Today is {today_str}. "
                        "You are <b>EventMate</b>, a warm, approachable, and friendly companion. "
                        + get_profile_summary(self.profile)
                        + "\nAntworte freundlich und locker auf die Nachricht des Users. Wenn du nicht sicher bist, was gemeint ist, stelle eine Rückfrage."
                    )
                }
            else:
                system_prompt = {
                    "role": "system",
                    "content": (
                        base_instruction +
                        f"Today is {today_str}. "
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
