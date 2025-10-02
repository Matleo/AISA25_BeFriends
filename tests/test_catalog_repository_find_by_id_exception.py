import pytest
from befriends.catalog.repository import CatalogRepository
from befriends.domain.event import Event


def sample_event():
    import datetime
    from datetime import datetime
    return Event(
        id="1",
        event_name="Sample Event",
        start_datetime=datetime(2025, 10, 1, 20, 0),
        end_datetime=None,
        recurrence_rule=None,
        date_description=None,
        event_type=None,
        dance_focus=None,
        dance_style=None,
        price_min=None,
        price_max=None,
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
        event_location=None,
        region=None,
        season=None,
        cross_border_potential=None,
        organizer=None,
        instagram=None,
        event_link=None,
        event_link_fit=None,
        description=None,
        ingested_at=datetime.now()
    )


def test_find_by_id_exception_handling(monkeypatch):
    repo = CatalogRepository()
    # Simulate exception in session.get

    def raise_exc(self, *a, **kw):
        raise sqlalchemy.exc.SQLAlchemyError("fail")
    import sqlalchemy.orm
    monkeypatch.setattr(sqlalchemy.orm.Session, "get", raise_exc)
    with pytest.raises(sqlalchemy.exc.SQLAlchemyError):
        repo.find_by_id("1")
