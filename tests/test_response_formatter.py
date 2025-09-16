import pytest
from befriends.response.formatter import ResponseFormatter
from befriends.domain.search_models import SearchResult
from befriends.domain.event import Event
from datetime import date, datetime

def make_event(**kwargs):
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
        venue=None
    )
    base.update(kwargs)
    return Event(**base)

def test_to_narrative_missing_optional_fields(formatter):
    event = make_event(name="No Details")
    result = SearchResult(events=[event], total=1)
    narrative = formatter.to_narrative(result)
    assert "No Details" in narrative

def test_to_narrative_truncates_after_5_events(formatter):
    events = [make_event(id=str(i), name=f"Event {i}", category="Music") for i in range(7)]
    result = SearchResult(events=events, total=7)
    narrative = formatter.to_narrative(result)
    assert "...and 2 more." in narrative


@pytest.fixture
def formatter():
    return ResponseFormatter()

def test_to_narrative_empty(formatter):
    result = SearchResult(events=[], total=0)
    narrative = formatter.to_narrative(result)
    assert isinstance(narrative, str)
    assert "No events" in narrative or narrative == "No events found."


def test_to_cards_empty(formatter):
    result = SearchResult(events=[], total=0)
    cards = formatter.to_cards(result)
    assert isinstance(cards, list)
    assert cards == []

def test_to_narrative_and_cards_with_events(formatter):
    event = make_event(
        name="Concert",
        time_text="20:00",
        location="Arena",
        description="Live music",
        city="Berlin",
        region="Berlin",
        source_id="src1",
        category="Music",
        tags=["live", "rock"],
        price="20 EUR",
        venue="Arena Berlin"
    )
    result = SearchResult(events=[event], total=1)
    narrative = formatter.to_narrative(result)
    cards = formatter.to_cards(result)
    assert "Concert" in narrative
    assert "Music" in narrative
    assert "20 EUR" in narrative
    assert any(card["category"] == "Music" for card in cards)
    assert any(card["tags"] == ["live", "rock"] for card in cards)
