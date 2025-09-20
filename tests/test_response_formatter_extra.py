from befriends.response.formatter import ResponseFormatter

from .conftest import DummyEvent

def test_chat_event_list_basic():
    events = [DummyEvent("Test Event", "2025-09-20", "Basel", "Music", description="A fun event.", time_text="20:00", location="Venue", instagram="@test")]
    fmt = ResponseFormatter()
    result = fmt.chat_event_list(events)
    assert "Test Event" in result
    assert "Basel" in result
    assert "Music" in result
    assert "20:00" in result
    assert "Venue" in result
    assert "@test" in result

def test_chat_event_list_empty():
    fmt = ResponseFormatter()
    result = fmt.chat_event_list([])
    assert result == ""

def test_chat_event_summary_basic():
    events = [DummyEvent("Test Event", "2025-09-20", "Basel", "Music")]
    fmt = ResponseFormatter()
    result = fmt.chat_event_summary(events)
    assert "Upcoming events include" in result
    assert "Test Event" in result

def test_chat_event_summary_empty():
    fmt = ResponseFormatter()
    result = fmt.chat_event_summary([])
    assert result == "(No events available)"

def test_to_narrative_and_to_cards():
    class DummyResult:
        def __init__(self):
            self.events = [DummyEvent("Event1", "2025-09-20", "Basel", "Music", price=10, tags=["music"])]
            self.total = 1
    fmt = ResponseFormatter()
    result = DummyResult()
    narrative = fmt.to_narrative(result)
    cards = fmt.to_cards(result)
    assert "Event1" in narrative
    assert isinstance(cards, list)
    assert cards[0]["title"] == "Event1"

def test_chat_event_list_with_long_description():
    desc = "A" * 200
    events = [DummyEvent("LongDesc", "2025-09-20", "Basel", "Music", description=desc)]
    fmt = ResponseFormatter()
    result = fmt.chat_event_list(events)
    assert "..." in result


# --- Additional coverage tests ---
def test_chat_event_list_invalid_date():
    # Should fall back to date_str if date parsing fails
    events = [DummyEvent("BadDate", "not-a-date", "Basel", "Music")]
    fmt = ResponseFormatter()
    result = fmt.chat_event_list(events)
    assert "not-a-date" in result

def test_chat_event_list_dict_event():
    # Should support dict event and missing fields
    fmt = ResponseFormatter()
    events = [{"name": "DictEvent", "date": "2025-09-21", "city": "Zurich", "category": "Art"}]
    result = fmt.chat_event_list(events)
    assert "DictEvent" in result
    assert "Zurich" in result

def test_chat_event_summary_invalid_date():
    # Should fall back to date_str if date parsing fails
    events = [DummyEvent("BadDate", "not-a-date", "Basel", "Music")]
    fmt = ResponseFormatter()
    result = fmt.chat_event_summary(events)
    assert "not-a-date" in result

def test_chat_event_summary_dict_event():
    # Should support dict event and missing fields
    fmt = ResponseFormatter()
    events = [{"name": "DictEvent", "date": "2025-09-21", "city": "Zurich", "category": "Art"}]
    result = fmt.chat_event_summary(events)
    assert "DictEvent" in result
    assert "Zurich" in result

def test_to_narrative_more_than_five_events():
    class DummyResult:
        def __init__(self):
            self.events = [DummyEvent(f"Event{i}", "2025-09-20", "Basel", "Music") for i in range(7)]
            self.total = 7
    fmt = ResponseFormatter()
    result = DummyResult()
    narrative = fmt.to_narrative(result)
    assert "...and 2 more." in narrative

def test_to_cards_missing_fields():
    class DummyResult:
        def __init__(self):
            # Event with only required fields
            self.events = [DummyEvent("Minimal", "2025-09-20", None, None)]
            self.total = 1
    fmt = ResponseFormatter()
    result = DummyResult()
    cards = fmt.to_cards(result)
    assert cards[0]["title"] == "Minimal"
