"""Formats search results for UI responses."""

from __future__ import annotations

from ..domain.search_models import SearchResult


class ResponseFormatter:
    """Formats search results as narratives and cards."""

    def to_narrative(self, result: SearchResult) -> str:
        """Return a narrative summary for the UI."""
        if not result.events:
            return "No events found."
        lines = [f"Found {result.total} event(s):"]
        for event in result.events[:5]:
            summary = event.to_summary()
            if event.price:
                summary += f" (Price: {event.price})"
            if event.tags:
                summary += f" Tags: {', '.join(event.tags)}"
            lines.append(summary)
        if result.total > 5:
            lines.append(f"...and {result.total - 5} more.")
        return "\n".join(lines)

    def to_cards(self, result: SearchResult) -> list[dict]:
        """Return card payloads for the UI."""
        cards = []
        for event in result.events:
            card = {
                "id": event.id,
                "title": event.name,
                "date": str(event.date),
                "time": event.time_text,
                "location": event.location,
                "city": event.city,
                "region": event.region,
                "category": event.category,
                "tags": event.tags,
                "price": event.price,
                "venue": event.venue,
                "description": event.description,
                "source_id": event.source_id,
                "instagram": getattr(event, "instagram", None),
            }
            cards.append(card)
        return cards
