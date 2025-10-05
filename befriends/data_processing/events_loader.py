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
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None

# Add missing parse_dance_style, parse_float, parse_int if not present
def parse_dance_style(style):
    if not style:
        return []
    if isinstance(style, list):
        return style
    return [s.strip() for s in style.split(",") if s.strip()]

def parse_float(val):
    try:
        return float(val) if val not in (None, "") else None
    except Exception:
        return None

def parse_int(val):
    try:
        return int(val) if val not in (None, "") else None
    except Exception:
        return None

def load_events_from_csv(csv_path: str) -> List[Event]:
    events = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ingested_at_val = parse_datetime(row.get("ingested_at"))
            if ingested_at_val is None:
                from datetime import datetime
                ingested_at_val = datetime.now()
            event = Event(
                id=row.get("id"),
                event_name=row.get("event_name", ""),
                start_datetime=parse_datetime(row.get("start_datetime")),
                end_datetime=parse_datetime(row.get("end_datetime")),
                recurrence_rule=row.get("recurrence_rule"),
                date_description=row.get("date_description"),
                event_type=row.get("event_type"),
                dance_focus=row.get("dance_focus"),
                dance_style=parse_dance_style(row.get("dance_style")),
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
                user_category=row.get("user_category"),
                event_location=row.get("event_location"),
                region=row.get("region"),
                region_standardized=row.get("region_standardized"),
                season=row.get("season"),
                cross_border_potential=row.get("cross_border_potential"),
                organizer=row.get("organizer"),
                instagram=row.get("instagram"),
                event_link=row.get("event_link"),
                event_link_fit=row.get("event_link_fit"),
                description=row.get("description"),
                ingested_at=ingested_at_val,
                event_date=row.get("event_date"),
                event_time=row.get("event_time"),
                weekday=row.get("weekday"),
                month=row.get("month"),
                country=row.get("country"),
                city=row.get("city"),
                latitude=parse_float(row.get("latitude")),
                longitude=parse_float(row.get("longitude")),
            )
            events.append(event)
    return events
