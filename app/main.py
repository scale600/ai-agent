import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from config.settings import GCP_PROJECT_ID

st.set_page_config(
    page_title="AI Agent — GCP IAM Audit",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @media (max-width: 576px) {
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.15rem !important; }
        h3 { font-size: 1rem !important; }
    }
    pre { overflow-x: auto; white-space: pre; }
    [data-testid="stTable"] { overflow-x: auto; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar (shared across all pages) ──────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <div style="display:flex; gap:14px; align-items:center; margin-bottom:12px;">
                <a href="https://project.techcloudup.com" target="_blank" title="TechCloudUp">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#9e9e9e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="2" y1="12" x2="22" y2="12"/>
                        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                    </svg>
                </a>
                <a href="https://linkedin.com/in/scale600" target="_blank" title="LinkedIn">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="#9e9e9e">
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                </a>
                <a href="https://github.com/scale600/ai-agent" target="_blank" title="GitHub">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="#9e9e9e">
                        <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.230 3.297-1.230.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                    </svg>
                </a>
            </div>
            <h3 style="margin:0; font-size:1.5rem;">🔐 AI Agent</h3>
            <p style="margin:4px 0 0 0; font-size:0.85rem; color:#9e9e9e;">GCP IAM Audit Agent · Google ADK + Gemini on Vertex AI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    project_id = st.text_input(
        "GCP Project ID",
        value=GCP_PROJECT_ID,
        placeholder="your-project-id",
        key="sidebar_project_id",
    )

    st.markdown("**Example prompts**")
    examples = [
        "Audit IAM policies and generate a full security report",
        "Find service accounts with excessive permissions",
        "Check for public access (allUsers) in IAM bindings",
    ]
    for example in examples:
        if st.button(example, use_container_width=True, key=f"sidebar_ex_{example[:20]}"):
            st.session_state.pending_prompt = example
            st.switch_page("pages/audit.py")

# ── Navigation ────────────────────────────────────────────────────────────────
pg = st.navigation([
    st.Page("pages/audit.py", title="IAM Audit", icon="🔐"),
    st.Page("pages/about.py", title="About", icon="ℹ️"),
    st.Page("pages/how_it_works.py", title="How it Works", icon="🔧"),
])

pg.run()
