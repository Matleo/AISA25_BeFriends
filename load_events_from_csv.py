import os
from befriends.catalog.repository import CatalogRepository
from befriends.data_processing.events_loader import load_events_from_csv

CSV_PATH = "befriends/data/08_events.csv"
DB_URL = "sqlite:///events.db"

def import_events_from_csv(csv_path=CSV_PATH, db_url=DB_URL, verbose=True):
    # Always delete the current DB to ensure a fresh schema
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        if os.path.exists(db_path):
            os.remove(db_path)
    repo = CatalogRepository(db_url)
    events = load_events_from_csv(csv_path)
    count = repo.upsert(events)
    if verbose:
        print(f"Imported {count} events from {csv_path}")
    return {"imported": count, "errors": []}
