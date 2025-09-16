"""Controller for user search requests."""

from __future__ import annotations

import logging
from ..search.service import SearchService
from ..response.formatter import ResponseFormatter
from ..common.telemetry import Telemetry


class SearchController:
    """Handles user search requests and prepares UI responses."""

    def __init__(
        self,
        search_service: SearchService,
        response_formatter: ResponseFormatter,
        telemetry: Telemetry,
    ):
        """Initialize with dependencies."""
        self.search_service = search_service
        self.response_formatter = response_formatter
        self.telemetry = telemetry

    def handle_search(self, query_text: str, **filters) -> dict:
        """Handle a search request and return UI payload."""
        logger = logging.getLogger(self.__class__.__name__)
        from ..domain.search_models import SearchQuery

        try:
            # Build SearchQuery from query_text and all supported filters
            query = SearchQuery(
                text=query_text,
                date_from=filters.get("date_from"),
                date_to=filters.get("date_to"),
                city=filters.get("city"),
                region=filters.get("region"),
                category=filters.get("category"),
                tags=filters.get("tags"),
                price_min=filters.get("price_min"),
                price_max=filters.get("price_max"),
            )
            # Search for events
            result = self.search_service.find_events(query)
            # Format response
            narrative = self.response_formatter.to_narrative(result)
            cards = self.response_formatter.to_cards(result)
            # Record telemetry
            self.telemetry.record_event("search", query=query_text, filters=filters)
            logger.info(f"Handled search for '{query_text}' with filters {filters}")
            return {"narrative": narrative, "cards": cards}
        except Exception as e:
            logger.error(f"Error in handle_search: {e}")
            raise
