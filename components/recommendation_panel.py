import streamlit as st
from components.ui import render_event_recommendations

class RecommendationPanel:
    @staticmethod
    def render(filters):
        import copy
        filters = copy.deepcopy(filters)  # Always work on a copy to prevent mutation
        from befriends.recommendation.service import RecommendationService
        from befriends.catalog.repository import CatalogRepository
        repo = CatalogRepository()
        recommender = RecommendationService(repo)
        st.markdown('<div class="recommendations-panel">', unsafe_allow_html=True)
        try:
            render_event_recommendations(filters=filters)
        except Exception as e:
            st.error(f"Failed to load recommendations: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
