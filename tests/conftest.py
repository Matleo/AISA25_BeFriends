# conftest.py for shared fixtures and test configuration
import pytest

# --- Shared test helpers and fixtures ---
from datetime import date, datetime
from befriends.domain.event import Event

class DummyEvent:
    def __init__(self, name, date, city, category, description=None, time_text=None, location=None, instagram=None, tags=None, price=None, id=None, region=None, venue=None, source_id=None):
        self.id = id or "dummy-id"
        self.name = name
        self.date = date
        self.city = city
        self.category = category
        self.description = description
        self.time_text = time_text
        self.location = location
        self.instagram = instagram
        self.tags = tags or []
        self.price = price
        self.region = region
        self.venue = venue
        self.source_id = source_id

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def to_summary(self):
        summary = f"{self.name} on {self.date}"
        if self.city:
            summary += f" in {self.city}"
        if self.category:
            summary += f" [{self.category}]"
        return summary

@pytest.fixture
def make_event():
    def _make_event(**kwargs):
        base = dict(
            id="1",
            name="Sample Event",
            date=date(2025, 10, 1),
            time_text=None,
            location=None,
            description=None,
            city=None,
            region=None,
            source_id=None,
            ingested_at=datetime.now(),
            category=None,
            tags=None,
            price=None,
            venue=None,
        )
        base.update(kwargs)
        return Event(**base)
    return _make_event

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP error")

@pytest.fixture(autouse=True)
def enable_strict_mode():
    # Example: could set up strict mode, logging, or env vars for all tests
    pass
