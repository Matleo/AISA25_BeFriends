from befriends.recommendation.service import RecommendationService
from befriends.domain.event import Event

import datetime
class DummyRepo:
    def search_text(self, *args, **kwargs):
        return self.list_recent()
    def list_recent(self, limit=100):
        now = datetime.datetime.now()
        return [Event(
            id=str(i),
            event_name=f"Event {i}",
            start_datetime=datetime.datetime(2025, 9, 20, 20, 0),
            end_datetime=None,
            recurrence_rule=None,
            date_description=None,
            event_type="Music",
            dance_focus=None,
            dance_style=["music"],
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
            event_location="Loc",
            region="Region",
            season=None,
            cross_border_potential=None,
            organizer="Venue",
            instagram=None,
            event_link=None,
            event_link_fit=None,
            description="desc",
            ingested_at=now
        ) for i in range(10)]

def test_recommend_events_returns_limited_events():
    repo = DummyRepo()
    service = RecommendationService(repo)
    events = service.recommend_events({}, {}, max_events=3)
    assert len(events) == 3
    assert all(isinstance(e, Event) for e in events)

def test_recommend_events_handles_exception():
    class FailingRepo:
        def list_recent(self, limit=100):
            raise Exception("DB error!")
    service = RecommendationService(FailingRepo())
    events = service.recommend_events({}, {}, max_events=2)
    assert events == []
