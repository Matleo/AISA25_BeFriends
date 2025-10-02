"""
Recommendation service for event suggestions.
Provides event recommendations based on user filters and profile.
Supports dependency injection for repository.
"""


from typing import List, Optional, Dict, Any
from befriends.catalog.repository import CatalogRepository
from befriends.domain.event import Event
import datetime
import logging
import copy


class RecommendationService:
    """
    Handles event recommendation and filtering logic.
    Accepts a repository dependency for testability and flexibility.
    """

    def __init__(self, repository: CatalogRepository):
        """
        Initialize RecommendationService.
        Args:
            repository (CatalogRepository): The event repository to use.
        """
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    def recommend_events(
        self,
        filters: Dict[str, Any],
        profile: Dict[str, Any],
        max_events: int = 6,
        today: Optional[datetime.date] = None,
        text: Optional[str] = None
    ) -> List[Event]:
        """
        Recommend events based on filters, user profile, and optional free-text query.

        Args:
            filters (Dict[str, Any]): Filtering options (city, category, etc.)
            profile (Dict[str, Any]): User profile (city, interests, etc.)
            max_events (int): Max number of events to return
            today (Optional[datetime.date]): Override for 'now'. Defaults to today.
            text (Optional[str]): Free-text search query (for chatbot)

        Returns:
            List[Event]: Recommended events
        """
        filters = copy.deepcopy(filters)  # Deepcopy FIRST, before any other code

        if today is None:
            today = datetime.date.today()
        try:
            # Only set defaults if missing or None
            if 'date_from' not in filters or filters['date_from'] is None:
                filters['date_from'] = today
            if 'date_to' not in filters or filters['date_to'] is None:
                filters['date_to'] = today + datetime.timedelta(days=30)
            if filters.get('region') is None and profile and profile.get('city'):
                filters['region'] = profile['city']

            # If a free-text query is provided, use full-text search
            if text:
                events = self.repository.search_text(text, filters)
                return events[:max_events]

            # Otherwise, use filters/profile for recommendations
            events = self.repository.search_text("", filters)
            return events[:max_events]
        except Exception as e:
            self.logger.error(f"Error in recommend_events: {e}")
            return []
