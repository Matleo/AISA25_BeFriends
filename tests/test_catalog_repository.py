import pytest
from befriends.catalog.repository import CatalogRepository
from befriends.domain.event import Event
from datetime import date, datetime, timedelta


@pytest.fixture
def repo():
    return CatalogRepository()


def sample_event():
    """Factory for a sample Event object for tests."""
    from datetime import datetime
    return Event(
        id="1",
        event_name="Sample Event",
        start_datetime=datetime(2025, 10, 1, 20, 0),
        end_datetime=None,
        recurrence_rule=None,
        date_description=None,
        event_type=None,
        dance_focus=None,
        dance_style=None,
        price_min=None,
        price_max=None,
        currency=None,
        pricing_type=None,
        price_category=None,
        audience_min=None,
        audience_max=None,
        audience_size_bucket=None,
        age_min=None,
        age_max=None,
        age_group_label=None,
        user_category=None,
        event_location=None,
        region=None,
        season=None,
        cross_border_potential=None,
        organizer=None,
        instagram=None,
        event_link=None,
        event_link_fit=None,
        description=None,
        ingested_at=datetime.now()
    )


def test_upsert_duplicate_id_overwrites(repo):
    event1 = sample_event()
    event2 = sample_event()
    event2 = event2.__class__(**{**event2.__dict__, "id": 42, "event_name": "B"})
    event1 = event1.__class__(**{**event1.__dict__, "id": 42, "event_name": "A"})
    repo.upsert([event1])
    repo.upsert([event2])
    found = repo.find_by_id(42)
    assert found.event_name == "B"


def test_search_text_with_filters(repo):
    # Insert multiple events with different cities and categories
    base_event = sample_event()
    events = []
    for i in range(6):
        event = base_event.__class__(**{
            **base_event.__dict__,
            "id": f"filt_{i}",
            "event_name": f"Event {i}",
            "start_datetime": base_event.start_datetime + timedelta(days=i),
            "region": "Berlin" if i % 2 == 0 else "Bavaria",
            "event_type": "Music" if i % 2 == 0 else "Art"
        })
        events.append(event)
    repo.upsert(events)
    # Search for Berlin Music events
    results = repo.search_text("music", filters={"region": "Berlin"})
    assert all(
        e.region == "Berlin" and (getattr(e, "event_type", "").lower() == "music")
        for e in results
    )
    # Search for Art events in Bavaria
    results = repo.search_text("art", filters={"region": "Bavaria"})
    assert all(
        e.region == "Bavaria" and (getattr(e, "event_type", "").lower() == "art")
        for e in results
    )


def test_search_text_all_filters(repo):
    from datetime import date, timedelta
    base_event = sample_event()
    events = []
    for i in range(5):
        event = base_event.__class__(**{
            **base_event.__dict__,
            "id": f"filt2_{i}",
            "event_name": f"Event {i}",
            "start_datetime": base_event.start_datetime + timedelta(days=i),
            "region": "RegionA" if i % 2 == 0 else "RegionB",
            "event_type": "Music",
            "price_min": 10 + i,
            "price_max": 10 + i,
            "dance_style": ["tag1", "tag2"] if i % 2 == 0 else ["tag3"]
        })
        events.append(event)
    repo.upsert(events)
    # Test price_min, price_max, region, tags, date_from, date_to
    results = repo.search_text("", filters={
        "price_min": 12,
        "price_max": 14,
        "region": "RegionA",
        "dance_style": ["tag1"],
        "date_from": date.today() + timedelta(days=1),
        "date_to": date.today() + timedelta(days=4)
    })
    assert all(
        (getattr(e, "price_min", 0) >= 12) and
        (getattr(e, "price_max", 0) <= 14) and
        e.region == "RegionA" and
        any("tag1" in (getattr(e, "dance_style", []) or []) for t in ["tag1"]) for e in results
    )


def test_upsert_edge_cases(repo):
    # Upsert with None id, tags as None, tags as empty
    event = sample_event()
    event_no_id = event.__class__(**{**event.__dict__, "id": None})
    event_empty_style = event.__class__(**{**event.__dict__, "dance_style": []})
    count = repo.upsert([event_no_id, event_empty_style])
    assert count == 2

    # Insert multiple events with different regions and types
    base_event = sample_event()
    events = []
    for i in range(6):
        event = base_event.__class__(**{
            **base_event.__dict__,
            "id": f"filt_{i}",
            "event_name": f"Event {i}",
            "start_datetime": base_event.start_datetime + timedelta(days=i),
            "region": "Berlin" if i % 2 == 0 else "Bavaria",
            "event_type": "Music" if i % 2 == 0 else "Art"
        })
        events.append(event)
    repo.upsert(events)
    # Search for Berlin Music events
    results = repo.search_text("music", filters={"region": "Berlin"})
    assert all(
        e.region == "Berlin" and (getattr(e, "event_type", "").lower() == "music")
        for e in results
    )
    # Search for Art events in Bavaria
    results = repo.search_text("art", filters={"region": "Bavaria"})
    assert all(
        e.region == "Bavaria" and (getattr(e, "event_type", "").lower() == "art")
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
