# Utility to format events as JSON for LLM context
import json
from typing import List
from befriends.domain.event import Event

def events_to_json(events: List[Event], max_events: int = 10) -> str:
    """Return a compact JSON string for a list of events for LLM context."""
    def event_to_dict(e: Event):
        return {
            "id": e.id,
            "name": e.name,
            "date": str(e.date),
            "city": e.city,
            "category": e.category,
            "description": e.description[:100] if e.description else None,
            "location": e.location,
            "tags": e.tags,
            "price": e.price,
        }
    return json.dumps([event_to_dict(e) for e in events[:max_events]], ensure_ascii=False)
