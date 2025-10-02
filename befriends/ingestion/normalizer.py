"""Normalizer for raw event data."""

from __future__ import annotations

import logging

from ..domain.event import Event


class Normalizer:
    """Normalizes raw event dicts into Event entities."""

    def normalize(self, raw: dict) -> Event:
        """Convert a raw dict to an Event using the new event schema."""
        from datetime import datetime, date as dt_date
        try:
            # Parse start_datetime
            raw_start = raw.get("start_datetime")
            if isinstance(raw_start, str):
                try:
                    start_datetime = datetime.fromisoformat(raw_start)
                except Exception:
                    start_datetime = datetime.now()
            elif isinstance(raw_start, dt_date):
                start_datetime = raw_start
            elif isinstance(raw_start, datetime):
                start_datetime = raw_start
            else:
                start_datetime = datetime.now()

            # Parse end_datetime
            raw_end = raw.get("end_datetime")
            if isinstance(raw_end, str):
                try:
                    end_datetime = datetime.fromisoformat(raw_end)
                except Exception:
                    end_datetime = None
            elif isinstance(raw_end, datetime):
                end_datetime = raw_end
            else:
                end_datetime = None

            # Parse dance_style (should be a list)
            dance_style = raw.get("dance_style")
            if isinstance(dance_style, str):
                dance_style = [dance_style]
            elif dance_style is None:
                dance_style = []

            return Event(
                id=raw.get("id"),
                event_name=raw.get("event_name", ""),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                recurrence_rule=raw.get("recurrence_rule"),
                date_description=raw.get("date_description"),
                event_type=raw.get("event_type"),
                dance_focus=raw.get("dance_focus"),
                dance_style=dance_style,
                price_min=raw.get("price_min"),
                price_max=raw.get("price_max"),
                currency=raw.get("currency"),
                pricing_type=raw.get("pricing_type"),
                price_category=raw.get("price_category"),
                audience_min=raw.get("audience_min"),
                audience_max=raw.get("audience_max"),
                audience_size_bucket=raw.get("audience_size_bucket"),
                age_min=raw.get("age_min"),
                age_max=raw.get("age_max"),
                age_group_label=raw.get("age_group_label"),
                user_category=raw.get("user_category"),
                event_location=raw.get("event_location"),
                region=raw.get("region"),
                season=raw.get("season"),
                cross_border_potential=raw.get("cross_border_potential"),
                organizer=raw.get("organizer"),
                instagram=raw.get("instagram"),
                event_link=raw.get("event_link"),
                event_link_fit=raw.get("event_link_fit"),
                description=raw.get("description"),
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
