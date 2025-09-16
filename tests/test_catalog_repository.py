import pytest
from befriends.catalog.repository import CatalogRepository
from befriends.domain.event import Event
from datetime import date, datetime, timedelta


@pytest.fixture
def repo():
    return CatalogRepository()


def sample_event():
    """Factory for a sample Event object for tests."""
    return Event(
        id="1",
        name="Sample Event",
        date=date.today(),
        time_text=None,
        location=None,
        description=None,
        city=None,
        region=None,
        source_id=None,
        ingested_at=datetime.now()
    )


def test_upsert_duplicate_id_overwrites(repo):
    event1 = sample_event()
    event2 = sample_event()
    event2 = event2.__class__(**{**event2.__dict__, "id": "dup1", "name": "B"})
    event1 = event1.__class__(**{**event1.__dict__, "id": "dup1", "name": "A"})
    repo.upsert([event1])
    repo.upsert([event2])
    found = repo.find_by_id("dup1")
    assert found.name == "B"


def test_search_text_with_filters(repo):
    # Insert multiple events with different cities and categories
    base_event = sample_event()
    events = []
    for i in range(6):
        event = base_event.__class__(**{
            **base_event.__dict__,
            "id": f"filt_{i}",
            "name": f"Event {i}",
            "date": base_event.date + timedelta(days=i),
            "city": "Berlin" if i % 2 == 0 else "Munich",
            "category": "Music" if i % 2 == 0 else "Art"
        })
        events.append(event)
    repo.upsert(events)
    # Search for Berlin Music events
    results = repo.search_text("music", filters={"city": "Berlin"})
    assert all(
        e.city == "Berlin" and (e.category or "").lower() == "music"
        for e in results
    )
    # Search for Art events in Munich
    results = repo.search_text("art", filters={"city": "Munich"})
    assert all(
        e.city == "Munich" and (e.category or "").lower() == "art"
        for e in results
    )


def test_upsert_and_list_recent(repo):
    event = sample_event()
    count = repo.upsert([event])
    assert isinstance(count, int)
    events = repo.list_recent()
    assert isinstance(events, list)


def test_find_by_id_none(repo):
    event = repo.find_by_id("nonexistent")
    assert event is None


def test_search_text_empty(repo):
    events = repo.search_text("anything")
    assert isinstance(events, list)
