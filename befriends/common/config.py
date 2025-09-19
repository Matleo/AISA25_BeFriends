"""Application configuration."""
from __future__ import annotations
import os

import json
from typing import Any



from dotenv import load_dotenv
load_dotenv()

class AppConfig:
    """Holds application configuration, secrets, and feature flags."""

    def __init__(
        self,
        db_url: str,
        openai_api_key: str,
        openai_api_endpoint: str,
        sources: list[dict],
        features: dict[str, Any],
    ):
        self.db_url = db_url
        self.openai_api_key = openai_api_key
        self.openai_api_endpoint = openai_api_endpoint
        self.sources = sources
        self.features = features

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Factory: load config from environment variables or .env file."""
        db_url = os.getenv("BEFRIENDS_DB_URL", "sqlite:///events.db")
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        openai_api_endpoint = os.getenv(
            "OPENAI_API_ENDPOINT",
            "https://api.openai.com/v1/chat/completions"
        )
        sources_json = os.getenv("BEFRIENDS_SOURCES", "[]")
        try:
            sources = json.loads(sources_json)
        except Exception:
            sources = []
        features = {}
        features_str = os.getenv("BEFRIENDS_FEATURES", "")
        for feat in features_str.split(","):
            if feat:
                features[feat.strip()] = True
        return cls(
            db_url=db_url,
            openai_api_key=openai_api_key,
            openai_api_endpoint=openai_api_endpoint,
            sources=sources,
            features=features,
        )

    @property
    def is_openai_enabled(self) -> bool:
        return bool(self.openai_api_key)
