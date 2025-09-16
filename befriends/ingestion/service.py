"""Ingestion service orchestrates connectors, normalization, dedupe, and upsert."""

from __future__ import annotations
from .base import SourceConnector
from .normalizer import Normalizer
from .deduper import Deduper
from ..catalog.repository import CatalogRepository
from ..common.telemetry import Telemetry

class IngestionService:
    """Coordinates ingestion from sources into the catalog."""

    def __init__(
        self,
        connectors: list[SourceConnector],
        normalizer: Normalizer,
        deduper: Deduper,
        repo: CatalogRepository,
        telemetry: Telemetry,
    ):
        """Initialize with dependencies."""
        self.connectors = connectors
        self.normalizer = normalizer
        self.deduper = deduper
        self.repo = repo
        self.telemetry = telemetry

    def ingest_all(self) -> int:
        """Ingest from all connectors and upsert into catalog."""
        total_upserted = 0
        for connector in self.connectors:
            raw = connector.fetch_raw()
            events = self.normalizer.normalize_batch(raw)
            deduped = self.deduper.dedupe(events)
            upserted = self.repo.upsert(deduped)
            self.telemetry.record_event("ingest", source=type(connector).__name__, count=upserted)
            total_upserted += upserted
        return total_upserted

    def ingest_from(self, connector: SourceConnector) -> int:
        """Ingest from a single connector."""
        raw = connector.fetch_raw()
        events = self.normalizer.normalize_batch(raw)
        deduped = self.deduper.dedupe(events)
        upserted = self.repo.upsert(deduped)
        self.telemetry.record_event("ingest", source=type(connector).__name__, count=upserted)
        return upserted
