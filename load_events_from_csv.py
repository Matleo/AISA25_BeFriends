import csv
import os
from datetime import datetime
from befriends.domain.event import Event
from befriends.catalog.repository import CatalogRepository

CSV_PATH = "befriends/data/06_events.csv"
DB_URL = "sqlite:///events.db"


def parse_date(dt_str):
    try:
        if dt_str and len(dt_str) >= 10:
            return datetime.strptime(dt_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None
    return None


def parse_datetime(dt_str):
    try:
        if dt_str and len(dt_str) >= 16:
            return datetime.strptime(dt_str[:16], "%Y-%m-%d %H:%M")
    except Exception:
        return datetime.now()
    return datetime.now()


def import_events_from_csv(csv_path=CSV_PATH, db_url=DB_URL, validate=True, verbose=True):
    # Always delete the current DB to ensure a fresh schema
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        if os.path.exists(db_path):
            os.remove(db_path)
    repo = CatalogRepository(db_url)
    events = []
    errors = []

    def cleanse_event_row(row: dict) -> dict:
        """Standardize and clean a single event row dict."""
        # Trim whitespace from all string fields
        cleaned = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        # Standardize city/region casing
        if cleaned.get("city"):
            cleaned["city"] = cleaned["city"].title()
        if cleaned.get("region"):
            cleaned["region"] = cleaned["region"].title()
        # Optionally, add more rules (e.g., replace empty strings with None)
        for k, v in cleaned.items():
            if isinstance(v, str) and v == "":
                cleaned[k] = None
        return cleaned
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, 1):
            # Require name and date
            row = cleanse_event_row(row)
            name = row.get("event-name") or None
            date_str = row.get("event-datetime") or None
            date_val = parse_date(date_str) if date_str else None
            if validate and (not name or not date_val):
                errors.append(f"Row {i}: Missing required field(s): name/date | Data: {row}")
                continue
            event = Event(
                id=None,
                name=name,
                date=date_val,
                time_text=row.get("event-datetime"),
                location=row.get("event-location"),
                description=row.get("event-type"),
                city=row.get("city"),
                region=row.get("region"),
                source_id=None,
                ingested_at=datetime.now(),
                category=row.get("event-type"),
                tags=[
                    t.strip() for t in (row.get("dance_style") or "").split("/")
                    if t.strip()
                ] or None,
                price=row.get("price"),
                venue=row.get("event-location"),
            )
            events.append(event)
    if verbose:
        print(f"Upserting {len(events)} events...")
    repo.upsert(events)
    if verbose:
        print("Done.")
        if errors:
            print("Validation errors:")
            for err in errors:
                print(err)
    return {"imported": len(events), "errors": errors}


if __name__ == "__main__":
    import_events_from_csv()
