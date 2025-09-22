# Changelog

## [0.2.1] - 2025-09-22
### Fixed
- Fixed: User chat input and quick replies now always store and display only plain text, never HTML or code blocks.
- Fixed: Assistant responses are stripped of HTML before display, preventing raw HTML/code block artifacts in chat.
- Fixed: Chatbot response and "EventBot is thinking" spinner now reliably display in correct order after user input.

### Changed
- Improved chat UI logic for Streamlit rerun model: user messages, spinner, and bot responses are shown in correct sequence.

### Open Points
- User chat input still sometimes displays as code block if backend or other logic returns HTML—needs further backend sanitization.
- Review all message formatting for edge cases (Markdown, emoji, etc.).
- Test with more diverse user/assistant message content.

👋 Hi! I'm <b>EventMate</b>, your friendly companion for discovering fun things to do. Your preferences are set up and used only for recommendations. Looking for something fun this weekend? Just ask or see my recommendations below!






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
