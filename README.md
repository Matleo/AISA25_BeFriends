
# Befriends


Befriends is a modular Python 3.11 system for discovering social events for a single user. It is designed with clean architecture, separation of concerns, and extensibility in mind.

## Codebase Summary

The codebase is organized into clear, modular layers:

- **Domain**: Immutable data models (`Event`, `SearchQuery`, `SearchResult`) define the core business entities and contracts.
- **Ingestion**: Source connectors fetch, normalize, and deduplicate event data before upserting into the catalog.
- **Catalog**: The authoritative repository for events, supporting upsert, list, find, and search operations.
- **Search & Relevance**: Handles keyword search and applies ranking policies to results.
- **Response**: Formats search results for UI consumption (narratives, cards).
- **Web**: Controllers for user and admin requests, orchestrating the main flows.
- **Common**: Configuration and telemetry utilities for observability and environment management.
- **App**: The composition root, wiring all dependencies and exposing controllers.

## Key Features
- Ingests events from multiple sources (HTML, APIs, etc.)
- Normalizes and deduplicates event data
- Stores events in an authoritative catalog
- Provides keyword search with relevance ranking and filters
- Formats responses for UI (narratives, cards)
- Web controllers for user and admin operations
- Configurable and observable via config and telemetry


## Project Structure
```
befriends/
   app.py                # Application composition root & FastAPI app
   common/               # Configuration and telemetry
   domain/               # Core domain models (Event, SearchQuery, etc.)
   ingestion/            # Source connectors, normalization, deduplication
   catalog/              # Event repository
   search/               # Search and relevance logic
   response/             # UI response formatting
   web/                  # Web controllers (user/admin)
tests/
   test_api_endpoints.py # Integration tests for API endpoints
   ...                   # Unit tests for all core features
requirements.txt        # All dependencies (including FastAPI, Uvicorn, pytest, ML stack)
```




## Basic User & API Flow

1. **User or client submits a search request** (via web UI or `/search` API endpoint).
2. **FastAPI endpoint `/search`** calls `SearchController.handle_search` with the search text and filters.
   - Builds a `SearchQuery` object.
   - Calls `SearchService.find_events(query)`.
3. **`SearchService.find_events`**:
   - Calls `CatalogRepository.search_text(query.text, filters=query.__dict__)` to fetch matching events.
   - Passes results to `RelevancePolicy.rank(events, query)` for ranking.
   - Returns a `SearchResult` object.
4. **`SearchController`**:
   - Uses `ResponseFormatter.to_narrative(result)` and `to_cards(result)` to prepare UI-friendly outputs.
   - Records the search event via `Telemetry`.
   - Returns the formatted response to the user or API client.

**Example (API Usage):**

```sh
# Search for "music events in Berlin" via API
curl -X GET "http://localhost:8000/search?query_text=music&city=Berlin"
# Response: {"narrative": ..., "cards": [...]}

# Trigger re-ingestion of all sources (admin)
curl -X POST "http://localhost:8000/admin/reingest"
# Response: {"status": "ok", "ingested": ...}
```

**Example (Python, internal):**

```python
# User action: search for "music events in Berlin"
response = search_controller.handle_search(
    query_text="music",
    city="Berlin"
)
# Returns: {"narrative": ..., "cards": [...]}
```


## Getting Started
1. Create and activate a Python 3.11 virtual environment:
   ```sh
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the API server (development):
   ```sh
   uvicorn befriends.app:create_app --factory --reload
   ```
4. Explore the codebase, run tests, and build features:
   ```sh
   pytest tests/ -v
   ```


## Design Principles
- **SOLID**: Each class has a single responsibility and clear dependencies.
- **Testability**: Pure logic, dependency injection, and clear contracts. Unit and integration tests included.
- **Extensibility**: Easy to add new connectors, policies, or controllers.
- **Separation of Concerns**: Domain, ingestion, catalog, search, response, and web layers are isolated.
- **API-first**: RESTful endpoints for search and admin flows, ready for frontend or automation.


## API Endpoints

- `GET /search` — Search for events. Query params: `query_text`, `date_from`, `date_to`, `city`, `region`
- `POST /admin/reingest` — Trigger re-ingestion of all sources (admin)


## Testing

- Unit tests for all core features: controllers, services, ingestion, deduplication, formatting, repository
- Integration tests for API endpoints using FastAPI's TestClient
- Edge case coverage: empty queries, invalid filters, no matches, duplicate upserts, missing fields, and narrative truncation
- Run all tests:
   ```sh
   pytest tests/ -v
   ```

## Future Extensions
- Multi-user friend matching
- Recommendations and chat
- Persistent storage and external search

## License
MIT
