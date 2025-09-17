# Changelog

## [0.1.1] - 2025-09-17
### Fixed
- Resolved infinite rerun loop in `streamlit_chatbot.py` that caused a white screen in Streamlit UI.
- Now, `st.rerun()` is only called after user input or quick reply selection, not after every message append.
- Improved app stability and user experience for the chatbot interface.
