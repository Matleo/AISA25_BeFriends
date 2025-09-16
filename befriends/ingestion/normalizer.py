"""Normalizer for raw event data."""

from __future__ import annotations

import logging
from .base import SourceConnector
from ..domain.event import Event

class Normalizer:
    """Normalizes raw event dicts into Event entities."""

    def normalize(self, raw: dict) -> Event:
        """Convert a raw dict to an Event."""
        try:
            # ...map fields, clean data...
            return Event(
                id=None, name=raw.get("name", ""), date=raw.get("date"), time_text=None,
                location=None, description=None, city=None, region=None, source_id=None, ingested_at=None
            )
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(f"Error normalizing event: {e}")
            raise

    def normalize_batch(self, raw_list: list[dict]) -> list[Event]:
        """Normalize a batch of raw dicts."""
        try:
            # ...batch normalization...
            return [self.normalize(raw) for raw in raw_list]
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(f"Error in batch normalization: {e}")
            raise
