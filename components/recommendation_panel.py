import streamlit as st
from components.ui import render_event_recommendations

class RecommendationPanel:
    @staticmethod
    def render(filters):
        st.markdown('<div class="recommendations-panel">', unsafe_allow_html=True)
        try:
            render_event_recommendations(filters=filters)
        except Exception as e:
            st.error(f"Failed to load recommendations: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
