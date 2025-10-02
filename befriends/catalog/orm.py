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
    """SQLAlchemy ORM model for events table (new schema)."""
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name = Column(String, nullable=False)
    start_datetime = Column(DateTime, nullable=True)
    end_datetime = Column(DateTime, nullable=True)
    recurrence_rule = Column(String, nullable=True)
    date_description = Column(String, nullable=True)
    event_type = Column(String, nullable=True)
    dance_focus = Column(String, nullable=True)
    dance_style = Column(String, nullable=True)
    price_min = Column(String, nullable=True)
    price_max = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    pricing_type = Column(String, nullable=True)
    price_category = Column(String, nullable=True)
    audience_min = Column(String, nullable=True)
    audience_max = Column(String, nullable=True)
    audience_size_bucket = Column(String, nullable=True)
    age_min = Column(String, nullable=True)
    age_max = Column(String, nullable=True)
    age_group_label = Column(String, nullable=True)
    user_category = Column(String, nullable=True)
    event_location = Column(String, nullable=True)
    region = Column(String, nullable=True)
    season = Column(String, nullable=True)
    cross_border_potential = Column(String, nullable=True)
    organizer = Column(String, nullable=True)
    instagram = Column(String, nullable=True)
    event_link = Column(String, nullable=True)
    event_link_fit = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    ingested_at = Column(DateTime, nullable=False)

    def to_domain(self) -> "Event":
        from datetime import datetime
        return Event(
            id=str(self.id) if self.id is not None else None,
            event_name=str(self.event_name) if self.event_name is not None else "",
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
            recurrence_rule=self.recurrence_rule,
            date_description=self.date_description,
            event_type=self.event_type,
            dance_focus=self.dance_focus,
            dance_style=self.dance_style,
            price_min=float(self.price_min) if self.price_min is not None else None,
            price_max=float(self.price_max) if self.price_max is not None else None,
            currency=self.currency,
            pricing_type=self.pricing_type,
            price_category=self.price_category,
            audience_min=int(self.audience_min) if self.audience_min is not None else None,
            audience_max=int(self.audience_max) if self.audience_max is not None else None,
            audience_size_bucket=self.audience_size_bucket,
            age_min=int(self.age_min) if self.age_min is not None else None,
            age_max=int(self.age_max) if self.age_max is not None else None,
            age_group_label=self.age_group_label,
            user_category=self.user_category,
            event_location=self.event_location,
            region=self.region,
            season=self.season,
            cross_border_potential=self.cross_border_potential,
            organizer=self.organizer,
            instagram=self.instagram,
            event_link=self.event_link,
            event_link_fit=self.event_link_fit,
            description=self.description,
            ingested_at=self.ingested_at if isinstance(self.ingested_at, datetime) else datetime.now(),
        )

    @staticmethod
    def from_domain(event: "Event") -> "EventORM":
        """Create EventORM from Event domain object, auto-converting id/datetime if needed (new schema)."""
        import datetime
        id_val = event.id
        if id_val is not None:
            id_val = str(id_val)
        ingested_val = event.ingested_at
        if isinstance(ingested_val, str):
            try:
                ingested_val = datetime.datetime.fromisoformat(ingested_val)
            except Exception:
                ingested_val = datetime.datetime.strptime(ingested_val, "%Y-%m-%d %H:%M:%S.%f")
        return EventORM(
            id=id_val,
            event_name=event.event_name,
            start_datetime=event.start_datetime,
            end_datetime=event.end_datetime,
            recurrence_rule=event.recurrence_rule,
            date_description=event.date_description,
            event_type=event.event_type,
            dance_focus=event.dance_focus,
            dance_style=event.dance_style,
            price_min=str(event.price_min) if event.price_min is not None else None,
            price_max=str(event.price_max) if event.price_max is not None else None,
            currency=event.currency,
            pricing_type=event.pricing_type,
            price_category=event.price_category,
            audience_min=str(event.audience_min) if event.audience_min is not None else None,
            audience_max=str(event.audience_max) if event.audience_max is not None else None,
            audience_size_bucket=event.audience_size_bucket,
            age_min=str(event.age_min) if event.age_min is not None else None,
            age_max=str(event.age_max) if event.age_max is not None else None,
            age_group_label=event.age_group_label,
            user_category=event.user_category,
            event_location=event.event_location,
            region=event.region,
            season=event.season,
            cross_border_potential=event.cross_border_potential,
            organizer=event.organizer,
            instagram=event.instagram,
            event_link=event.event_link,
            event_link_fit=event.event_link_fit,
            description=event.description,
            ingested_at=ingested_val,
        )


def get_engine_and_session(db_url: str = "sqlite:///events.db"):
    """Create SQLAlchemy engine and session factory."""
    engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, Session
