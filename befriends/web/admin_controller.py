"""Controller for admin operations."""

from __future__ import annotations
from ..ingestion.service import IngestionService
from ..common.telemetry import Telemetry

class AdminController:
    """Handles admin requests for ingestion and status."""

    def __init__(self, ingestion_service: IngestionService, telemetry: Telemetry):
        """Initialize with dependencies."""
        self.ingestion_service = ingestion_service
        self.telemetry = telemetry

    def reingest(self) -> dict:
        """Trigger re-ingestion of all sources."""
        count = self.ingestion_service.ingest_all()
        self.telemetry.record_event("reingest", count=count)
        return {"status": "ok", "ingested": count}

    def status(self) -> dict:
        """Return system status."""
        # ...gather status info...
        return {"status": "ok"}
