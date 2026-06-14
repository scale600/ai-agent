# ai-agent — PRD (Product Requirements Document)

> **Purpose:** Agentic AI demo project built on Google ADK + Gemini on Vertex AI  
> **Date:** 2026-06-13  
> **Status:** Nearly Complete (domain DNS propagation pending)

---

## 1. Project Overview

| Field | Details |
|-------|---------|
| Project Name | `ai-agent` |
| GitHub Repo | `github.com/scale600/ai-agent` |
| Live Demo | `ai-agent.techcloudup.com` |
| Summary | Automated GCP IAM Audit Agentic AI — natural language input → real GCP API calls → report generation |

---

## 2. Goals

- Demonstrate how Agentic AI actually works using Google ADK + Gemini on Vertex AI
- Implement and show an end-to-end flow: natural language → GCP API execution → report generation
- Validate ReAct pattern, tool calling, and multi-agent architecture through working code
- Provide a live demo at `ai-agent.techcloudup.com` that anyone can run immediately

## 3. Non-Goals

- ~~Multiple features: AWS cost optimization, security scanning, resource recommendations~~ → moved to v2
- ~~Vertex AI Agent Engine deployment~~ → Cloud Run first due to cost/stability
- ~~CrewAI integration~~ → ADK + LangChain combination is sufficient

---

## 4. Demo Scenario (v1 Scope)

> **One scenario, done deeply and completely** — "GCP IAM Audit Agent"

### User Flow

```
[User natural language input]
"Audit IAM policies for project my-project-123.
 Find service accounts with excessive permissions and generate a report."

        ↓

[Agent — Perceive]
→ LlmAgent analyzes the request and decides which Tools to call

        ↓

[Agent — Reason (Gemini 2.5 Flash)]
→ ReAct pattern: Think → Act → Observe → Think...
→ Plans tool call sequence: get_iam_policy → analyze_roles → generate_report

        ↓

[Agent — Act (Tool Calling)]
→ get_iam_policy(project_id)     # GCP Resource Manager API
→ list_service_accounts(project) # GCP IAM API
→ check_role_permissions(roles)  # Permission analysis

        ↓

[Agent — Report]
→ Generates Markdown report: excessive permissions list + remediation recommendations
→ Displayed in Streamlit UI
```

### v2 Expansion Plan (after v1 is complete)

- Add AWS IAM audit (boto3)
- GCP cost anomaly detection (Cloud Billing API)
- Slack notification integration

---

## 5. Tech Stack

### ⭐ Core

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| **Platform** | **Vertex AI** | — | GCP managed AI platform — provides Gemini endpoints, monitoring, and scaling |
| **AI Framework** | **Google ADK** | `>=1.0.0` | Main agent orchestration — supports multi-agent, ReAct, tool calling |
| **AI Framework** | **LangChain** | `>=0.3.0` | Tool wrapper — builds an extensible tool ecosystem alongside ADK |
| LLM | Gemini 2.5 Flash | `gemini-2.5-flash` | Called via Vertex AI — fast response time suited for live demo |
| Language | Python | `3.11+` | |

### Infrastructure

| Layer | Technology | Notes |
|-------|-----------|-------|
| Deployment | Cloud Run | Serverless, custom domain, watch for cold starts |
| Auth | Workload Identity / Service Account | SA key files prohibited — use Secret Manager |
| Domain | Cloudflare DNS → GCP Domain Mapping → Cloud Run | CNAME `ai-agent` → `ghs.googlehosted.com` |
| UI | Streamlit | `>=1.35.0` |
| IaC | Terraform | Manages Cloud Run, IAM, Secret Manager |
| CI/CD | GitHub Actions | Auto-deploy to Cloud Run on main push |

### Security (Required)

```
❌ Prohibited: Embedding SA key JSON files directly in code or environment variables
✅ Allowed:
  - Local: gcloud auth application-default login
  - Cloud Run: Workload Identity or Secret Manager
  - GitHub Actions: Workload Identity Federation (OIDC)
```

---

## 6. Project Structure

```
ai-agent/
├── app/
│   ├── main.py               # Streamlit entry point (st.navigation multi-page)
│   ├── agent_client.py       # ADK Agent call wrapper
│   └── pages/
│       ├── audit.py          # IAM Audit chat UI
│       ├── about.py          # About page
│       └── how_it_works.py   # Architecture + ReAct flow explanation
├── agents/
│   ├── supervisor.py         # ADK LlmAgent (orchestrator)
│   └── iam_audit_agent.py    # IAM Audit dedicated agent (sub-agent)
├── tools/
│   ├── gcp_iam_tools.py      # GCP IAM API wrapper (Tool definitions)
│   └── report_tools.py       # Markdown report generation
├── config/
│   └── settings.py           # Environment variable loading (python-dotenv)
├── terraform/
│   ├── main.tf               # Cloud Run, IAM, Secret Manager
│   ├── variables.tf
│   └── outputs.tf
├── .github/
│   └── workflows/
│       └── deploy.yml        # Cloud Run auto-deploy
├── Dockerfile
├── requirements.txt
├── .env.example              # Environment variable template (no real values)
└── README.md
```

---

## 7. Implementation Roadmap

### Day 1 — Environment Setup

```bash
# GCP setup
gcloud projects create ai-agent-demo --name="AI Agent Demo"
gcloud services enable \
  aiplatform.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com

# Python environment
python -m venv .venv && source .venv/bin/activate

# Check package versions before installing
pip index versions google-adk
pip install google-adk langchain langchain-google-vertexai streamlit python-dotenv

# Local authentication
gcloud auth application-default login
```

### Day 2~3 — Core Agent Implementation

- `tools/gcp_iam_tools.py`: Define `get_iam_policy()`, `list_service_accounts()`, `analyze_permissions()` tools
- `agents/iam_audit_agent.py`: ADK `LlmAgent` + ReAct pattern
- `agents/supervisor.py`: Multi-agent orchestration (Supervisor → IAM Audit Agent)
- Local testing: `python -m pytest tests/` + manual validation against a real GCP project

### Day 4~5 — UI + Integration

- `app/main.py`: Streamlit Chat interface
  - Sidebar: project ID input, example prompt buttons
  - Main: conversation + Agent reasoning trace display
  - Results: Markdown report rendering
- Local run: `streamlit run app/main.py`

### Day 6~7 — Deployment

- Write `Dockerfile` and test with `docker build` locally
- Provision Cloud Run + IAM with Terraform
- Set up GitHub Actions `deploy.yml` (Workload Identity Federation)
- Cloudflare DNS: `ai-agent.techcloudup.com` CNAME → Cloud Run URL

### Day 8 — Documentation & Wrap-up

- `README.md`: Architecture diagram, demo GIF, quickstart guide
- Set GitHub Topics: `agentic-ai` `vertex-ai` `google-adk` `gemini` `langchain` `gcp` `python`

---

## 8. Cost Estimate

| Service | Estimated Cost | Notes |
|---------|---------------|-------|
| Vertex AI (Gemini 2.5 Flash) | ~$1–5/month | Based on demo traffic |
| Cloud Run | ~$0–2/month | Request-based billing |
| Secret Manager | ~$0.06/month | |
| **Total** | **~$5–10/month** | Sufficient for live demo operation |

> Gemini 2.5 Pro costs 5–10x more than Flash. Start with Flash, switch if needed.

---

## 9. Completion Criteria

- [x] End-to-end flow confirmed: natural language input → real GCP IAM API call → report generation
- [ ] External access and execution available at `ai-agent.techcloudup.com` ← DNS propagation pending
- [x] Agent's reasoning trace displayed in real-time in the UI
- [x] ADK multi-agent (Supervisor + Sub-agent) structure working in practice
- [x] GitHub README includes Architecture diagram + demo screenshot

---

## 10. Next Steps

Ready to start. Pick where to begin:

| # | Task | Est. Time |
|---|------|-----------|
| A | Write full `tools/gcp_iam_tools.py` | 1 hour |
| B | Draft `agents/` ADK Agent code | 1 hour |
| C | Draft `app/main.py` Streamlit UI | 30 min |
| D | `Dockerfile` + `terraform/` setup | 1 hour |
| E | `GitHub Actions` CI/CD pipeline | 30 min |

---

## 11. Build Checklist

> Follow in order from top to bottom. Check each item off when complete.

### Phase 1 — GCP Environment Setup

- [x] Create GCP project (`ai-agentic-2026`)
- [x] Enable Vertex AI API (`aiplatform.googleapis.com`)
- [x] Enable IAM API (`iam.googleapis.com`)
- [x] Enable Cloud Resource Manager API (`cloudresourcemanager.googleapis.com`)
- [x] Enable Cloud Run API (`run.googleapis.com`)
- [x] Enable Secret Manager API (`secretmanager.googleapis.com`)
- [x] Configure local authentication (`gcloud auth application-default login`)

### Phase 2 — Local Development Environment

- [x] Create project folder (`ai-agent/`)
- [x] Create and activate Python virtual environment (`.venv`)
- [x] Check ADK version → `2.2.0` latest confirmed
- [x] Install packages (`google-adk==2.2.0`, `langchain`, `langchain-google-vertexai`, `streamlit`, `python-dotenv`)
- [x] Write `requirements.txt`
- [x] Write `.env.example` (environment variable template)
- [x] Configure `.gitignore` (exclude `.env`, `*.json` key files)
- [x] Create GitHub repo (`ai-agent`) and initial commit

### Phase 3 — Tools Implementation

- [x] `tools/gcp_iam_tools.py` — implement `get_iam_policy()` and test standalone
- [x] `tools/gcp_iam_tools.py` — implement `list_service_accounts()` and test
- [x] `tools/gcp_iam_tools.py` — implement `analyze_permissions()` and test
- [x] `tools/report_tools.py` — implement Markdown report generation function
- [x] Run each tool against a real GCP project and verify responses

### Phase 4 — Agent Implementation

- [x] `agents/iam_audit_agent.py` — write ADK `LlmAgent` base structure
- [x] `agents/iam_audit_agent.py` — connect tools and verify ReAct pattern behavior
- [x] `agents/supervisor.py` — write Supervisor Agent
- [x] `agents/supervisor.py` — connect sub-agent (`iam_audit_agent`) orchestration
- [x] End-to-end CLI test (`python agents/supervisor.py`)

### Phase 5 — Streamlit UI

- [x] `app/agent_client.py` — write Agent call wrapper
- [x] `app/main.py` — write basic Chat interface
- [x] Sidebar: GCP project ID input field + example prompt buttons
- [x] Main: implement real-time Reasoning trace display
- [x] Results: verify Markdown report rendering
- [x] Final local verification: `streamlit run app/main.py`

### Phase 6 — Containerization & Deployment

- [x] Write `Dockerfile` and test with `docker build` locally
- [x] Verify container runs correctly with `docker run`
- [x] Write `terraform/main.tf` (Cloud Run, IAM, Secret Manager)
- [x] Verify with `terraform init && terraform plan`
- [x] `terraform apply` — provision Cloud Run service
- [x] Register environment variables in Secret Manager
- [x] Verify Cloud Run URL is accessible after deployment

### Phase 7 — CI/CD + Domain

- [x] Write GitHub Actions `deploy.yml`
- [x] Configure Workload Identity Federation (deploy without SA key files)
- [x] Verify main branch push triggers auto-deploy
- [x] Google Search Console: verify domain ownership for `techcloudup.com`
- [x] GCP Domain Mapping created: `ai-agent.techcloudup.com` → `ghs.googlehosted.com`
- [ ] Cloudflare DNS: update CNAME `ai-agent` → `ghs.googlehosted.com` (was Cloud Run URL)
- [ ] Final verification: HTTPS access and external execution (`curl -I https://ai-agent.techcloudup.com`)

### Phase 8 — Documentation

- [x] Write `README.md` (project description, Architecture diagram, quickstart guide)
- [x] Capture demo screenshot or GIF and embed in README
- [x] Add multi-page Streamlit UI: About + How it Works pages
- [ ] Set GitHub Topics: `agentic-ai` `vertex-ai` `google-adk` `gemini` `gcp` `cloud-run` `python` `streamlit`
- [ ] Confirm all 5 completion criteria are checked off
