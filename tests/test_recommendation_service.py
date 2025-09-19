import pytest
from befriends.recommendation.service import RecommendationService
from befriends.domain.event import Event

import datetime
class DummyRepo:
    def list_recent(self, limit=100):
        now = datetime.datetime.now()
        return [Event(
            id=str(i),
            name=f"Event {i}",
            date="2025-09-20",
            city="Basel",
            category="Music",
            description="desc",
            tags=["music"],
            price=10,
            venue="Venue",
            region="Region",
            source_id="src",
            time_text="20:00",
            location="Loc",
            instagram=None,
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
