import streamlit as st

st.title("About")
st.caption("GCP IAM Audit Agent — Google ADK + Gemini on Vertex AI")

st.markdown("""
This is a live demo of an **Agentic AI** system that automates GCP IAM security audits.

You describe what you want in plain English — the Agent figures out which GCP APIs to call,
executes them in sequence, reasons about the results, and produces a structured audit report.
No scripting. No manual API calls.

---

### Why this exists

Most IAM audit tools are scripts that run a fixed set of checks.
This demo shows a different model: a **reasoning agent** that can adapt its approach based on what it finds.

> "Find service accounts with owner-level access and check if any of them have been
> inactive for more than 90 days" — that kind of flexible, multi-step query is where
> agents shine over fixed scripts.

---

### Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Framework | [Google ADK](https://google.github.io/adk-docs/) 2.2 |
| LLM | Gemini 2.5 Flash via Vertex AI |
| Pattern | ReAct (Reason + Act) multi-agent |
| UI | Streamlit 1.58 |
| Deployment | Cloud Run (serverless) |
| IaC | Terraform |
| CI/CD | GitHub Actions + Workload Identity Federation |

---

### Source

[![GitHub](https://img.shields.io/badge/GitHub-scale600/ai--agent-181717?logo=github&style=flat-square)](https://github.com/scale600/ai-agent)

Licensed under MIT. Contributions welcome.
""")
