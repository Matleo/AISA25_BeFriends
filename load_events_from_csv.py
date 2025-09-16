import csv
from datetime import datetime, date
from befriends.domain.event import Event
from befriends.catalog.repository import CatalogRepository

CSV_PATH = "befriends/data/06_events.csv"
DB_URL = "sqlite:///events.db"  # Change if you want a different DB

def parse_date(dt_str):
    # Try to parse date or return None
    try:
        if dt_str and len(dt_str) >= 10:
            return datetime.strptime(dt_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None
    return None

def parse_datetime(dt_str):
    # Try to parse datetime or return now
    try:
        if dt_str and len(dt_str) >= 16:
            return datetime.strptime(dt_str[:16], "%Y-%m-%d %H:%M")
    except Exception:
        return datetime.now()
    return datetime.now()

def main():
    repo = CatalogRepository(DB_URL)
    events = []
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            event = Event(
                id=None,
                name=row.get("event-name"),
                date=parse_date(row.get("event-datetime")),
                time_text=row.get("event-datetime"),
                location=row.get("event-location"),
                description=row.get("event-type"),
                city=None,  # You can parse city from location if needed
                region=row.get("region"),
                source_id=None,
                ingested_at=datetime.now(),
                category=row.get("event-type"),
                tags=[t.strip() for t in (row.get("dance_style") or "").split("/") if t.strip()] or None,
                price=row.get("price"),
                venue=row.get("event-location"),
            )
            events.append(event)
    print(f"Upserting {len(events)} events...")
    repo.upsert(events)
    print("Done.")

if __name__ == "__main__":
    main()
