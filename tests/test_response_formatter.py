import pytest
from befriends.response.formatter import ResponseFormatter
from befriends.domain.search_models import SearchResult





@pytest.mark.parametrize("event_kwargs,expected", [
    (dict(event_name="No Details"), "No Details"),
    (dict(event_name="Concert", category="Music"), "Concert"),
])
def test_to_narrative_various_cases(formatter, make_event, event_kwargs, expected):
    # Map legacy 'category' to 'event_type' for new schema
    if "category" in event_kwargs:
        event_kwargs["event_type"] = event_kwargs.pop("category")
    event = make_event(**event_kwargs)
    result = SearchResult(events=[event], total=1)
    narrative = formatter.to_narrative(result)
    assert expected in narrative



@pytest.mark.parametrize("num_events,expected", [
    (7, "...and 2 more."),
    (3, None),
])
def test_to_narrative_truncation_cases(formatter, make_event, num_events, expected):
    events = [make_event(id=str(i), event_name=f"Event {i}", event_type="Music") for i in range(num_events)]
    result = SearchResult(events=events, total=num_events)
    narrative = formatter.to_narrative(result)
    if expected:
        assert expected in narrative
    else:
        assert "...and" not in narrative


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


def test_to_narrative_and_cards_with_events(formatter, make_event):
    event = make_event(
        event_name="Concert",
        event_location="Arena",
        description="Live music",
        region="Berlin",
        event_type="Music",
        dance_style=["live", "rock"],
        price_min=20.0,
        price_max=20.0,
        currency="EUR",
        organizer="Arena Berlin"
    )
    result = SearchResult(events=[event], total=1)
    narrative = formatter.to_narrative(result)
    cards = formatter.to_cards(result)
    assert "Concert" in narrative
    assert "Music" in narrative
    assert "20.0 - 20.0 EUR" in narrative
    assert any(
        card["event_type"] == "Music" for card in cards
    )
    assert any(
        card["tags"] == ["live", "rock"] for card in cards
    )
