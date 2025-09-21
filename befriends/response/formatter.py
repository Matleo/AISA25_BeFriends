"""Formats search results for UI responses."""

from __future__ import annotations

from ..domain.search_models import SearchResult


class ResponseFormatter:

    def chat_event_list(self, events, with_weekday: bool = True) -> str:
        """
        Format a list of events for chat display.
        Args:
            events (list): List of event objects or dicts
            with_weekday (bool): Whether to include weekday in date
        Returns:
            str: Formatted event list for chat
        """
        lines = []
        for i, event in enumerate(events, 1):
            time = getattr(event, 'time_text', None)
            location = getattr(event, 'location', None)
            instagram = getattr(event, 'instagram', None)
            date_str = str(getattr(event, 'date', None))
            if with_weekday:
                try:
                    import datetime
                    date_obj = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d")
                    weekday = date_obj.strftime("%A")
                    date_with_weekday = f"{date_str} ({weekday})"
                except Exception:
                    date_with_weekday = date_str
            else:
                date_with_weekday = date_str
            name = getattr(event, 'name', '')
            city = getattr(event, 'city', 'n/a')
            category = getattr(event, 'category', 'n/a')
            line = f"{i}. {name} ({date_with_weekday}, {city}, {category})"
            if time:
                line += f" at {time}"
            if location:
                line += f" | {location}"
            if instagram:
                handle = instagram.lstrip('@')
                url = f"https://instagram.com/{handle}"
                line += f" | IG: [{instagram}]({url})"
            lines.append(line)
            desc = getattr(event, 'description', None)
            if desc:
                lines.append(f"   - {desc[:120]}{'...' if len(desc) > 120 else ''}")
        return "\n".join(lines)

    def chat_event_summary(self, events) -> str:
        """
        Format a short summary of upcoming events for chat.
        Args:
            events (list): List of event objects or dicts
        Returns:
            str: Summary string
        """
        if not events:
            return "(No events available)"
        lines = []
        for e in events:
            time = getattr(e, 'time_text', None)
            location = getattr(e, 'location', None)
            instagram = getattr(e, 'instagram', None)
            date_str = str(getattr(e, 'date', None))
            try:
                import datetime
                date_obj = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d")
                weekday = date_obj.strftime("%A")
                date_with_weekday = f"{date_str} ({weekday})"
            except Exception:
                date_with_weekday = date_str
            name = getattr(e, 'name', '')
            city = getattr(e, 'city', 'n/a')
            category = getattr(e, 'category', 'n/a')
            line = f"- {name} ({date_with_weekday}, {city}, {category})"
            if time:
                line += f" at {time}"
            if location:
                line += f" | {location}"
            if instagram:
                handle = instagram.lstrip('@')
                url = f"https://instagram.com/{handle}"
                line += f" | IG: [{instagram}]({url})"
            lines.append(line)
        return "Upcoming events include:\n" + "\n".join(lines)
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
