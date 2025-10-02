"""Ranking policy for search results."""

from __future__ import annotations
from ..domain.event import Event
from ..domain.search_models import SearchQuery


class RelevancePolicy:
    """Ranks events for search results."""

    def rank(self, events: list[Event], query: SearchQuery) -> list[Event]:
        """
        Rank events by recency, keyword/category/tag match,
        price proximity, and filter match.
        """
        def score(event: Event) -> float:
            s = 0.0
            from datetime import datetime, date as dt_date
            today = datetime.now().date()
            # Recency: prioritize future events, then most recent
            if hasattr(event, "start_datetime") and event.start_datetime is not None:
                event_date = event.start_datetime.date() if isinstance(event.start_datetime, datetime) else event.start_datetime
                if event_date >= today:
                    s -= (event_date - today).days * 0.5  # future events: less penalty
                else:
                    s += (today - event_date).days * 2  # past events: strong penalty
            # Keyword in event_name/event_type/date_description/dance_style
            text = (query.text or "").lower()
            if text:
                if text in (event.event_name or "").lower():
                    s -= 20
                if text in (event.event_type or "").lower():
                    s -= 10
                if text in (event.date_description or "").lower():
                    s -= 5
                # Fix: handle dance_style as list or string
                if isinstance(event.dance_style, list):
                    if any(text in (ds or "").lower() for ds in event.dance_style):
                        s -= 5
                elif isinstance(event.dance_style, str):
                    if text in event.dance_style.lower():
                        s -= 5
            # Event type exact match
            if (
                hasattr(query, "event_type")
                and query.event_type
                and event.event_type
                and query.event_type.lower() == event.event_type.lower()
            ):
                s -= 5
            # Dance style match
            if hasattr(query, "dance_style") and query.dance_style and event.dance_style:
                q_style = query.dance_style.lower() if isinstance(query.dance_style, str) else query.dance_style
                if isinstance(event.dance_style, list):
                    if any(q_style in (ds or "").lower() for ds in event.dance_style):
                        s -= 3
                elif isinstance(event.dance_style, str):
                    if q_style in event.dance_style.lower():
                        s -= 3
            # Price proximity (if price filter used)
            if (hasattr(query, "price_min") or hasattr(query, "price_max")) and (event.price_min is not None or event.price_max is not None):
                try:
                    price_val = float(event.price_min) if event.price_min is not None else float(event.price_max)
                    if hasattr(query, "price_min") and query.price_min:
                        s += abs(price_val - query.price_min)
                    if hasattr(query, "price_max") and query.price_max:
                        s += abs(price_val - query.price_max)
                except Exception:
                    pass
            # Date range filter match
            if hasattr(query, "start_datetime_from") and query.start_datetime_from and event.start_datetime and event.start_datetime < query.start_datetime_from:
                s += 10
            if hasattr(query, "start_datetime_to") and query.start_datetime_to and event.start_datetime and event.start_datetime > query.start_datetime_to:
                s += 10
            return s  # Lower score = higher rank
        return sorted(events, key=score)
