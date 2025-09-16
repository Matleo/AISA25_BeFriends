"""Application configuration."""

from __future__ import annotations

class AppConfig:
    """Holds application configuration sources and feature flags."""

    def __init__(self, sources: list[dict], features: dict):
        """Initialize config with sources and features."""
        self.sources = sources
        self.features = features

    @classmethod
    def from_env(cls) -> AppConfig:
        """Factory: load config from environment."""
        # ...load sources and features from env...
        return cls(sources=[], features={})
