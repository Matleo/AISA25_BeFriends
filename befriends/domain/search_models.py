"""Search query and result models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from .event import Event, EventModel


@dataclass(frozen=True)
class SearchQuery:
    """Encapsulates search parameters for events."""

    text: str
    date_from: Optional[date]
    date_to: Optional[date]
    city: Optional[str]
    region: Optional[str]
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    # audience_size_min: Optional[int] = None
    # audience_size_max: Optional[int] = None

    def has_filters(self) -> bool:
        """Return True if any filters are set."""
        return any(
            [
                self.date_from,
                self.date_to,
                self.city,
                self.region,
                self.category,
                self.tags,
            ]
        )


# Pydantic model for API validation


class SearchQueryModel(BaseModel):
    text: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    city: Optional[str] = None
    region: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    # audience_size_min: Optional[int] = None
    # audience_size_max: Optional[int] = None

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
