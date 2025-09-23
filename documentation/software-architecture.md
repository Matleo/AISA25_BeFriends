# BeFriends Software Architecture Document

> **Last updated:** 2025-09-19

## Table of Contents
1. Overview
2. High-Level Architecture Diagram
3. Main Components
4. Data Flow
5. Key Design Principles
6. Technology Stack
7. Extensibility & Adaptability
8. Error Handling & Logging
9. Testing Strategy
10. Deployment & Configuration

---

## 1. Overview
BeFriends is a modular, extensible event recommendation and chatbot platform built with Python and Streamlit. It provides personalized event suggestions and a conversational interface, integrating with external APIs and a local event database.

## 2. High-Level Architecture Diagram
```
+-------------------+
|   User (Browser)  |
+--------+----------+
         |
         v
+--------+----------+
|   Streamlit UI    |  <--- Chat, event cards, filters, onboarding
+--------+----------+
         |
         v
+--------+----------+
|  UI Components    |  (components/ui.py)
+--------+----------+
         |
         v
+--------+----------+
| Recommendation   |  (befriends/recommendation/service.py)
| & Search Service |
+--------+----------+
         |
         v
+--------+----------+
|   Catalog Repo   |  (befriends/catalog/repository.py)
+--------+----------+
         |
         v
+--------+----------+
|   SQLite DB      |
+------------------+

+-------------------+
|  ResponseFormatter|  (befriends/response/formatter.py)
+-------------------+

+-------------------+
|  Chatbot Client   |  (befriends/chatbot_client.py)
+-------------------+
```


### Component Responsibilities & Interactions
- **[Streamlit UI](../streamlit_chatbot.py)**: Main entry point, manages session state, chat, and event display. Orchestrates user interaction and delegates logic to services/components.
- **[UI Components](../components/ui.py)**: Renders event cards, filters, and chat UI. Stateless; receives data and formatting from services/formatter.
- **[RecommendationService](../befriends/recommendation/service.py)**: Business logic for event filtering, ranking, and recommendations. Accepts repository and config via dependency injection.
- **[CatalogRepository](../befriends/catalog/repository.py)**: Handles all event data access (CRUD) via SQLAlchemy ORM. Abstracts DB details from business logic.
- **[ResponseFormatter](../befriends/response/formatter.py)**: Formats event data for chat, cards, and summaries. Used by both UI and chatbot for consistent output.
- **[ChatbotClient](../befriends/chatbot_client.py)**: Integrates with OpenAI or other LLM APIs for conversational responses. Uses config for API keys and endpoints.
- **[Domain Models](../befriends/domain/)**: Dataclasses and Pydantic models for events, search queries, and results. Enforces type safety and validation.
- **[Config](../befriends/common/config.py)**: Centralized configuration for DB, API keys, and feature flags. Loads from `.env` and environment variables.


## 4. Data Flow (Example)
1. User interacts with Streamlit UI (chat, filters, etc.).
2. UI calls `RecommendationService.recommend_events(filters, profile)`.
3. Service fetches events from `CatalogRepository`.
4. Events are filtered/ranked and returned.
5. `ResponseFormatter` formats events for display (cards, chat, summaries).
6. UI renders formatted data.
7. For chat, user messages are sent to `ChatbotClient`, which returns a response.

**Example:**
```python
from befriends.recommendation.service import RecommendationService
from befriends.catalog.repository import CatalogRepository
repo = CatalogRepository()
recommender = RecommendationService(repo)
events = recommender.recommend_events(filters, profile)
```

## 5. Key Design Principles
- **Separation of Concerns**: UI, business logic, data access, and formatting are strictly separated.
- **Modularity**: Each module has a single responsibility and can be tested independently.
- **Adaptability**: Easy to swap out event sources, chat providers, or UI frameworks.
- **Type Safety**: Uses dataclasses and Pydantic models for all core data.
- **Configuration**: All settings are centralized and environment-based.

## 6. Technology Stack
- **Python 3.11+**
- **Streamlit** (UI)
- **SQLAlchemy** (ORM)
- **SQLite** (default DB)
- **OpenAI API** (chatbot)
- **Pydantic** (validation)
- **pytest** (testing)


## 7. Extensibility & Adaptability
- **Add new event sources:** Implement a new repository class (subclass `CatalogRepository` or follow its interface), then register it in the config or service layer.
- **Swap chatbot providers:** Update or extend `ChatbotClient` to use a different API/provider. Inject via config.
- **Add new UI features:** Extend or add functions in `components/ui.py` and call them from the Streamlit app.
- **Business logic:** All logic is in services and can be tested/mocked independently.

**Example: Adding a new event source**
```python
class MyApiRepository(CatalogRepository):
    def list_recent(self, limit=50):
        # Fetch from external API
        ...
```

## 8. Error Handling & Logging
- All major operations have try/except blocks and log errors.
- User-friendly error messages in UI.
- Custom exceptions for domain-specific errors.

## 9. Testing Strategy
- Unit tests for all business logic and formatting.
- Integration tests for end-to-end flows.
- Mocks for external APIs and DB.


## 10. Deployment & Configuration
- **Config:** All config in [befriends/common/config.py](../befriends/common/config.py) or `.env` file. See `.env.example` for required variables.
- **Secrets:** API keys and DB URLs should be set via environment variables or `.env` (never hardcoded).
- **Deployment:**
    - Local: `streamlit run streamlit_app.py`
    - Docker: `docker build -t aisa25_befriends . && docker run -p 8000:8000 --env-file .env aisa25_befriends`
    - Streamlit Cloud: Upload repo, set secrets in dashboard.
- **Requirements:** Managed in `requirements.txt`.

## 11. Testing Examples & Structure
- **Test folder:** All tests in `tests/` (unit, integration, end-to-end).
- **Sample unit test:**
```python
def test_recommendation_service_returns_events():
    repo = MockRepository()
    service = RecommendationService(repo)
    events = service.recommend_events({}, {}, max_events=2)
    assert isinstance(events, list)
```
- **Run tests:** `pytest`

## 12. Glossary
- **Service:** A class encapsulating business logic (e.g., RecommendationService).
- **Repository:** Data access layer, abstracts DB or API (e.g., CatalogRepository).
- **Formatter:** Formats data for UI or chat (e.g., ResponseFormatter).
- **Profile:** User preferences and attributes used for recommendations.
- **Config:** Centralized settings, loaded from environment.

## 13. Known Limitations & Future Work
- Filtering and ranking logic in `RecommendationService` is basic; can be improved with ML or advanced heuristics.
- No authentication or user management yet.
- No admin UI for event management.
- Limited support for recurring events and multi-language.
- More robust error handling and logging can be added.

---

For a quick summary, see the project [README.md](../README.md).

---

For a quick summary, see the project README.md.
