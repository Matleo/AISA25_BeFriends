"""Catalog repository for authoritative event storage."""

from __future__ import annotations


import logging
from ..domain.event import Event
from .orm import EventORM, get_engine_and_session


class CatalogRepository:
    """Stores and retrieves events using SQLite via SQLAlchemy ORM."""

    def _get_logger(self):
        return logging.getLogger(self.__class__.__name__)

    def __init__(self, db_url: str = "sqlite:///events.db"):
        self.engine, self.Session = get_engine_and_session(db_url)

    def upsert(self, events: list[Event]) -> int:
        logger = self._get_logger()
        session = self.Session()
        count = 0
        try:
            for event in events:
                obj = session.get(EventORM, event.id) if event.id else None
                if obj:
                    for field in Event.__dataclass_fields__:
                        value = getattr(event, field)
                        if field == "tags":
                            value = ",".join(value) if value else None
                        setattr(obj, field, value)
                else:
                    obj = EventORM.from_domain(event)
                    session.merge(obj)
                count += 1
            session.commit()
            # Info log removed
        except Exception as e:
            logger.error(f"Error during upsert: {e}")
            session.rollback()
            raise
        finally:
            session.close()
        return count

    def list_recent(self, limit: int = 50) -> list[Event]:
        logger = self._get_logger()
        session = self.Session()
        try:
            q = session.query(EventORM).order_by(EventORM.start_datetime.desc()).limit(limit)
            events = [e.to_domain() for e in q]
            import logging
            for ev in events:
                logging.info(f"[Repository] Event: name={getattr(ev, 'event_name', None)}, description={getattr(ev, 'description', None)}")
            return events
        except Exception as e:
            logger.error(f"Error during list_recent: {e}")
            raise
        finally:
            session.close()

    def find_by_id(self, event_id: str) -> Event | None:
        logger = self._get_logger()
        session = self.Session()
        try:
            obj = session.get(EventORM, event_id)
            if obj:
                # Info log removed
                return obj.to_domain()
            else:
                # Info log removed
                return None
        except Exception as e:
            logger.error(f"Error during find_by_id: {e}")
            raise
        finally:
            session.close()

    def search_text(self, text: str, filters: dict | None = None) -> list[Event]:
        logger = self._get_logger()
        from sqlalchemy import or_, cast, Float
        session = self.Session()
        try:
            q = session.query(EventORM)
            if text:
                pattern = f"%{text}%"
                q = q.filter(
                    or_(
                        EventORM.event_name.ilike(pattern),
                        EventORM.event_type.ilike(pattern),
                        EventORM.dance_style.ilike(pattern),
                        EventORM.region.ilike(pattern),
                        EventORM.event_location.ilike(pattern),
                        EventORM.organizer.ilike(pattern),
                        EventORM.instagram.ilike(pattern),
                    )
                )
            if filters:
                if filters.get("region"):
                    q = q.filter(EventORM.region == filters["region"])
                if filters.get("event_type"):
                    q = q.filter(EventORM.event_type == filters["event_type"])
                # Map date_from/date_to to strict date filtering if both are present and equal
                if filters.get("date_from") and filters.get("date_to") and filters["date_from"] == filters["date_to"]:
                    from sqlalchemy import func
                    q = q.filter(func.date(EventORM.start_datetime) == filters["date_from"])
                else:
                    if filters.get("date_from"):
                        q = q.filter(EventORM.start_datetime >= filters["date_from"])
                    if filters.get("date_to"):
                        q = q.filter(EventORM.start_datetime <= filters["date_to"])
                if filters.get("start_datetime_from"):
                    q = q.filter(EventORM.start_datetime >= filters["start_datetime_from"])
                if filters.get("start_datetime_to"):
                    q = q.filter(EventORM.start_datetime <= filters["start_datetime_to"])
                if filters.get("price_min"):
                    q = q.filter(cast(EventORM.price_min, Float) >= filters["price_min"])
                if filters.get("price_max"):
                    q = q.filter(cast(EventORM.price_max, Float) <= filters["price_max"])
                if filters.get("dance_style"):
                    q = q.filter(EventORM.dance_style == filters["dance_style"])
                if filters.get("organizer"):
                    q = q.filter(EventORM.organizer == filters["organizer"])
                if filters.get("instagram"):
                    q = q.filter(EventORM.instagram == filters["instagram"])
            q = q.order_by(EventORM.start_datetime.desc())
            events = [e.to_domain() for e in q.all()]
            import logging
            for ev in events:
                logging.info(f"[Repository] Event: name={getattr(ev, 'event_name', None)}, description={getattr(ev, 'description', None)}")
            return events
        except Exception as e:
            logger.error(f"Error during search_text: {e}")
            raise
        finally:
            session.close()

    def search_events(self, filters, *args, **kwargs):
    # Entry log removed
        # Do not modify filters here
        session = self.Session()
        try:
            q = session.query(EventORM)
            # ... existing filtering logic ...
            q = q.order_by(EventORM.start_datetime.desc())
            events = [e.to_domain() for e in q.all()]
            for ev in events:
                logger.info(f"[Repository] Event: name={getattr(ev, 'event_name', None)}, description={getattr(ev, 'description', None)}")
            return events
        except Exception as e:
            self._get_logger().error(f"Error during search_events: {e}")
            raise
        finally:
            session.close()
