import streamlit as st

html = '''
<div class="event-card">
    <div class="event-card-row">
        <div class="event-main">
            <div class="event-title">Campus Open Day Universität Freiburg</div>
            <div class="event-meta">2026-06-05 • Universität Freiburg</div>
            <div class="event-pills"><span class="pill category bildung">Bildung / Tag der offenen Tür</span> <span class="pill price">kostenlos</span></div>
        </div>
    </div>
    <div class="event-desc">Bildung / Tag der offenen Tür</div>
    <div class="event-footer">
        <button class="primary">View & Book</button>
        <div class="event-footer-actions">
            <button class="icon" title="Save">★</button>
            <button class="icon" title="Share">🔗</button>
        </div>
    </div>
</div>
'''

st.markdown(html, unsafe_allow_html=True)
