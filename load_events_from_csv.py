


import os
import glob
import logging
from befriends.catalog.repository import CatalogRepository
from befriends.catalog.orm import get_engine_and_session, Base
from befriends.catalog.orm import EventORM  # Ensure EventORM is registered
from befriends.data_processing.events_loader import load_events_from_csv

def get_latest_csv_path():
    csv_files = glob.glob("befriends/data/events/*_events.csv")
    if not csv_files:
        return None
    # Extract number prefix from filename, e.g. '12_events.csv' -> 12
    def extract_number(f):
        base = os.path.basename(f)
        try:
            return int(base.split("_")[0])
        except Exception:
            return -1
    csv_files.sort(key=extract_number, reverse=True)
    return csv_files[0]

CSV_PATH = get_latest_csv_path() or "befriends/data/events/12_events.csv"
DB_URL = "sqlite:///events.db"

def import_events_from_csv(csv_path=CSV_PATH, db_url=DB_URL, verbose=True):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger("load_events_from_csv")
    # Always delete the current DB to ensure a fresh schema
    try:
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            if os.path.exists(db_path):
                logger.info(f"Removing existing DB at {db_path}")
                os.remove(db_path)
        logger.info("Creating database tables if needed...")
        engine, _ = get_engine_and_session(db_url)
        logger.info(f"Engine created: {engine}")
        # Explicitly check EventORM is registered
        logger.info(f"Base.metadata.tables: {list(Base.metadata.tables.keys())}")
        if 'events' not in Base.metadata.tables:
            logger.error("EventORM not registered in Base.metadata.tables!")
        else:
            logger.info("EventORM is registered in Base.metadata.tables.")
        Base.metadata.create_all(engine)
        logger.info("Base.metadata.create_all(engine) called successfully.")
        repo = CatalogRepository(db_url)
        logger.info(f"CatalogRepository initialized: {repo}")
        logger.info(f"Loading events from CSV: {csv_path}")
        events = load_events_from_csv(csv_path)
        logger.info(f"Loaded {len(events)} events from CSV.")
        # Filter out regions with less than 10 entries
        from collections import Counter
        region_counts = Counter([e.region_standardized for e in events if e.region_standardized])
        valid_regions = {region for region, count in region_counts.items() if count >= 10}
        filtered_events = [e for e in events if e.region_standardized in valid_regions]
        logger.info(f"Filtered events: {len(filtered_events)} remain after removing regions with <10 entries.")
        count = repo.upsert(filtered_events)
        logger.info(f"Upserted {count} events into DB.")
        if verbose:
            print(f"Imported {count} events from {csv_path}")
        return {"imported": count, "errors": []}
    except Exception as e:
        logger.error(f"Exception during import: {e}", exc_info=True)
        if verbose:
            print(f"Import failed: {e}")
        return {"imported": 0, "errors": [str(e)]}

if __name__ == "__main__":
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH
    import_events_from_csv(csv_path=csv_path, db_url=DB_URL, verbose=True)
