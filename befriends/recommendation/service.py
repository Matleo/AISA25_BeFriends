
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
        today: Optional[datetime.date] = None
    ) -> List[Event]:
        """
        Recommend events based on filters and user profile.

        Args:
            filters (Dict[str, Any]): Filtering options (city, category, etc.)
            profile (Dict[str, Any]): User profile (city, interests, etc.)
            max_events (int): Max number of events to return
            today (Optional[datetime.date]): Override for 'now'. Defaults to today.

        Returns:
            List[Event]: Recommended events
        """
        if today is None:
            today = datetime.date.today()
        try:
            events = self.repository.list_recent(limit=100)
            # TODO: Add filtering and ranking logic here, using filters/profile
            # For now, just return the most recent events
            return events[:max_events]
        except Exception as e:
            self.logger.error(f"Error in recommend_events: {e}")
            return []
