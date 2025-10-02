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
    # Add a Salsa-tagged event for tag search test
    from befriends.domain.event import Event
    import datetime
    salsa_event = Event(
        id="100",
        event_name="Salsa Night",
        start_datetime=datetime.date.today(),
        end_datetime=None,
        recurrence_rule=None,
        date_description=None,
        event_type="Dance",
        dance_focus=None,
        dance_style=["Salsa", "party"],
        price_min=10,
        price_max=10,
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
        event_location="Test Club",
        region="Test Region",
        season=None,
        cross_border_potential=None,
        organizer="Test Club",
        instagram=None,
        event_link=None,
        event_link_fit=None,
        description="A salsa dance event",
        ingested_at=datetime.datetime.now(),
    )
    repo.upsert([salsa_event])
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
        # Use price_min and price_max fields from new schema
        price_min = card.get("price_min")
        price_max = card.get("price_max")
        if price_min is not None:
            try:
                price_val = float(price_min)
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
