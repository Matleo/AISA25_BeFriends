
import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
load_dotenv()


class ChatbotConfig:
    """Configuration for the GPT-5 chatbot client."""

    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        self.endpoint = endpoint or os.getenv(
            "OPENAI_API_ENDPOINT",
            "https://api.openai.com/v1/chat/completions"
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set in environment or passed to ChatbotConfig."
            )


class ChatbotClient:
    """Client for interacting with GPT-5 via OpenAI API."""

    def __init__(self, config: ChatbotConfig):
        self.config = config

    def get_response(
        self,
        user_id: str,
        messages: List[Dict[str, str]],
        model: str = "gpt-5"
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "user": user_id
        }
        if not isinstance(self.config.endpoint, str):
            raise ValueError("ChatbotConfig.endpoint must be a string.")
        response = requests.post(
            self.config.endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        # OpenAI API returns choices[0]['message']['content']
        return data["choices"][0]["message"]["content"]
