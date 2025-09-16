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

def test_is_duplicate_false(deduper):
    e1 = Event(id="1", name="A", date=date.today(), time_text=None, location=None, description=None, city=None, region=None, source_id=None, ingested_at=datetime.now())
    e2 = Event(id="2", name="B", date=date.today(), time_text=None, location=None, description=None, city=None, region=None, source_id=None, ingested_at=datetime.now())
    assert not deduper.is_duplicate(e1, e2)

def test_merge_returns_first(deduper):
    e1 = Event(id="1", name="A", date=date.today(), time_text=None, location=None, description=None, city=None, region=None, source_id=None, ingested_at=datetime.now())
    e2 = Event(id="2", name="B", date=date.today(), time_text=None, location=None, description=None, city=None, region=None, source_id=None, ingested_at=datetime.now())
    merged = deduper.merge(e1, e2)
    assert merged == e1

def test_normalize_and_batch(normalizer):
    raw = {"name": "Test Event", "date": date.today()}
    event = normalizer.normalize(raw)
    assert isinstance(event, Event)
    batch = normalizer.normalize_batch([raw, raw])
    assert isinstance(batch, list)
    assert all(isinstance(e, Event) for e in batch)
