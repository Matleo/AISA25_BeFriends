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
            # Fix: handle dicts and str dates robustly
            start_dt = getattr(event, 'start_datetime', None)
            if isinstance(event, dict):
                start_dt = event.get('start_datetime', None)
                if isinstance(start_dt, str):
                    try:
                        from datetime import datetime
                        start_dt = datetime.fromisoformat(start_dt)
                    except Exception:
                        pass
            time = start_dt
            date_str = str(start_dt.date()) if hasattr(start_dt, 'date') else str(start_dt) if start_dt else "n/a"
            if with_weekday and start_dt and hasattr(start_dt, 'strftime'):
                try:
                    weekday = start_dt.strftime("%A")
                    date_with_weekday = f"{date_str} ({weekday})"
                except Exception:
                    date_with_weekday = date_str
            else:
                date_with_weekday = date_str
            name = getattr(event, 'event_name', event.get('event_name', '')) if isinstance(event, dict) else getattr(event, 'event_name', '')
            region = getattr(event, 'region', event.get('region', 'n/a')) if isinstance(event, dict) else getattr(event, 'region', 'n/a')
            event_type = getattr(event, 'event_type', event.get('event_type', 'n/a')) if isinstance(event, dict) else getattr(event, 'event_type', 'n/a')
            line = f"{i}. {name} ({date_with_weekday}, {region}, {event_type})"
            if time and hasattr(time, 'strftime'):
                line += f" at {time.strftime('%H:%M')}"
            elif time:
                line += f" at {time}"
            location = getattr(event, 'event_location', event.get('event_location', None)) if isinstance(event, dict) else getattr(event, 'event_location', None)
            if location:
                line += f" | {location}"
            instagram = getattr(event, 'instagram', event.get('instagram', None)) if isinstance(event, dict) else getattr(event, 'instagram', None)
            if instagram:
                handle = instagram.lstrip('@')
                url = f"https://instagram.com/{handle}"
                line += f" | IG: [{instagram}]({url})"
            lines.append(line)
            desc = getattr(event, 'date_description', event.get('date_description', None)) if isinstance(event, dict) else getattr(event, 'date_description', None)
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
            start_dt = getattr(e, 'start_datetime', None)
            if isinstance(e, dict):
                start_dt = e.get('start_datetime', None)
                if isinstance(start_dt, str):
                    try:
                        from datetime import datetime
                        start_dt = datetime.fromisoformat(start_dt)
                    except Exception:
                        pass
            time = start_dt
            date_str = str(start_dt.date()) if hasattr(start_dt, 'date') else str(start_dt) if start_dt else "n/a"
            if start_dt and hasattr(start_dt, 'strftime'):
                try:
                    weekday = start_dt.strftime("%A")
                    date_with_weekday = f"{date_str} ({weekday})"
                except Exception:
                    date_with_weekday = date_str
            else:
                date_with_weekday = date_str
            name = getattr(e, 'event_name', e.get('event_name', '')) if isinstance(e, dict) else getattr(e, 'event_name', '')
            region = getattr(e, 'region', e.get('region', 'n/a')) if isinstance(e, dict) else getattr(e, 'region', 'n/a')
            event_type = getattr(e, 'event_type', e.get('event_type', 'n/a')) if isinstance(e, dict) else getattr(e, 'event_type', 'n/a')
            line = f"- {name} ({date_with_weekday}, {region}, {event_type})"
            if time and hasattr(time, 'strftime'):
                line += f" at {time.strftime('%H:%M')}"
            elif time:
                line += f" at {time}"
            location = getattr(e, 'event_location', e.get('event_location', None)) if isinstance(e, dict) else getattr(e, 'event_location', None)
            if location:
                line += f" | {location}"
            instagram = getattr(e, 'instagram', e.get('instagram', None)) if isinstance(e, dict) else getattr(e, 'instagram', None)
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
                # Fix: handle both list and string for dance_style
                if isinstance(event.dance_style, list):
                    summary += f" Style: {', '.join(event.dance_style)}"
                else:
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
                "tags": event.dance_style if isinstance(event.dance_style, list) else [event.dance_style] if event.dance_style else [],
                "price_min": event.price_min,
                "price_max": event.price_max,
                "currency": event.currency,
                "region": event.region,
                "event_location": event.event_location,
                "organizer": event.organizer,
                "instagram": getattr(event, "instagram", None),
                "description": event.description,
                "event_link": getattr(event, "event_link", None),
            }
            cards.append(card)
        return cards
