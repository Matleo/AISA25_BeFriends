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
            for ev in events:
                logger.info(f"[Repository] Event: name={getattr(ev, 'event_name', None)}, description={getattr(ev, 'description', None)}")
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
            logger.info(f"[DEBUG] search_text called with text='{text}' and filters={filters}")
            q = session.query(EventORM)
            if text:
                pattern = f"%{text}%"
                q = q.filter(
                    or_(
                        EventORM.event_name.ilike(pattern),
                        EventORM.event_type.ilike(pattern),
                        EventORM.dance_style.ilike(pattern),
                        EventORM.region_standardized.ilike(pattern),
                        EventORM.event_location.ilike(pattern),
                        EventORM.organizer.ilike(pattern),
                        EventORM.instagram.ilike(pattern),
                    )
                )
            logger.info(f"[DEBUG] search_text SQL after text filter: {str(q)}")
            if filters:
                logger.info(f"[DEBUG] search_text applying filters: {filters}")
                region_val = filters.get("region_standardized")
                # Only filter by region if not 'All' and not empty
                if region_val and region_val != "All":
                    q = q.filter(EventORM.region_standardized == region_val)
                    logger.info(f"[DEBUG] search_text filter region_standardized={region_val}")
                if filters.get("event_type"):
                    q = q.filter(EventORM.event_type == filters["event_type"])
                    logger.info(f"[DEBUG] search_text filter event_type={filters['event_type']}")
                # Map date_from/date_to to strict date filtering if both are present and equal
                if filters.get("date_from") and filters.get("date_to") and filters["date_from"] == filters["date_to"]:
                    from sqlalchemy import func
                    q = q.filter(func.date(EventORM.start_datetime) == filters["date_from"])
                    logger.info(f"[DEBUG] search_text filter date_from=date_to={filters['date_from']}")
                else:
                    if filters.get("date_from"):
                        q = q.filter(EventORM.start_datetime >= filters["date_from"])
                        logger.info(f"[DEBUG] search_text filter date_from>={filters['date_from']}")
                    if filters.get("date_to"):
                        q = q.filter(EventORM.start_datetime <= filters["date_to"])
                        logger.info(f"[DEBUG] search_text filter date_to<={filters['date_to']}")
                if filters.get("start_datetime_from"):
                    q = q.filter(EventORM.start_datetime >= filters["start_datetime_from"])
                    logger.info(f"[DEBUG] search_text filter start_datetime_from>={filters['start_datetime_from']}")
                if filters.get("start_datetime_to"):
                    q = q.filter(EventORM.start_datetime <= filters["start_datetime_to"])
                    logger.info(f"[DEBUG] search_text filter start_datetime_to<={filters['start_datetime_to']}")
                if filters.get("price_min"):
                    q = q.filter(cast(EventORM.price_min, Float) >= filters["price_min"])
                    logger.info(f"[DEBUG] search_text filter price_min>={filters['price_min']}")
                if filters.get("price_max"):
                    q = q.filter(cast(EventORM.price_max, Float) <= filters["price_max"])
                    logger.info(f"[DEBUG] search_text filter price_max<={filters['price_max']}")
                if filters.get("dance_style"):
                    q = q.filter(EventORM.dance_style == filters["dance_style"])
                    logger.info(f"[DEBUG] search_text filter dance_style={filters['dance_style']}")
                if filters.get("organizer"):
                    q = q.filter(EventORM.organizer == filters["organizer"])
                    logger.info(f"[DEBUG] search_text filter organizer={filters['organizer']}")
                if filters.get("instagram"):
                    q = q.filter(EventORM.instagram == filters["instagram"])
                    logger.info(f"[DEBUG] search_text filter instagram={filters['instagram']}")
            # Exclude past events by default (start_datetime >= today, date only)
            import datetime
            from sqlalchemy import func
            today_date = datetime.date.today()
            q = q.filter(func.date(EventORM.start_datetime) >= today_date)
            # Order by ascending start_datetime (upcoming first)
            q = q.order_by(EventORM.start_datetime.asc())
            logger.info(f"[DEBUG] search_text final SQL: {str(q)}")
            events = [e.to_domain() for e in q.all()]
            logger.info(f"[DEBUG] search_text returned {len(events)} events")
            for ev in events:
                logger.info(f"[DEBUG] Event: name={getattr(ev, 'event_name', None)}, city={getattr(ev, 'city', None)}, region_standardized={getattr(ev, 'region_standardized', None)}, organizer={getattr(ev, 'organizer', None)}")
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
            logger = self._get_logger()
            for ev in events:
                logger.info(f"[Repository] Event: name={getattr(ev, 'event_name', None)}, description={getattr(ev, 'description', None)}")
            return events
        except Exception as e:
            self._get_logger().error(f"Error during search_events: {e}")
            raise
        finally:
            session.close()
