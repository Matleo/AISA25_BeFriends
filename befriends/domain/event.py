"""Event domain entity."""

from __future__ import annotations


from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel

import datetime


@dataclass(frozen=True)
class Event:
    """Immutable event entity representing a social event."""

    id: Optional[str]
    name: str
    date: datetime.date
    time_text: Optional[str]
    location: Optional[str]
    description: Optional[str]
    city: Optional[str]
    region: Optional[str]
    source_id: Optional[str]
    ingested_at: datetime.datetime
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    price: Optional[str] = None
    venue: Optional[str] = None

    def to_summary(self) -> str:
        """Return a narrative summary of the event."""
        summary = f"{self.name} on {self.date}"
        if self.city:
            summary += f" in {self.city}"
        if self.category:
            summary += f" [{self.category}]"
        return summary


# Pydantic model for API validation
class EventModel(BaseModel):
    id: Optional[str] = None
    name: str
    date: datetime.date
    time_text: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    source_id: Optional[str] = None
    ingested_at: datetime.datetime
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    price: Optional[str] = None
    venue: Optional[str] = None

    model_config = {"from_attributes": True}
