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
    e1 = Event(
        id="1",
        name=a_name,
        date=date.today(),
        time_text=None,
        location=None,
        description=None,
        city=None,
        region=None,
        source_id=None,
        ingested_at=datetime.now(),
    )
    e2 = Event(
        id="2",
        name=b_name,
        date=date.today(),
        time_text=None,
        location=None,
        description=None,
        city=None,
        region=None,
        source_id=None,
        ingested_at=datetime.now(),
    )
    assert deduper.is_duplicate(e1, e2) is expected


@pytest.mark.parametrize("a_name,b_name", [
    ("A", "B"),
    ("A", "A"),
])
def test_merge_returns_first_param(deduper, a_name, b_name):
    e1 = Event(
        id="1",
        name=a_name,
        date=date.today(),
        time_text=None,
        location=None,
        description=None,
        city=None,
        region=None,
        source_id=None,
        ingested_at=datetime.now(),
    )
    e2 = Event(
        id="2",
        name=b_name,
        date=date.today(),
        time_text=None,
        location=None,
        description=None,
        city=None,
        region=None,
        source_id=None,
        ingested_at=datetime.now(),
    )
    merged = deduper.merge(e1, e2)
    assert merged == e1


def test_normalize_and_batch(normalizer):
    raw = {"name": "Test Event", "date": date.today()}
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
    # Should fallback to today if date is invalid
    raw = {"name": "Bad Date", "date": "not-a-date"}
    event = normalizer.normalize(raw)
    assert isinstance(event, Event)

def test_normalize_missing_name(normalizer):
    # Should default name to empty string
    raw = {"date": date.today()}
    event = normalizer.normalize(raw)
    assert event.name == ""

def test_normalize_batch_exception(monkeypatch, normalizer):
    # Simulate exception in normalize_batch
    def bad_normalize(raw):
        raise Exception("normalize fail")
    monkeypatch.setattr(normalizer, "normalize", bad_normalize)
    with pytest.raises(Exception):
        normalizer.normalize_batch([{"name": "fail"}])
