"""
Script to ingest events from dreilaendereck_events_enriched.csv into the persistent catalog.
Maps CSV columns to Event dataclass fields as best as possible.
"""
import csv
from datetime import datetime, date
from befriends.domain.event import Event
from befriends.catalog.repository import CatalogRepository
import os

file_path = '../befriends/data/dreilaendereck_events_enriched.csv'
CSV_PATH = os.path.join(os.path.dirname(__file__), file_path)
repo = CatalogRepository()


def parse_date(dt_str):
    # Try to parse as ISO, else fallback to today
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M").date()
    except Exception:
        return date.today()


def csv_to_event(row, idx):
    event_dt = row.get("event-datetime", "")
    time_text = event_dt.split(" ")[1] if " " in event_dt else None
    return Event(
        id=f"csv_{idx}",
        name=row.get("event-name"),
        date=parse_date(event_dt),
        time_text=time_text,
        location=row.get("event-location"),
        description=f"{row.get('event-type', '')} | {row.get('organizer', '')}",
        city=row.get("region"),
        region=row.get("region"),
        source_id=row.get("organizer"),
        ingested_at=datetime.now(),
        category=row.get("event-type"),
        tags=[row.get("dance_style")] if row.get("dance_style") else None,
        price=row.get("price"),
        venue=row.get("event-location")
    )


events = []
with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader):
        events.append(csv_to_event(row, idx))

inserted = repo.upsert(events)
print(f"Inserted {inserted} events from CSV.")
