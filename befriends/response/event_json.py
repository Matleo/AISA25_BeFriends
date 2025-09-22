# Utility to format events as JSON for LLM context
import json
from typing import List
from befriends.domain.event import Event

def events_to_json(events: List[Event], max_events: int = 10) -> str:
    """Return a compact JSON string for a list of events for LLM context (new schema)."""
    def event_to_dict(e: Event):
        return {
            "id": e.id,
            "event_name": e.event_name,
            "start_datetime": e.start_datetime.isoformat() if e.start_datetime else None,
            "end_datetime": e.end_datetime.isoformat() if e.end_datetime else None,
            "recurrence_rule": e.recurrence_rule,
            "date_description": e.date_description,
            "event_type": e.event_type,
            "dance_focus": e.dance_focus,
            "dance_style": e.dance_style,
            "price_min": e.price_min,
            "price_max": e.price_max,
            "currency": e.currency,
            "pricing_type": e.pricing_type,
            "price_category": e.price_category,
            "audience_min": e.audience_min,
            "audience_max": e.audience_max,
            "audience_size_bucket": e.audience_size_bucket,
            "age_min": e.age_min,
            "age_max": e.age_max,
            "age_group_label": e.age_group_label,
            "user_category": e.user_category,
            "event_location": e.event_location,
            "region": e.region,
            "season": e.season,
            "cross_border_potential": e.cross_border_potential,
            "organizer": e.organizer,
            "instagram": e.instagram,
        }
    return json.dumps([event_to_dict(e) for e in events[:max_events]], ensure_ascii=False)
