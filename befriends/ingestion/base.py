"""Abstract base for source connectors."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

class SourceConnector(ABC):
    """Abstract connector for event sources."""


    @abstractmethod
    def fetch_raw(self) -> list[dict]:
        """Fetch raw event data from the source."""
        try:
            # Implementation in subclass
            pass
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(f"Error fetching raw data: {e}")
            raise

    @abstractmethod
    def healthcheck(self) -> dict:
        """Return health status of the connector."""
        try:
            # Implementation in subclass
            pass
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(f"Error in healthcheck: {e}")
            raise
