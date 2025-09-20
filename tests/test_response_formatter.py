import pytest
from befriends.response.formatter import ResponseFormatter
from befriends.domain.search_models import SearchResult





@pytest.mark.parametrize("event_kwargs,expected", [
    (dict(name="No Details"), "No Details"),
    (dict(name="Concert", category="Music"), "Concert"),
])
def test_to_narrative_various_cases(formatter, make_event, event_kwargs, expected):
    event = make_event(**event_kwargs)
    result = SearchResult(events=[event], total=1)
    narrative = formatter.to_narrative(result)
    assert expected in narrative



@pytest.mark.parametrize("num_events,expected", [
    (7, "...and 2 more."),
    (3, None),
])
def test_to_narrative_truncation_cases(formatter, make_event, num_events, expected):
    events = [make_event(id=str(i), name=f"Event {i}", category="Music") for i in range(num_events)]
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
    assert any(
        card["category"] == "Music" for card in cards
    )
    assert any(
        card["tags"] == ["live", "rock"] for card in cards
    )
