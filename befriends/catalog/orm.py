from sqlalchemy import (
    create_engine,
    Column,
    String,
    Date,
    DateTime,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid
from befriends.domain.event import Event

Base = declarative_base()  # type: ignore


class EventORM(Base):  # type: ignore[misc, valid-type]
    """SQLAlchemy ORM model for events table. Uses string PK and correct types for SQLite compatibility."""
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time_text = Column(String)
    location = Column(String)
    description = Column(Text)
    city = Column(String)
    region = Column(String)
    source_id = Column(String)
    ingested_at = Column(DateTime, nullable=False)
    category = Column(String)
    price = Column(String)
    venue = Column(String)
    tags = Column(Text)

    def to_domain(self) -> "Event":
        from datetime import datetime, date as dt_date
        return Event(
            id=str(self.id) if self.id is not None else None,
            name=str(self.name) if self.name is not None else "",
            date=self.date if isinstance(self.date, dt_date) else dt_date.today(),
            time_text=str(self.time_text) if self.time_text is not None else None,
            location=str(self.location) if self.location is not None else None,
            description=str(self.description) if self.description is not None else None,
            city=str(self.city) if self.city is not None else None,
            region=str(self.region) if self.region is not None else None,
            source_id=str(self.source_id) if self.source_id is not None else None,
            ingested_at=self.ingested_at if isinstance(self.ingested_at, datetime)
            else datetime.now(),
            category=str(self.category) if self.category is not None else None,
            tags=self.tags.split(",") if self.tags else None,
            price=str(self.price) if self.price is not None else None,
            venue=str(self.venue) if self.venue is not None else None,
        )

    @staticmethod
    def from_domain(event: "Event") -> "EventORM":
        """Create EventORM from Event domain object, auto-converting id/date/datetime if needed."""
        import datetime
        id_val = event.id
        if id_val is not None:
            id_val = str(id_val)
        date_val = event.date
        if isinstance(date_val, str):
            date_val = datetime.datetime.strptime(date_val, "%Y-%m-%d").date()
        ingested_val = event.ingested_at
        if isinstance(ingested_val, str):
            try:
                ingested_val = datetime.datetime.fromisoformat(ingested_val)
            except Exception:
                ingested_val = datetime.datetime.strptime(ingested_val, "%Y-%m-%d %H:%M:%S.%f")
        return EventORM(
            id=id_val,
            name=event.name,
            date=date_val,
            time_text=event.time_text,
            location=event.location,
            description=event.description,
            city=event.city,
            region=event.region,
            source_id=event.source_id,
            ingested_at=ingested_val,
            category=event.category,
            tags=",".join(event.tags) if event.tags else None,
            price=event.price,
            venue=event.venue,
        )


def get_engine_and_session(db_url: str = "sqlite:///events.db"):
    """Create SQLAlchemy engine and session factory."""
    engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, Session
