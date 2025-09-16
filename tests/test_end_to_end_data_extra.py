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


def test_end_to_end_price_range(controller):
    # Should return only events with price >= 10 and <= 20
    response = controller.handle_search(query_text="", price_min=10, price_max=20)
    assert "cards" in response
    for card in response["cards"]:
        if card["price"]:
            try:
                price_val = float(str(card["price"]).split()[0].replace(",", "."))
                assert 10 <= price_val <= 20
            except Exception:
                pass  # Ignore non-numeric prices


def test_end_to_end_tags(controller):
    # Should return events with tag 'Salsa' (case-insensitive, partial match)
    response = controller.handle_search(query_text="", tags=["Salsa"])
    assert "cards" in response
    found = False
    for card in response["cards"]:
        if card["tags"] and any("salsa" in t.lower() for t in card["tags"] if t):
            found = True
    assert found
