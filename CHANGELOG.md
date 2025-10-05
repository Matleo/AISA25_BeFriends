# Changelog

## [0.7.0] - 2025-11-XX
### Added
- Automatic event import from newest CSV (`befriends/data/11_events.csv`) at backend startup, ensuring up-to-date event data including SAK Lörrach and other regional events.
- Debug logging for event import, repository actions, and recommendation logic to aid troubleshooting and transparency.
- UI region filter now uses a select box populated from distinct regions in the database, preventing invalid or empty region selections.

### Changed
- Refactored backend region filtering logic: region is now consistently used for all event queries and recommendations, both in API and chatbot.
- Recommendation service and chatbot logic updated to always use region from filters or user profile, ensuring correct event surfacing.
- UI filter logic cleaned up for sidebar and recommendations panel; date filters default to current week when region is set.

### Fixed
- Events for SAK Lörrach and other regions are now reliably available and surfaced in the UI and API.
- Selectable regions in the UI always correspond to available events.
- Chatbot intent detection and event query logic improved for more accurate responses.

### Release
- This release completes the "region filtering and event import reliability" milestone for EventBot.
- Tag: v0.7.0

## [0.6.0] - 2025-10-03
### Added
- Enriched event data schema: added columns for event_date, event_time, weekday, month, country, city, latitude, longitude, and event_link.
- Improved event descriptions for better readability.
- Added new documentation (AISA Abgabe PDF, etc).

### Changed
- Refactored all event models, ORM, repository, and loader to support new schema.
- Updated all tests to cover new event fields and ensure robust data handling.

### Fixed
- Corrected initial event date selection logic in UI.
- Improved chatbot logic for special queries (e.g., Karolina praise).
- All tests now pass with the new schema.

### Release
- This release completes the "event schema enrichment and migration" milestone for EventBot.


## [0.5.0] - 2025-09-22
### Added
- Chatbot and recommendations now always filter events by the user's preferred city (from profile) and only show events for the current week.
- User profile city is mapped to the region filter for all event queries and recommendations.
- Date filters for recommendations panel are automatically set to this week's range (Monday-Sunday).

### Fixed
- Prevented events from other cities/regions (e.g., Freiburg) from appearing in recommendations when user preference is set.
- Ensured consistent event filtering logic between chatbot and recommendations panel.

### Changed
- Refactored `components/ui.py` and `components/chatbot_service.py` to enforce user preference and date logic for all event queries.

### Release
- This release completes the "chatbot backend logic" milestone for EventBot.

---

## [0.3.0] - 2025-09-22
### Added
- Modernized and visually integrated main header and subheading (see `static/header.html`, `static/eventbot.css`, `assets/chat_header.html`).
- Recommendations panel cleaned up: removed redundant horizontal rule and dividers for a cleaner look.

### Changed
- Chat input area fully refactored: always interactive, Send button never disabled, Enter and Send both submit, empty messages are ignored with a warning.
- Spinner logic deduplicated: spinner only appears once, inside the chat card.
- Header and subheading are now horizontally aligned and visually modern.

### Fixed
- Removed all redundant UI elements: duplicate spinners, unnecessary horizontal rules, and excess whitespace.
- All frontend UI/UX issues resolved for a robust, user-friendly, and visually appealing chat and recommendations experience.

### Release
- This release completes the "finished frontend" milestone for EventBot.

### Fixed
- Chat input: Send button is always enabled and both Enter and Send submit the message
### Changed
- Chat input now uses Streamlit form and form_submit_button for consistent behavior
### Open Points
- User chat input still sometimes displays as code block if backend or other logic returns HTML—needs further backend sanitization.
---
## [0.2.1] - 2025-09-22
### Fixed
- Fixed: User chat input and quick replies now always store and display only plain text, never HTML or code blocks.
### Changed
- Improved chat UI logic for Streamlit rerun model: user messages, spinner, and bot responses are shown in correct sequence.
### Open Points
- User chat input still sometimes displays as code block if backend or other logic returns HTML—needs further backend sanitization.
👋 Hi! I'm <b>EventMate</b>, your friendly companion for discovering fun things to do. Your preferences are set up and used only for recommendations. Looking for something fun this weekend? Just ask or see my recommendations below!






## [0.2.0] - 2025-09-19
### Added
- Aggressively reduced all vertical whitespace above and around the chat card and onboarding/info box using global and targeted CSS.
- All custom HTML/CSS removed from Python logic; now loaded from static files for maintainability.

### Fixed
- Eliminated persistent whitespace above the onboarding/info box and chat card.
### Fixed
- Resolved infinite rerun loop in `streamlit_chatbot.py` that caused a white screen in Streamlit UI.
- Now, `st.rerun()` is only called after user input or quick reply selection, not after every message append.

## [0.1.2] - 2025-09-18
### Changed
- Synchronised chatbot and recommendation system: both now always use the same, up-to-date filters and profile from session state for chat and sidebar recommendations.
