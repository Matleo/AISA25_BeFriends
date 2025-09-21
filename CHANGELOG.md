# Changelog

## [0.2.0] - 2025-09-19
### Added
- Modularized all custom HTML and CSS for the chatbot UI: header moved to `static/header.html`, all styles to `static/eventbot.css`, and chat UI logic to `components/chat_ui.py`.
- Added utility for formatting events as JSON for LLM context (`befriends/response/event_json.py`).

### Changed
- Moved the EventMate header into the chat column for a more integrated look.
- Aggressively reduced all vertical whitespace above and around the chat card and onboarding/info box using global and targeted CSS.
- All custom HTML/CSS removed from Python logic; now loaded from static files for maintainability.
- Improved onboarding/info box and quick reply UI for a visually connected, modern appearance.
- Refactored event recommendation logic to support free-text queries and improved intent detection.

### Fixed
- Eliminated persistent whitespace above the onboarding/info box and chat card.
- Fixed minor layout quirks and ensured consistent appearance across Streamlit reruns.

## [0.1.1] - 2025-09-17
### Fixed
- Resolved infinite rerun loop in `streamlit_chatbot.py` that caused a white screen in Streamlit UI.
- Now, `st.rerun()` is only called after user input or quick reply selection, not after every message append.
- Improved app stability and user experience for the chatbot interface.

## [0.1.2] - 2025-09-18
### Changed
- Synchronised chatbot and recommendation system: both now always use the same, up-to-date filters and profile from session state for chat and sidebar recommendations.
