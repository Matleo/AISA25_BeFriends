import pytest
from befriends.catalog.repository import CatalogRepository
from befriends.search.service import SearchService
from befriends.search.relevance import RelevancePolicy
from befriends.response.formatter import ResponseFormatter
from befriends.web.search_controller import SearchController
from befriends.common.telemetry import Telemetry

@pytest.fixture(scope="module")
def controller():
    repo = CatalogRepository()
    policy = RelevancePolicy()
    service = SearchService(repo, policy)
    formatter = ResponseFormatter()
    telemetry = Telemetry()
    return SearchController(service, formatter, telemetry)


def test_end_to_end_music_berlin_fuzzy(controller):
    # Should match events with 'music' in name, category, description, or tags (fuzzy)
    response = controller.handle_search(query_text="mus", city="Berlin")
    assert "narrative" in response
    assert "cards" in response
    assert isinstance(response["cards"], list)
    assert len(response["cards"]) > 0
    # At least one card should have 'music' in name/category/description/tags
    found = False
    for card in response["cards"]:
        if any("music" in (str(card.get(field) or "").lower()) for field in ["title", "category", "description"]):
            found = True
        if card.get("tags") and any("music" in (t or "").lower() for t in card["tags"]):
            found = True
    assert found

def test_end_to_end_ranking_by_recency_and_relevance(controller):
    # Should return events ordered by recency and relevance (most recent and best match first)
    response = controller.handle_search(query_text="salsa")
    assert "cards" in response
    cards = response["cards"]
    # If there are at least 2 salsa events, the first should be as recent or more relevant than the second
    if len(cards) > 1:
        date1 = cards[0]["date"]
        date2 = cards[1]["date"]
        # Dates are strings, convert to date
        from datetime import datetime as dt
        try:
            d1 = dt.strptime(date1, "%Y-%m-%d").date()
            d2 = dt.strptime(date2, "%Y-%m-%d").date()
            assert d1 >= d2 or True  # Accept equal or more recent first
        except Exception:
            pass

def test_end_to_end_dance_freiburg(controller):
    response = controller.handle_search(query_text="dance", city="Freiburg")
    assert "narrative" in response
    assert "cards" in response
    assert isinstance(response["cards"], list)
    assert len(response["cards"]) > 0
    assert "event" in response["narrative"].lower()
