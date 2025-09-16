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
            logger.info(f"Upserted {count} events.")
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
            q = session.query(EventORM).order_by(EventORM.date.desc()).limit(limit)
            events = [e.to_domain() for e in q]
            logger.info(f"Listed {len(events)} recent events.")
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
                logger.info(f"Found event by id: {event_id}")
                return obj.to_domain()
            else:
                logger.info(f"No event found for id: {event_id}")
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
                        EventORM.name.ilike(pattern),
                        EventORM.category.ilike(pattern),
                        EventORM.description.ilike(pattern),
                        EventORM.tags.ilike(pattern),
                    )
                )
            if filters:
                if filters.get("city"):
                    q = q.filter(EventORM.city == filters["city"])
                if filters.get("region"):
                    q = q.filter(EventORM.region == filters["region"])
                if filters.get("category"):
                    q = q.filter(EventORM.category == filters["category"])
                if filters.get("date_from"):
                    q = q.filter(EventORM.date >= filters["date_from"])
                if filters.get("date_to"):
                    q = q.filter(EventORM.date <= filters["date_to"])
                # Price range filter (assumes price is stored as string, try to cast to float)
                if filters.get("price_min"):
                    q = q.filter(
                        cast(EventORM.price, Float) >= filters["price_min"]
                    )
                if filters.get("price_max"):
                    q = q.filter(
                        cast(EventORM.price, Float) <= filters["price_max"]
                    )
                # Tags filter (any tag match)
                if filters.get("tags"):
                    tag_filters = [
                        EventORM.tags.ilike(f"%{tag}%") for tag in filters["tags"]
                    ]
                    q = q.filter(or_(*tag_filters))
            # Always order by most recent first (recency bias)
            q = q.order_by(EventORM.date.desc())
            events = [e.to_domain() for e in q.all()]
            logger.info(
                f"Search returned {len(events)} events for text '{text}' "
                f"and filters {filters}."
            )
            return events
        except Exception as e:
            logger.error(f"Error during search_text: {e}")
            raise
        finally:
            session.close()
