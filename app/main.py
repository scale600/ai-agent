import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="AI Agent — GCP IAM Audit",
    page_icon="🔐",
    layout="wide",
)

# ── Sidebar header (shared across all pages) ──────────────────────────────────
with st.sidebar:
    st.title("🔐 AI Agent")
    st.caption("GCP IAM Audit Agent · Google ADK + Gemini on Vertex AI")

# ── Navigation ────────────────────────────────────────────────────────────────
pg = st.navigation([
    st.Page("pages/audit.py", title="IAM Audit", icon="🔐"),
    st.Page("pages/about.py", title="About", icon="ℹ️"),
    st.Page("pages/how_it_works.py", title="How it Works", icon="🔧"),
])

pg.run()
