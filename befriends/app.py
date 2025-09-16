"""Application composition root for befriends."""

from __future__ import annotations

from .common.config import AppConfig
from .common.telemetry import Telemetry
from .ingestion.service import IngestionService
from .catalog.repository import CatalogRepository
from .search.relevance import RelevancePolicy
from .search.service import SearchService
from .response.formatter import ResponseFormatter
from .web.search_controller import SearchController
from .web.admin_controller import AdminController
from fastapi import FastAPI, Query, HTTPException, status, Depends
import os
from load_events_from_csv import import_events_from_csv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager


class Application:
    """Composition root; wires dependencies and exposes controllers."""

    def __init__(self, config: AppConfig, telemetry: Telemetry):
        """Initialize application with config and telemetry."""
        self.config = config
        self.telemetry = telemetry
        # Wire repositories, services, policies, controllers, telemetry, config
        self.catalog_repo = CatalogRepository()
        self.relevance_policy = RelevancePolicy()
        self.search_service = SearchService(self.catalog_repo, self.relevance_policy)
        self.response_formatter = ResponseFormatter()
        from .ingestion.normalizer import Normalizer
        from .ingestion.deduper import Deduper
        self.ingestion_service = IngestionService(
            [], Normalizer(), Deduper(), self.catalog_repo, self.telemetry
        )
        self.search_controller_inst = SearchController(
            self.search_service, self.response_formatter, self.telemetry
        )
        self.admin_controller_inst = AdminController(
            self.ingestion_service, self.telemetry
        )

    @classmethod
    def build_default(cls) -> "Application":
        """Factory for default application instance."""
        config = AppConfig.from_env()
        telemetry = Telemetry()
        return cls(config, telemetry)

    def search_controller(self) -> SearchController:
        """Return the search controller."""
        return self.search_controller_inst

    def admin_controller(self) -> AdminController:
        """Return the admin controller."""
        return self.admin_controller_inst


def create_app() -> FastAPI:
    """Create and configure FastAPI app, wiring controllers to endpoints."""
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        result = import_events_from_csv(verbose=True)
        print(
            f"[Startup] Imported {result['imported']} events from CSV. "
            f"Errors: {len(result['errors'])}"
        )
        yield

    app = FastAPI(title="Befriends API", version="1.0", lifespan=lifespan)
    # Allow CORS for local dev
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application = Application.build_default()
    search_controller = application.search_controller()
    admin_controller = application.admin_controller()

    @app.get("/search")
    def search(
        query_text: str = Query(..., description="Search text"),
        date_from: str = Query(None),
        date_to: str = Query(None),
        city: str = Query(None),
        region: str = Query(None),
    ):
        """Search for events."""
        filters = {
            "date_from": date_from,
            "date_to": date_to,
            "city": city,
            "region": region,
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        result = search_controller.handle_search(query_text, **filters)
        return JSONResponse(content=result)

    # --- API ENDPOINT TO TRIGGER CSV IMPORT (with password auth) ---
    def check_password(password: str = Query(..., description="Admin password")):
        default_pw = os.environ.get("CSV_IMPORT_PASSWORD", "import123")
        if password != default_pw:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
            )
        return True

    @app.post("/admin/import-csv")
    def import_csv(password_ok: bool = Depends(check_password)):
        result = import_events_from_csv(verbose=False)
        return {
            "imported": result["imported"],
            "errors": result["errors"]
        }

    @app.post("/admin/reingest")
    def reingest():
        """Trigger re-ingestion of all sources."""
        result = admin_controller.reingest()
        return JSONResponse(content=result)

    return app


# Entrypoint for running with uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "befriends.app:create_app",
        host="0.0.0.0",
        port=8000,
        factory=True,
        reload=True,
    )
