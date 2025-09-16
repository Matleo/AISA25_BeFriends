"""Normalizer for raw event data."""

from __future__ import annotations

import logging

from ..domain.event import Event


class Normalizer:
    """Normalizes raw event dicts into Event entities."""

    def normalize(self, raw: dict) -> Event:
        """Convert a raw dict to an Event."""
        from datetime import datetime, date as dt_date
        try:
            # ...map fields, clean data...
            raw_date = raw.get("date")
            if isinstance(raw_date, str):
                try:
                    event_date = dt_date.fromisoformat(raw_date)
                except Exception:
                    event_date = dt_date.today()
            elif isinstance(raw_date, dt_date):
                event_date = raw_date
            else:
                event_date = dt_date.today()
            return Event(
                id=None,
                name=raw.get("name", ""),
                date=event_date,
                time_text=None,
                location=None,
                description=None,
                city=None,
                region=None,
                source_id=None,
                ingested_at=raw.get("ingested_at") or datetime.now(),
            )
        except Exception as e:
            import logging
            logging.getLogger(self.__class__.__name__).error(
                f"Error normalizing event: {e}"
            )
            raise

    def normalize_batch(self, raw_list: list[dict]) -> list[Event]:
        """Normalize a batch of raw dicts."""
        try:
            # ...batch normalization...
            return [self.normalize(raw) for raw in raw_list]
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(
                f"Error in batch normalization: {e}"
            )
            raise
