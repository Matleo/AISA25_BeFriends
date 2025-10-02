import pytest
from unittest.mock import MagicMock
from befriends.search.service import SearchService
from befriends.domain.search_models import SearchQuery, SearchResult


@pytest.fixture
def mock_repository():
    repository = MagicMock()
    repository.search_text.return_value = ["event1", "event2"]
    return repository


@pytest.fixture
def mock_policy():
    policy = MagicMock()
    policy.rank.return_value = ["event2", "event1"]
    return policy


@pytest.fixture
def search_service(mock_repository, mock_policy):
    return SearchService(repository=mock_repository, policy=mock_policy)


def test_find_events_calls_repository_and_policy(search_service, mock_repository, mock_policy):
    from datetime import datetime, timedelta
    query = SearchQuery(
        text="music",
        start_datetime_from=datetime.now(),
        start_datetime_to=datetime.now() + timedelta(days=30),
        region="Berlin"
    )
    result = search_service.find_events(query)
    # Check repository.search_text called
    assert mock_repository.search_text.called
    # Check policy.rank called
    assert mock_policy.rank.called
    # Check result is a SearchResult
    assert isinstance(result, SearchResult)
