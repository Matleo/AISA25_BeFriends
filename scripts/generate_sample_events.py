"""
Script to generate and upsert sample events into the persistent catalog.
Run this to populate the SQLite DB for validation/testing.
"""
from befriends.domain.event import Event
from befriends.catalog.repository import CatalogRepository
from datetime import datetime, timedelta

repo = CatalogRepository()

sample_events = [
    Event(
        id=f"evt_{i}",
        name=f"Sample Event {i}",
        description=f"This is a description for event {i}.",
        date=(datetime.now() + timedelta(days=i)).date(),
        city="Berlin" if i % 2 == 0 else "Munich",
        region="Berlin" if i % 2 == 0 else "Bavaria",
        category="Music" if i % 2 == 0 else "Art",
        tags=["fun", "social"] if i % 2 == 0 else ["culture", "exhibition"],
        price=str(10 + i),
        venue=f"Venue {i}",
        time_text="19:00" if i % 2 == 0 else "18:00",
        location=f"Location {i}",
        source_id=f"src_{i}",
        ingested_at=datetime.now()
    )
    for i in range(1, 6)
]

inserted = repo.upsert(sample_events)
print(f"Inserted {inserted} sample events.")
