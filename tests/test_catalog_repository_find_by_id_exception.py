import pytest
import sqlalchemy
from befriends.catalog.repository import CatalogRepository
from befriends.domain.event import Event

def sample_event():
    from datetime import date, datetime
    return Event(
        id="1",
        name="Sample Event",
        date=date.today(),
        time_text=None,
        location=None,
        description=None,
        city=None,
        region=None,
        source_id=None,
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
