from befriends.common.config import AppConfig
import requests
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
load_dotenv()

class ChatbotConfig:
    """Configuration for the GPT-5 chatbot client."""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig.from_env()
        self.endpoint = self.config.openai_api_endpoint
        self.api_key = self.config.openai_api_key
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set in environment or AppConfig."
            )


class ChatbotClient:
    """Client for interacting with GPT-5 via OpenAI API."""

    def __init__(self, config: ChatbotConfig):
        self.config = config

    def get_response(
        self,
        user_id: str,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo"  # Use a valid default model
    ) -> str:
        logger = logging.getLogger("ChatbotClient")
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 256,  # Limit response length for speed
            "temperature": 0.7,  # Keep answers relevant
            # 'user' is optional and only supported for some models, so only include if not None
        }
        # Only add 'user' if not None and not empty
        if user_id:
            payload["user"] = user_id
        if not isinstance(self.config.endpoint, str):
            logger.error("ChatbotConfig.endpoint must be a string, got: %s",
                         type(self.config.endpoint))
            raise ValueError("ChatbotConfig.endpoint must be a string.")
        logger.info("Sending request to backend endpoint: %s", self.config.endpoint)
        logger.debug("Payload: %s", payload)
        try:
            response = requests.post(
                self.config.endpoint,
                headers=headers,
                json=payload,
                timeout=30  # Allow up to 30s for OpenAI response
            )
            logger.info(f"[DEBUG] OpenAI API request payload: {payload}")
            logger.info(f"[DEBUG] OpenAI API response status: {response.status_code}")
        except requests.Timeout:
            logger.error("Backend request timed out after 30 seconds.")
            msg = "The backend took too long to respond (30s). Please try again later."
            raise RuntimeError(msg)
        except Exception as e:
            logger.exception("Backend request failed: %s", e)
            raise RuntimeError(f"Backend error: {e}")
        try:
            response.raise_for_status()
            data = response.json()
            logger.info(f"[DEBUG] OpenAI API response JSON: {data}")
            if not data or "choices" not in data or not data["choices"] or "message" not in data["choices"][0] or "content" not in data["choices"][0]["message"]:
                logger.error(f"[ERROR] Malformed OpenAI API response: {data}")
        except Exception as e:
            logger.exception("Failed to parse backend response: %s", e)
            raise RuntimeError(f"Failed to parse backend response: {e}")
        # OpenAI API returns choices[0]['message']['content']
        logger.debug("Backend response JSON: %s", data)
        # Defensive: Always return a string, even if malformed
        try:
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                logger.error(f"[ERROR] OpenAI API response missing or empty content: {data}")
                logger.info(f"[TRACE] Returning fallback assistant message from ChatbotClient: I'm here to help! Could you please rephrase your question or ask about events, concerts, or activities? 😊")
                return "I'm here to help! Could you please rephrase your question or ask about events, concerts, or activities? 😊"
            logger.info(f"[TRACE] Returning assistant content from ChatbotClient: {repr(content)}")
            return content
        except Exception as e:
            logger.error(f"[ERROR] Exception extracting content from OpenAI API response: {e}, data: {data}")
            logger.info(f"[TRACE] Returning fallback assistant message from ChatbotClient: I'm here to help! Could you please rephrase your question or ask about events, concerts, or activities? 😊")
            return "I'm here to help! Could you please rephrase your question or ask about events, concerts, or activities? 😊"
