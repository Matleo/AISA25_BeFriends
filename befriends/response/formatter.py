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
            time = getattr(event, 'time_text', None) or (event.get('time_text') if isinstance(event, dict) else None)
            location = getattr(event, 'location', None) or (event.get('location') if isinstance(event, dict) else None)
            instagram = getattr(event, 'instagram', None) if hasattr(event, 'instagram') else (event.get('instagram') if isinstance(event, dict) else None)
            date_str = str(getattr(event, 'date', None) or (event.get('date') if isinstance(event, dict) else ''))
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
            line = f"{i}. {getattr(event, 'name', event.get('name', ''))} ({date_with_weekday}, {getattr(event, 'city', event.get('city', 'n/a'))}, {getattr(event, 'category', event.get('category', 'n/a'))})"
            if time:
                line += f" at {time}"
            if location:
                line += f" | {location}"
            if instagram:
                handle = instagram.lstrip('@')
                url = f"https://instagram.com/{handle}"
                line += f" | IG: [{instagram}]({url})"
            lines.append(line)
            desc = getattr(event, 'description', None) or (event.get('description') if isinstance(event, dict) else None)
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
            time = getattr(e, 'time_text', None) or (e.get('time_text') if isinstance(e, dict) else None)
            location = getattr(e, 'location', None) or (e.get('location') if isinstance(e, dict) else None)
            instagram = getattr(e, 'instagram', None) if hasattr(e, 'instagram') else (e.get('instagram') if isinstance(e, dict) else None)
            date_str = str(getattr(e, 'date', None) or (e.get('date') if isinstance(e, dict) else ''))
            try:
                import datetime
                date_obj = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d")
                weekday = date_obj.strftime("%A")
                date_with_weekday = f"{date_str} ({weekday})"
            except Exception:
                date_with_weekday = date_str
            line = f"- {getattr(e, 'name', e.get('name', ''))} ({date_with_weekday}, {getattr(e, 'city', e.get('city', 'n/a'))}, {getattr(e, 'category', e.get('category', 'n/a'))})"
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
