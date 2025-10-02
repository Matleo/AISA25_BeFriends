# conftest.py for shared fixtures and test configuration
import pytest

# --- Shared test helpers and fixtures ---
from datetime import date, datetime
from befriends.domain.event import Event

class DummyEvent:
    def __init__(self, event_name, start_datetime, event_location, event_type=None, description=None, instagram=None, id=None, region=None, price_min=None, price_max=None, currency=None, organizer=None, dance_style=None, date_description=None):
        self.id = id or "dummy-id"
        self.event_name = event_name
        # Accept both str and datetime for start_datetime
        if isinstance(start_datetime, str):
            try:
                from datetime import datetime
                self.start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d")
            except Exception:
                self.start_datetime = start_datetime
        else:
            self.start_datetime = start_datetime
        self.end_datetime = None
        self.recurrence_rule = None
        self.date_description = date_description
        self.event_type = event_type
        self.dance_focus = None
        self.dance_style = dance_style if dance_style is not None else ["music"]
        self.price_min = price_min if price_min is not None else 20
        self.price_max = price_max if price_max is not None else 20
        self.currency = currency if currency is not None else "EUR"
        self.pricing_type = None
        self.price_category = None
        self.audience_min = None
        self.audience_max = None
        self.audience_size_bucket = None
        self.age_min = None
        self.age_max = None
        self.age_group_label = None
        self.user_category = None
        self.event_location = event_location
        self.region = region if region is not None else (event_location if event_location else "Region")
        self.season = None
        self.cross_border_potential = None
        self.organizer = organizer if organizer is not None else "Venue"
        self.instagram = instagram
        self.event_link = None
        self.event_link_fit = None
        self.description = description
        self.ingested_at = datetime.now()

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def to_summary(self):
        summary = f"{self.event_name} on {self.start_datetime}"
        if self.event_location:
            summary += f" in {self.event_location}"
        if self.event_type:
            summary += f" [{self.event_type}]"
        return summary

@pytest.fixture
def make_event():
    def _make_event(**kwargs):
        base = dict(
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
            ingested_at=datetime.now(),
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
