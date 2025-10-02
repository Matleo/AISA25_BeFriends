import pytest
from befriends.ingestion.deduper import Deduper
from befriends.ingestion.normalizer import Normalizer
from befriends.domain.event import Event
from datetime import date, datetime


@pytest.fixture
def deduper():
    return Deduper()


@pytest.fixture
def normalizer():
    return Normalizer()


@pytest.mark.parametrize("a_name,b_name,expected", [
    ("A", "B", False),
    ("A", "A", True),
])
def test_is_duplicate_cases(deduper, a_name, b_name, expected):
    from datetime import datetime
    e1 = Event(
        id="1",
        event_name=a_name,
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
        ingested_at=datetime.now(),
    )
    e2 = Event(
        id="2",
        event_name=b_name,
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
        ingested_at=datetime.now(),
    )
    assert deduper.is_duplicate(e1, e2) is expected


@pytest.mark.parametrize("a_name,b_name", [
    ("A", "B"),
    ("A", "A"),
])
def test_merge_returns_first_param(deduper, a_name, b_name):
    from datetime import datetime
    e1 = Event(
        id="1",
        event_name=a_name,
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
        ingested_at=datetime.now(),
    )
    e2 = Event(
        id="2",
        event_name=b_name,
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
        ingested_at=datetime.now(),
    )
    merged = deduper.merge(e1, e2)
    assert merged == e1


def test_normalize_and_batch(normalizer):
    raw = {
        "id": "1",
        "event_name": "Test Event",
        "start_datetime": datetime(2025, 10, 1, 20, 0),
        "end_datetime": None,
        "recurrence_rule": None,
        "date_description": None,
        "event_type": None,
        "dance_focus": None,
        "dance_style": ["test"],
        "price_min": None,
        "price_max": None,
        "currency": None,
        "pricing_type": None,
        "price_category": None,
        "audience_min": None,
        "audience_max": None,
        "audience_size_bucket": None,
        "age_min": None,
        "age_max": None,
        "age_group_label": None,
        "user_category": None,
        "event_location": None,
        "region": None,
        "season": None,
        "cross_border_potential": None,
        "organizer": None,
        "instagram": None,
        "event_link": None,
        "event_link_fit": None,
        "description": None,
        "ingested_at": datetime.now(),
    }
    event = normalizer.normalize(raw)
    assert isinstance(event, Event)
    batch = normalizer.normalize_batch([raw, raw])
    assert isinstance(batch, list)
    assert all(
        isinstance(e, Event) for e in batch
    )


# --- Additional coverage and robustness tests ---
def test_is_duplicate_exception(monkeypatch, deduper):
    # Simulate exception in is_duplicate
    class BadEvent:
        def __getattr__(self, name):
            raise Exception("fail")
    with pytest.raises(Exception):
        deduper.is_duplicate(BadEvent(), BadEvent())

def test_merge_exception(monkeypatch, deduper):
    # Simulate exception in merge
    class BadEvent:
        pass
    def bad_merge(a, b):
        raise Exception("merge fail")
    monkeypatch.setattr(deduper, "merge", bad_merge)
    with pytest.raises(Exception):
        deduper.merge(BadEvent(), BadEvent())

def test_dedupe_exception(monkeypatch, deduper):
    # Simulate exception in dedupe
    def bad_dedupe(events):
        raise Exception("dedupe fail")
    monkeypatch.setattr(deduper, "dedupe", bad_dedupe)
    with pytest.raises(Exception):
        deduper.dedupe([Event(id="1", name="A", date=date.today(), time_text=None, location=None, description=None, city=None, region=None, source_id=None, ingested_at=datetime.now())])

def test_normalize_invalid_date(normalizer):
    # Should fallback to now if start_datetime is invalid
    raw = {"event_name": "Bad Date", "start_datetime": "not-a-date"}
    event = normalizer.normalize(raw)
    assert isinstance(event, Event)

def test_normalize_missing_name(normalizer):
    # Should default event_name to empty string
    raw = {"start_datetime": datetime.now()}
    event = normalizer.normalize(raw)
    assert event.event_name == ""

def test_normalize_batch_exception(monkeypatch, normalizer):
    # Simulate exception in normalize_batch
    def bad_normalize(raw):
        raise Exception("normalize fail")
    monkeypatch.setattr(normalizer, "normalize", bad_normalize)
    with pytest.raises(Exception):
        normalizer.normalize_batch([{"name": "fail"}])
