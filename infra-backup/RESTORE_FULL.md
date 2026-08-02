# 🔄 Full IAM Audit Service Restore Guide

> Restore the original agentic AI service with Gemini + Vertex AI + GCP API tools.

---

## What gets restored

| Layer | Change | Restore action |
|---|---|---|
| **App code** | `audit.py`, `agent_client.py`, `agents/`, `tools/`, `config/` deleted | `git checkout` from pre-archive commit |
| **Dependencies** | google-adk, google-cloud-*, google-genai removed | Restore `requirements.txt` |
| **Navigation** | Audit page removed from nav | Restore `app/main.py` |
| **Dockerfile** | PYTHONPATH removed | Restore `Dockerfile` |
| **IAM** | 3 roles removed from SA | Re-add via `gcloud` |
| **Cloud Run** | CPU/ram reduced, env vars stripped | Restore via `gcloud` |

---

## Step-by-step

### 1. Restore source code from git

The files were deleted in commit `05f9f69`. Restore from the commit right before it (`9d90a04`):

```bash
git checkout 9d90a04 -- \
  app/pages/audit.py \
  app/agent_client.py \
  agents/ \
  tools/ \
  config/settings.py \
  requirements.txt \
  Dockerfile \
  app/main.py
```

### 2. Restore IAM permissions

```bash
SA="ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com"
PROJECT="ai-agentic-2026"

gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA" --role="roles/iam.securityReviewer"

gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA" --role="roles/iam.serviceAccountViewer"

gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA" --role="roles/aiplatform.user"
```

### 3. Restore Cloud Run resources & env vars

```bash
gcloud run services update ai-agent \
  --region=us-central1 \
  --cpu=1 --memory=1Gi --concurrency=80 \
  --no-cpu-throttling \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=true,GCP_PROJECT_ID=ai-agentic-2026,GCP_REGION=us-central1,GEMINI_MODEL=gemini-2.5-flash" \
  --project=ai-agentic-2026
```

### 4. Commit & deploy

```bash
git add -A
git commit -m "Restore IAM Audit service with Vertex AI + GCP API tools"
git push
# CI/CD auto-deploys to Cloud Run
```

### 5. Verify

```bash
# Check service status
gcloud run services describe ai-agent --region=us-central1 --format="value(status.url)"

# Test the audit endpoint
curl -s -o /dev/null -w "%{http_code}" https://ai-agent.techcloudup.com/
```

---

## Cost impact after restore

| Item | Monthly estimate |
|---|---|
| Cloud Run (1 CPU, 1Gi) | ~$2–5 |
| Vertex AI (Gemini 2.5 Flash) | ~$10–50 (query-dependent) |
| GCP API calls (IAM, Resource Manager) | ~$0.10 |
| Artifact Registry | ~$1–2 |
| **Total (estimated)** | **~$15–60/month** |

Budget alert is set at **$10/month**. Expect it to trigger.

---

## One-liner

```bash
git checkout 9d90a04 -- app/pages/audit.py app/agent_client.py agents/ tools/ config/settings.py requirements.txt Dockerfile app/main.py && git add -A && git commit -m "Restore IAM Audit service" && git push
```

> ⚠️ The IAM permissions and Cloud Run env vars must be restored separately via the `gcloud` commands above — they are not in git.
