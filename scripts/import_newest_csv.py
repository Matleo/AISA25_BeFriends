"""
Script to import the newest CSV file from the data folder into the persistent catalog.
"""

import os
import glob
from datetime import datetime
from befriends.domain.event import Event
from befriends.catalog.repository import CatalogRepository
import csv

def get_newest_csv(data_dir):
    files = glob.glob(os.path.join(data_dir, '*.csv'))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def parse_date(dt_str):
    # Try to parse as ISO, fallback to today, ignore non-date strings
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M").date()
    except Exception:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d").date()
        except Exception:
            return datetime.today().date()

def clean_str(val):
    if val is None:
        return None
    return str(val).strip()

def normalize_price(price):
    if not price:
        return None
    # Extract numeric part, keep currency if present
    import re
    match = re.search(r"([0-9]+([.,][0-9]+)?)([^0-9]*)", price)
    if match:
        num = match.group(1).replace(",", ".")
        cur = match.group(3).strip()
        return f"{num} {cur}".strip()
    return price.strip()

def deduplicate(events):
    seen = set()
    unique = []
    for e in events:
        key = (clean_str(e.name).lower() if e.name else None, e.date, clean_str(e.location).lower() if e.location else None)
        if key in seen:
            continue
        seen.add(key)
        unique.append(e)
    return unique

def geocode_city(city):
    # Stub for geolocation enrichment (could call an API)
    return None

def csv_to_event(row, idx):
    # Validate required fields
    name = clean_str(row.get("event-name"))
    date_val = parse_date(row.get("event-datetime", ""))
    if not name or not date_val:
        return None
    # Clean and normalize fields
    location = clean_str(row.get("event-location"))
    description = f"{clean_str(row.get('event-type'))} | {clean_str(row.get('organizer'))}"
    city = clean_str(row.get("region"))
    category = clean_str(row.get("event-type"))
    tags = [clean_str(row.get("dance_style"))] if row.get("dance_style") else None
    price = normalize_price(row.get("price"))
    # Enrichment stub: geocode_city(city)
    return Event(
        id=f"csv_{idx}",
        name=name,
        date=date_val,
        time_text=row.get("event-datetime", "").split(" ")[1] if " " in row.get("event-datetime", "") else None,
        location=location,
        description=description,
        city=city,
        region=city,
        source_id=clean_str(row.get("organizer")),
        ingested_at=datetime.now(),
        category=category,
        tags=tags,
        price=price,
        venue=location
    )

def import_newest_csv():
    data_dir = os.path.join(os.path.dirname(__file__), '../befriends/data')
    newest_csv = get_newest_csv(data_dir)
    if not newest_csv:
        print("No CSV files found.")
        return
    print(f"Importing {newest_csv}")
    repo = CatalogRepository()
    events = []
    with open(newest_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            event = csv_to_event(row, idx)
            if event:
                events.append(event)
            else:
                print(f"Skipped row {idx+1}: missing required fields or invalid data.")
    events = deduplicate(events)
    inserted = repo.upsert(events)
    print(f"Inserted {inserted} unique events from {os.path.basename(newest_csv)}.")

if __name__ == "__main__":
    import_newest_csv()
