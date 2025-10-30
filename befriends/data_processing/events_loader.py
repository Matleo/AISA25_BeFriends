"""
Data processing module for event ingestion and normalization (new schema).
"""
import csv

import logging
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
        expected_fields = [
            "event_name", "start_datetime", "end_datetime", "recurrence_rule", "date_description", "event_type", "dance_focus", "dance_style", "price_min", "price_max", "currency", "pricing_type", "price_category", "audience_min", "audience_max", "audience_size_bucket", "age_min", "age_max", "age_group_label", "user_category", "event_location", "region", "region_standardized", "season", "cross_border_potential", "organizer", "instagram", "event_link", "event_link_fit", "description", "ingested_at", "event_date", "event_time", "weekday", "month", "country", "city", "latitude", "longitude"
        ]
        for row in reader:
            ingested_at_val = parse_datetime(row.get("ingested_at"))
            if ingested_at_val is None:
                row["ingested_at"] = datetime.now()
            # Check for missing/unmapped fields
            for field in expected_fields:
                if field not in row and field.replace("_", "-") not in row:
                    logging.warning(f"[CSV Loader] Missing or unmapped field: '{field}' in row: {row}")
            
            price_min = parse_float(row.get("price_min") or row.get("price-min"))
            price_max = parse_float(row.get("price_max") or row.get("price-max"))
            if price_min is None:
                price_min = 0.0
            if price_max is None:
                price_max = 0.0
            event = Event(
                id=row.get("id"),
                event_name=row.get("event_name") or row.get("event-name") or "",
                start_datetime=parse_datetime(row.get("start_datetime") or row.get("start-datetime")),
                end_datetime=parse_datetime(row.get("end_datetime") or row.get("end-datetime")),
                recurrence_rule=row.get("recurrence_rule") or row.get("recurrence-rule"),
                date_description=row.get("date_description") or row.get("date-description"),
                event_type=row.get("event_type") or row.get("event-type"),
                dance_focus=row.get("dance_focus") or row.get("dance-focus"),
                dance_style=parse_dance_style(row.get("dance_style") or row.get("dance-style")),
                price_min=price_min,
                price_max=price_max,
                currency=row.get("currency"),
                pricing_type=row.get("pricing_type") or row.get("pricing-type"),
                price_category=row.get("price_category") or row.get("price-category"),
                audience_min=parse_int(row.get("audience_min") or row.get("audience-min")),
                audience_max=parse_int(row.get("audience_max") or row.get("audience-max")),
                audience_size_bucket=row.get("audience_size_bucket") or row.get("audience-size-bucket"),
                age_min=parse_int(row.get("age_min") or row.get("age-min")),
                age_max=parse_int(row.get("age_max") or row.get("age-max")),
                age_group_label=row.get("age_group_label") or row.get("age-group-label"),
                user_category=row.get("user_category") or row.get("user-category"),
                event_location=row.get("event_location") or row.get("event-location"),
                region=row.get("region"),
                region_standardized=row.get("region_standardized") or row.get("region-standardized"),
                season=row.get("season"),
                cross_border_potential=row.get("cross_border_potential") or row.get("cross-border-potential"),
                organizer=row.get("organizer"),
                instagram=row.get("instagram"),
                event_link=row.get("event_link") or row.get("event-link"),
                event_link_fit=row.get("event_link_fit") or row.get("event-link-fit"),
                description=row.get("description"),
                ingested_at=row.get("ingested_at"),
                event_date=row.get("event_date") or row.get("event-date"),
                event_time=row.get("event_time") or row.get("event-time"),
                weekday=row.get("weekday"),
                month=row.get("month"),
                country=row.get("country"),
                city=row.get("city"),
                latitude=parse_float(row.get("latitude")),
                longitude=parse_float(row.get("longitude")),
            )
            events.append(event)
        return events
