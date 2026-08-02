import streamlit as st

st.title("AI Agentic Project")
st.caption("GCP IAM Security Audit Agent — Project Archive")

st.markdown("""
This project was a live demo of an **Agentic AI** system that automated GCP IAM security audits
using Google ADK + Gemini 2.5 Flash on Vertex AI.

> ⚠️ **Status: Archived** — The IAM audit service has been decommissioned to reduce GCP costs.
> This page serves as the project portfolio and documentation.

---

### What it did

Users described what they wanted in plain English — the Agent figured out which GCP APIs to call,
executed them in sequence, reasoned about the results, and produced structured audit reports.

**Example queries:**
- *"Audit IAM policies and generate a full security report"*
- *"Find service accounts with excessive permissions"*
- *"Check for public access (allUsers) in IAM bindings"*

---

### Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Framework | Google ADK 2.2 |
| LLM | Gemini 2.5 Flash via Vertex AI |
| Pattern | ReAct (Reason + Act) multi-agent |
| UI | Streamlit 1.58 |
| Deployment | Cloud Run (serverless) |
| IaC | Terraform |
| CI/CD | GitHub Actions + Workload Identity Federation (keyless) |

---

### Why it was built

Most IAM audit tools are scripts that run a fixed set of checks.
This demo explored a different model: a **reasoning agent** that could adapt its approach
based on what it found — demonstrating the flexibility of agentic architectures over
deterministic pipelines.

---

### Source

[![GitHub](https://img.shields.io/badge/GitHub-scale600/ai--agent-181717?logo=github&style=flat-square)](https://github.com/scale600/ai-agent)

MIT License. All infrastructure code (Terraform, Cloud Run configs, IAM policies) 
is preserved in the `infra-backup/` directory for full restoration.
""")
