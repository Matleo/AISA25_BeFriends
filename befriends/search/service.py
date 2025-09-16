"""Search service for finding events."""

from __future__ import annotations

import logging
from ..catalog.repository import CatalogRepository
from .relevance import RelevancePolicy
from ..domain.search_models import SearchQuery, SearchResult

class SearchService:
    """Handles event search and relevance ranking."""

    def __init__(self, repository: CatalogRepository, policy: RelevancePolicy):
        """Initialize with repository and ranking policy."""
        self.repository = repository
        self.policy = policy

    def find_events(self, query: SearchQuery) -> SearchResult:
        """Find and rank events matching the query."""
        logger = logging.getLogger(self.__class__.__name__)
        try:
            events = self.repository.search_text(query.text, filters=query.__dict__)
            ranked = self.policy.rank(events, query)
            logger.info(f"Found {len(ranked)} events for query '{query.text}'")
            return SearchResult(events=ranked, total=len(ranked))
        except Exception as e:
            logger.error(f"Error in find_events: {e}")
            raise
