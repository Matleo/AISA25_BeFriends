"""Search query and result models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from .event import Event, EventModel



@dataclass(frozen=True)
class SearchQuery:
    """Encapsulates search parameters for events (new schema)."""

    text: str
    start_datetime_from: Optional[date]
    start_datetime_to: Optional[date]
    region: Optional[str]
    event_type: Optional[str] = None
    dance_style: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None

    def has_filters(self) -> bool:
        """Return True if any filters are set."""
        return any(
            [
                self.start_datetime_from,
                self.start_datetime_to,
                self.region,
                self.event_type,
                self.dance_style,
            ]
        )


# Pydantic model for API validation



class SearchQueryModel(BaseModel):
    text: str
    start_datetime_from: Optional[date] = None
    start_datetime_to: Optional[date] = None
    region: Optional[str] = None
    event_type: Optional[str] = None
    dance_style: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None

    model_config = {"from_attributes": True}


class SearchResultModel(BaseModel):
    events: List[EventModel]
    total: int

    model_config = {"from_attributes": True}


@dataclass(frozen=True)
class SearchResult:
    """Holds search results and total count."""

    events: list[Event]
    total: int
