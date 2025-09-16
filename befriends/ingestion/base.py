"""Abstract base for source connectors."""

from __future__ import annotations

from abc import ABC, abstractmethod


class SourceConnector(ABC):
    """Abstract connector for event sources."""

    @abstractmethod
    def fetch_raw(self) -> list[dict]:
        """Fetch raw event data from the source."""
        raise NotImplementedError()

    @abstractmethod
    def healthcheck(self) -> dict:
        """Return health status of the connector."""
        raise NotImplementedError()
