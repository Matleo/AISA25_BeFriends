"""
Data processing module for event ingestion and normalization (new schema).
"""
import csv
from datetime import datetime
from typing import List, Optional
from befriends.domain.event import Event

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        # Accepts ISO 8601 or 'YYYY-MM-DD HH:MM' format
        return datetime.fromisoformat(dt_str)
    except Exception:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except Exception:
            return None

def parse_float(val: Optional[str]) -> Optional[float]:
    try:
        return float(val) if val not in (None, "", "NA") else None
    except Exception:
        return None

def parse_int(val: Optional[str]) -> Optional[int]:
    try:
        return int(val) if val not in (None, "", "NA") else None
    except Exception:
        return None

def cleanse_event_row(row: dict) -> dict:
    """Standardize and clean a single event row dict for the new schema."""
    cleaned = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
    for k, v in cleaned.items():
        if isinstance(v, str) and v == "":
            cleaned[k] = None
    return cleaned

def load_events_from_csv(csv_path: str) -> List[Event]:
    """Load and parse events from a CSV file using the new schema."""
    events = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, 1):
            row = cleanse_event_row(row)
            event = Event(
                id=None,
                event_name=row.get("event-name"),
                start_datetime=parse_datetime(row.get("start_datetime")),
                end_datetime=parse_datetime(row.get("end_datetime")),
                recurrence_rule=row.get("recurrence_rule"),
                date_description=row.get("date_description"),
                event_type=row.get("event-type"),
                dance_focus=row.get("dance_focus"),
                dance_style=row.get("dance_style"),
                price_min=parse_float(row.get("price_min")),
                price_max=parse_float(row.get("price_max")),
                currency=row.get("currency"),
                pricing_type=row.get("pricing_type"),
                price_category=row.get("price_category"),
                audience_min=parse_int(row.get("audience_min")),
                audience_max=parse_int(row.get("audience_max")),
                audience_size_bucket=row.get("audience_size_bucket"),
                age_min=parse_int(row.get("age_min")),
                age_max=parse_int(row.get("age_max")),
                age_group_label=row.get("age_group_label"),
                user_category=row.get("user-category"),
                event_location=row.get("event-location"),
                region=row.get("region"),
                season=row.get("season"),
                cross_border_potential=row.get("cross_border_potential"),
                organizer=row.get("organizer"),
                instagram=row.get("instagram"),
                ingested_at=datetime.now(),
            )
            events.append(event)
    return events
