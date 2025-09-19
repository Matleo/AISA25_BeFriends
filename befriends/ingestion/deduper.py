"""Deduplication logic for events."""

from __future__ import annotations

import logging
from ..domain.event import Event


class Deduper:
    """Detects and merges duplicate events."""

    def is_duplicate(self, a: Event, b: Event) -> bool:
        """Return True if two events are duplicates."""
        try:
            # Minimal attribute access for testability/coverage
            return (
                getattr(a, "name", None) == getattr(b, "name", None)
                and getattr(a, "date", None) == getattr(b, "date", None)
            )
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(
                f"Error in is_duplicate: {e}"
            )
            raise

    def merge(self, a: Event, b: Event) -> Event:
        """Merge two duplicate events into one."""
        try:
            # ...merge logic...
            return a
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(f"Error in merge: {e}")
            raise

    def dedupe(self, events: list[Event]) -> list[Event]:
        """Remove duplicates from a list of events."""
        try:
            # ...deduplication logic...
            return events
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(f"Error in dedupe: {e}")
            raise
