from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Date,
    DateTime,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from befriends.domain.event import Event

Base = declarative_base()


class EventORM(Base):
    __tablename__ = "events"
    id = Column('id', Integer, primary_key=True, autoincrement=True)
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
    # tags as comma-separated string for simplicity
    tags = Column(String)

    def to_domain(self) -> "Event":
        return Event(
            id=self.id,
            name=self.name,
            date=self.date,
            time_text=self.time_text,
            location=self.location,
            description=self.description,
            city=self.city,
            region=self.region,
            source_id=self.source_id,
            ingested_at=self.ingested_at,
            category=self.category,
            tags=self.tags.split(",") if self.tags else None,
            price=self.price,
            venue=self.venue,
        )

    @staticmethod
    def from_domain(event: "Event") -> "EventORM":
        """Create EventORM from Event domain object."""
        return EventORM(
            id=event.id,
            name=event.name,
            date=event.date,
            time_text=event.time_text,
            location=event.location,
            description=event.description,
            city=event.city,
            region=event.region,
            source_id=event.source_id,
            ingested_at=event.ingested_at,
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
