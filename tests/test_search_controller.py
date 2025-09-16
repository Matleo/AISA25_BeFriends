def test_handle_search_empty_query(controller, mock_search_service, mock_response_formatter, mock_telemetry):
    mock_search_service.find_events.return_value = None
    mock_response_formatter.to_narrative.return_value = "No events found."
    mock_response_formatter.to_cards.return_value = []
    response = controller.handle_search("")
    assert response["narrative"] == "No events found."
    assert response["cards"] == []

def test_handle_search_invalid_filters(controller, mock_search_service, mock_response_formatter, mock_telemetry):
    # Should not raise even with unexpected filter keys
    mock_search_service.find_events.return_value = None
    response = controller.handle_search("music", foo="bar", baz=123)
    assert "narrative" in response
    assert "cards" in response
def test_handle_search_with_nonempty_result(controller, mock_search_service, mock_response_formatter, mock_telemetry):
    from befriends.domain.event import Event
    from befriends.domain.search_models import SearchResult
    from datetime import date, datetime
    event = Event(
        id="2",
        name="Music Event",
        date=date.today(),
        time_text=None,
        location=None,
        description="A fun music event",
        city="Berlin",
        region=None,
        source_id=None,
        ingested_at=datetime.now(),
        category="Music"
    )
    mock_search_service.find_events.return_value = SearchResult(events=[event], total=1)
    mock_response_formatter.to_narrative.return_value = "Found 1 event"
    mock_response_formatter.to_cards.return_value = [{"id": "2"}]
    response = controller.handle_search("music", city="Berlin")
    assert response["narrative"] == "Found 1 event"
    assert response["cards"] == [{"id": "2"}]
import pytest
from unittest.mock import MagicMock
from befriends.web.search_controller import SearchController
from befriends.domain.search_models import SearchQuery, SearchResult

@pytest.fixture
def mock_search_service():
    service = MagicMock()
    service.find_events.return_value = SearchResult(events=[], total=0)
    return service

@pytest.fixture
def mock_response_formatter():
    formatter = MagicMock()
    formatter.to_narrative.return_value = "Test narrative"
    formatter.to_cards.return_value = [{"card": 1}]
    return formatter

@pytest.fixture
def mock_telemetry():
    return MagicMock()

@pytest.fixture
def controller(mock_search_service, mock_response_formatter, mock_telemetry):
    return SearchController(
        search_service=mock_search_service,
        response_formatter=mock_response_formatter,
        telemetry=mock_telemetry
    )

def test_handle_search_builds_query_and_calls_service(controller, mock_search_service, mock_response_formatter, mock_telemetry):
    response = controller.handle_search("music", city="Berlin")
    # Check that SearchQuery was built and find_events called
    assert mock_search_service.find_events.called
    # Check that formatter methods were called
    assert mock_response_formatter.to_narrative.called
    assert mock_response_formatter.to_cards.called
    # Check that telemetry was recorded
    assert mock_telemetry.record_event.called
    # Check response structure
    assert response == {"narrative": "Test narrative", "cards": [{"card": 1}]}
