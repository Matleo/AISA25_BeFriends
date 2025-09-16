"""Application configuration."""

from __future__ import annotations
import os
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional


class AppConfig:
    """Holds application configuration sources and feature flags."""

    def __init__(self, db_url: str, sources: list[dict], features: dict[str, Any]):
        self.sources: list[dict] = sources
        """Initialize config with db_url, sources, and features."""
        self.db_url = db_url
        self.sources = sources
        self.features = features

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Factory: load config from environment variables or .env file."""
        db_url = os.getenv("BEFRIENDS_DB_URL", "sqlite:///events.db")
        # Example: load feature flags from env as comma-separated list
        features = {}
        features_str = os.getenv("BEFRIENDS_FEATURES", "")
        for feat in features_str.split(","):
            if feat:
                features[feat.strip()] = True
        # Example: sources could be loaded from a JSON env var or file (stubbed here)
        sources = []
        return cls(db_url=db_url, sources=sources, features=features)
