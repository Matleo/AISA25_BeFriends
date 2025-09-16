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
            # Recency: prioritize future events, then most recent
            from datetime import date as dt_date

            today = dt_date.today()
            if hasattr(event, "date") and event.date:
                if event.date >= today:
                    s -= (event.date - today).days * 0.5  # future events: less penalty
                else:
                    s += (today - event.date).days * 2  # past events: strong penalty
            # Keyword in name/category/description/tags
            text = (query.text or "").lower()
            if text:
                if text in (event.name or "").lower():
                    s -= 20
                if text in (event.category or "").lower():
                    s -= 10
                if text in (event.description or "").lower():
                    s -= 5
                if event.tags and any(text in (t or "").lower() for t in event.tags):
                    s -= 5
            # Category exact match
            if (
                query.category
                and event.category
                and query.category.lower() == event.category.lower()
            ):
                s -= 5
            # Tag match
            if query.tags and event.tags:
                for tag in query.tags:
                    if any(tag.lower() in (t or "").lower() for t in event.tags):
                        s -= 3
            # Price proximity (if price filter used)
            if (query.price_min or query.price_max) and event.price:
                try:
                    price_val = float(str(event.price).split()[0].replace(",", "."))
                    if query.price_min:
                        s += abs(price_val - query.price_min)
                    if query.price_max:
                        s += abs(price_val - query.price_max)
                except Exception:
                    pass
            # Date range filter match
            if query.date_from and event.date and event.date < query.date_from:
                s += 10
            if query.date_to and event.date and event.date > query.date_to:
                s += 10
            return s  # Lower score = higher rank
        return sorted(events, key=score)
