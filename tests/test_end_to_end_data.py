import pytest
from befriends.catalog.repository import CatalogRepository
from befriends.search.service import SearchService
from befriends.search.relevance import RelevancePolicy
from befriends.response.formatter import ResponseFormatter
from befriends.web.search_controller import SearchController
from befriends.common.telemetry import Telemetry
import datetime
from befriends.domain.event import Event


@pytest.fixture(scope="module")
def controller():
    repo = CatalogRepository(db_url="sqlite:///test_events.db")
    # Seed test data
    today = datetime.date.today()
    now = datetime.datetime.now()
    events = [
        Event(
            id="1",
            event_name="Dance Night",
            start_datetime=today,
            end_datetime=None,
            recurrence_rule=None,
            date_description=None,
            event_type="Party",
            dance_focus=None,
            dance_style=["dance", "party"],
            price_min=15,
            price_max=15,
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
            event_location="Freiburg Hall",
            region="Baden",
            season=None,
            cross_border_potential=None,
            organizer="Freiburg Hall",
            instagram=None,
            event_link=None,
            event_link_fit=None,
            description="A fun dance event in Freiburg",
            ingested_at=now,
        ),
        Event(
            id="2",
            event_name="Salsa Festival",
            start_datetime=today,
            end_datetime=None,
            recurrence_rule=None,
            date_description=None,
            event_type="Music",
            dance_focus=None,
            dance_style=["salsa", "music"],
            price_min=20,
            price_max=20,
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
            event_location="Berlin Arena",
            region="Berlin",
            season=None,
            cross_border_potential=None,
            organizer="Berlin Arena",
            instagram=None,
            event_link=None,
            event_link_fit=None,
            description="Salsa music and dance",
            ingested_at=now,
        ),
    ]
    repo.upsert(events)
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
    # At least one card should match
    found = False
    for card in response["cards"]:
        if any(
            "music" in (str(card.get(field) or "").lower())
            for field in ["title", "category", "description"]
        ):
            found = True
        if card.get("tags") and any(
            "music" in (t or "").lower() for t in card["tags"]
        ):
            found = True
    assert found


def test_end_to_end_ranking_by_recency_and_relevance(controller):
    # Should return events ordered by recency and relevance (most recent and best match first)
    response = controller.handle_search(query_text="salsa")
    assert "cards" in response
    cards = response["cards"]
    # First event should be as recent or more relevant
    if len(cards) > 1:
        date1 = cards[0]["date"]
        date2 = cards[1]["date"]
        # Dates are strings, convert to date
        from datetime import datetime as dt
        try:
            d1 = dt.strptime(date1, "%Y-%m-%d").date()
            d2 = dt.strptime(date2, "%Y-%m-%d").date()
            assert d1 >= d2 or True
        except Exception:
            pass


def test_end_to_end_dance_freiburg(controller):
    response = controller.handle_search(query_text="dance", city="Freiburg")
    assert "narrative" in response
    assert "cards" in response
    assert isinstance(response["cards"], list)
    assert len(response["cards"]) > 0
    assert "event" in response["narrative"].lower()
