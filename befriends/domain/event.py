"""Event domain entity."""

from __future__ import annotations



from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel
import datetime



@dataclass(frozen=True)
class Event:
    """Immutable event entity representing a social event (new schema)."""

    id: Optional[str]
    event_name: str
    start_datetime: Optional[datetime.datetime]
    end_datetime: Optional[datetime.datetime]
    recurrence_rule: Optional[str]
    date_description: Optional[str]
    event_type: Optional[str]
    dance_focus: Optional[str]
    dance_style: Optional[List[str]]
    price_min: Optional[float]
    price_max: Optional[float]
    currency: Optional[str]
    pricing_type: Optional[str]
    price_category: Optional[str]
    audience_min: Optional[int]
    audience_max: Optional[int]
    audience_size_bucket: Optional[str]
    age_min: Optional[int]
    age_max: Optional[int]
    age_group_label: Optional[str]
    user_category: Optional[str]
    event_location: Optional[str]
    region: Optional[str]
    season: Optional[str]
    cross_border_potential: Optional[str]
    organizer: Optional[str]
    instagram: Optional[str]
    event_link: Optional[str] = None
    event_link_fit: Optional[str] = None
    description: Optional[str] = None
    ingested_at: datetime.datetime = datetime.datetime.now()

    event_date: Optional[str] = None
    event_time: Optional[str] = None
    weekday: Optional[str] = None
    month: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def to_summary(self) -> str:
        summary = f"{self.event_name} on {self.start_datetime}"
        if self.event_location:
            summary += f" at {self.event_location}"
        if self.event_type:
            summary += f" [{self.event_type}]"
        return summary



# Pydantic model for API validation (new schema)
class EventModel(BaseModel):
    id: Optional[str] = None
    event_name: str
    start_datetime: Optional[datetime.datetime] = None
    end_datetime: Optional[datetime.datetime] = None
    recurrence_rule: Optional[str] = None
    date_description: Optional[str] = None
    event_type: Optional[str] = None
    dance_focus: Optional[str] = None
    dance_style: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: Optional[str] = None
    pricing_type: Optional[str] = None
    price_category: Optional[str] = None
    audience_min: Optional[int] = None
    audience_max: Optional[int] = None
    audience_size_bucket: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    age_group_label: Optional[str] = None
    user_category: Optional[str] = None
    event_location: Optional[str] = None
    region: Optional[str] = None
    season: Optional[str] = None
    cross_border_potential: Optional[str] = None
    organizer: Optional[str] = None
    instagram: Optional[str] = None
    event_link: Optional[str] = None
    event_link_fit: Optional[str] = None
    description: Optional[str] = None
    ingested_at: datetime.datetime = datetime.datetime.now()

    model_config = {"from_attributes": True}
