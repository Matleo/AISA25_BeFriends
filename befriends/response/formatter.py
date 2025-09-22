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
            time = getattr(event, 'start_datetime', None)
            location = getattr(event, 'event_location', None)
            instagram = getattr(event, 'instagram', None)
            date_str = str(event.start_datetime.date()) if event.start_datetime else "n/a"
            if with_weekday and event.start_datetime:
                try:
                    weekday = event.start_datetime.strftime("%A")
                    date_with_weekday = f"{date_str} ({weekday})"
                except Exception:
                    date_with_weekday = date_str
            else:
                date_with_weekday = date_str
            name = getattr(event, 'event_name', '')
            region = getattr(event, 'region', 'n/a')
            event_type = getattr(event, 'event_type', 'n/a')
            line = f"{i}. {name} ({date_with_weekday}, {region}, {event_type})"
            if time:
                line += f" at {time.strftime('%H:%M') if hasattr(time, 'strftime') else time}"
            if location:
                line += f" | {location}"
            if instagram:
                handle = instagram.lstrip('@')
                url = f"https://instagram.com/{handle}"
                line += f" | IG: [{instagram}]({url})"
            lines.append(line)
            desc = getattr(event, 'date_description', None)
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
            time = getattr(e, 'start_datetime', None)
            location = getattr(e, 'event_location', None)
            instagram = getattr(e, 'instagram', None)
            date_str = str(e.start_datetime.date()) if e.start_datetime else "n/a"
            if e.start_datetime:
                try:
                    weekday = e.start_datetime.strftime("%A")
                    date_with_weekday = f"{date_str} ({weekday})"
                except Exception:
                    date_with_weekday = date_str
            else:
                date_with_weekday = date_str
            name = getattr(e, 'event_name', '')
            region = getattr(e, 'region', 'n/a')
            event_type = getattr(e, 'event_type', 'n/a')
            line = f"- {name} ({date_with_weekday}, {region}, {event_type})"
            if time:
                line += f" at {time.strftime('%H:%M') if hasattr(time, 'strftime') else time}"
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
            if event.price_min is not None or event.price_max is not None:
                summary += f" (Price: {event.price_min} - {event.price_max} {event.currency or ''})"
            if event.dance_style:
                summary += f" Style: {event.dance_style}"
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
                "title": event.event_name,
                "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
                "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
                "event_type": event.event_type,
                "dance_style": event.dance_style,
                "price_min": event.price_min,
                "price_max": event.price_max,
                "currency": event.currency,
                "region": event.region,
                "event_location": event.event_location,
                "organizer": event.organizer,
                "instagram": getattr(event, "instagram", None),
                "description": event.date_description,
            }
            cards.append(card)
        return cards
