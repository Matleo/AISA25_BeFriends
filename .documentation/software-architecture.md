# BeFriends Software Architecture Document

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

## 3. Main Components
- **Streamlit UI**: Main entry point, manages session state, chat, and event display.
- **UI Components**: Renders event cards, filters, and chat UI. Calls services for data.
- **Recommendation/Search Service**: Business logic for event filtering, ranking, and recommendations.
- **Catalog Repository**: Handles all event data access (CRUD) via SQLAlchemy ORM.
- **ResponseFormatter**: Formats event data for chat, cards, and summaries.
- **Chatbot Client**: Integrates with OpenAI or other LLM APIs for conversational responses.
- **Domain Models**: Dataclasses and Pydantic models for events, search queries, and results.
- **Config**: Centralized configuration for DB, API keys, and feature flags.

## 4. Data Flow
1. User interacts with Streamlit UI (chat, filters, etc.).
2. UI calls RecommendationService with filters/profile.
3. Service fetches events from CatalogRepository.
4. Events are filtered/ranked and returned.
5. ResponseFormatter formats events for display.
6. UI renders formatted data.
7. For chat, user messages are sent to ChatbotClient, which returns a response.

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
- Add new event sources by implementing repository interfaces.
- Swap chatbot providers by updating ChatbotClient.
- Add new UI features by extending components/ui.py.
- All business logic is service-based and testable.

## 8. Error Handling & Logging
- All major operations have try/except blocks and log errors.
- User-friendly error messages in UI.
- Custom exceptions for domain-specific errors.

## 9. Testing Strategy
- Unit tests for all business logic and formatting.
- Integration tests for end-to-end flows.
- Mocks for external APIs and DB.

## 10. Deployment & Configuration
- All config in befriends/common/config.py or .env file.
- Can be run locally or deployed to Streamlit Cloud.
- Requirements managed in requirements.txt.

---

For a quick summary, see the project README.md.
