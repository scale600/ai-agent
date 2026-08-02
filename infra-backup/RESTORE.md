# 🔄 Infrastructure Restore Guide

> Last backup: **2026-08-02** — Project: `ai-agentic-2026`

This guide documents how to fully restore GCP resources after deletion, so the same configuration can be recreated at any time.

---

## 📦 Backup Contents

| File | Description |
|---|---|
| `terraform.tfstate` | Terraform state (most critical — without this, manual resource import is required) |
| `terraform.tfstate.backup` | Terraform state backup |
| `cloud-run-service.yaml` | Full Cloud Run service config (env vars, resources, scaling) |
| `domain-mappings.yaml` | Custom domain mappings (`ai-agent.techcloudup.com`, `ai-agentic.techcloudup.com`) |
| `iam-policy.yaml` | Project IAM policy (SA roles, user roles) |
| `service-account.yaml` | Cloud Run service account (`ai-agent-sa`) |
| `artifact-registry.yaml` | Artifact Registry repository config |
| `docker-images.yaml` | Registered Docker image list |
| `wif-pool.yaml` | Workload Identity Federation Pool |
| `wif-provider.yaml` | WIF Provider (GitHub OIDC) |

---

## ⚠️ Prerequisites

```bash
# 1. gcloud authentication
gcloud auth login wonhee.lee.ok@gmail.com
gcloud auth application-default login

# 2. Project configuration
gcloud config set project ai-agentic-2026
gcloud config set compute/region us-central1

# 3. Link billing account (if new project)
# GCP Console → Billing → Link billing account: 010684-CD0CA1-65C083

# 4. Domain DNS setup (techcloudup.com)
# ai-agent.techcloudup.com  → CNAME → ghs.googlehosted.com
# ai-agentic.techcloudup.com → CNAME → ghs.googlehosted.com

# 5. GitHub Secrets configuration
# Repo: scale600/ai-agent → Settings → Secrets and variables → Actions
#   WIF_PROVIDER: projects/1004402056084/locations/global/workloadIdentityPools/github-pool/providers/github-provider
#   GCP_SERVICE_ACCOUNT: ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com
#   GCP_PROJECT_ID: ai-agentic-2026
```

---

## 🚀 Method 1: Restore via Terraform (Recommended)

The Terraform state file exists, so existing resources can be managed as-is.

```bash
# 1. Enable required APIs
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  aiplatform.googleapis.com \
  --project=ai-agentic-2026

# 2. Initialize Terraform and restore state
cd terraform
cp ../infra-backup/terraform.tfstate .
cp ../infra-backup/terraform.tfstate.backup .

terraform init
terraform plan -var="project_id=ai-agentic-2026"

# 3. If state has drifted, refresh then apply
terraform apply -var="project_id=ai-agentic-2026"
```

> ⚠️ **The state file is critical.** Without it, you must manually import every resource via `terraform import`.

---

## 🛠️ Method 2: Manual Restore via gcloud CLI

If Terraform state is lost, follow these steps in order.

### Step 1: Enable APIs

```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  iamcredentials.googleapis.com \
  --project=ai-agentic-2026
```

### Step 2: Create Artifact Registry

```bash
gcloud artifacts repositories create ai-agent \
  --location=us-central1 \
  --repository-format=DOCKER \
  --project=ai-agentic-2026
```

### Step 3: Create Service Account and Grant Permissions

```bash
# Create SA
gcloud iam service-accounts create ai-agent-sa \
  --display-name="AI Agent App Service Account" \
  --project=ai-agentic-2026

# Grant IAM permissions
gcloud projects add-iam-policy-binding ai-agentic-2026 \
  --member="serviceAccount:ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com" \
  --role="roles/iam.securityReviewer"

gcloud projects add-iam-policy-binding ai-agentic-2026 \
  --member="serviceAccount:ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountViewer"

gcloud projects add-iam-policy-binding ai-agentic-2026 \
  --member="serviceAccount:ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ai-agentic-2026 \
  --member="serviceAccount:ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com" \
  --role="roles/run.developer"

gcloud projects add-iam-policy-binding ai-agentic-2026 \
  --member="serviceAccount:ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### Step 4: Build & Push Docker Image

```bash
REGISTRY=us-central1-docker.pkg.dev/ai-agentic-2026/ai-agent/app

docker buildx build --platform linux/amd64 \
  -t $REGISTRY:latest \
  --push .
```

### Step 5: Deploy to Cloud Run

```bash
gcloud run deploy ai-agent \
  --image=us-central1-docker.pkg.dev/ai-agentic-2026/ai-agent/app:latest \
  --region=us-central1 \
  --service-account=ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com \
  --cpu=1 \
  --memory=1Gi \
  --min-instances=0 \
  --max-instances=1 \
  --port=8080 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=ai-agentic-2026,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=true,GCP_PROJECT_ID=ai-agentic-2026,GCP_REGION=us-central1,GEMINI_MODEL=gemini-2.5-flash" \
  --project=ai-agentic-2026
```

### Step 6: Connect Custom Domain

```bash
gcloud beta run domain-mappings create \
  --service=ai-agent \
  --domain=ai-agent.techcloudup.com \
  --region=us-central1
```

Add `CNAME` record to DNS:
- `ai-agent` → `ghs.googlehosted.com`

> SSL certificates are automatically provisioned (~10-15 minutes).

### Step 7: Restore WIF (GitHub Actions CI/CD)

```bash
# WIF Pool
gcloud iam workload-identity-pools create github-pool \
  --location=global \
  --display-name="GitHub Actions Pool" \
  --project=ai-agentic-2026

# WIF Provider (OIDC)
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='scale600/ai-agentic' || assertion.repository=='scale600/ai-agent'" \
  --project=ai-agentic-2026

# WIF → SA permission binding
gcloud iam service-accounts add-iam-policy-binding \
  ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com \
  --member="principalSet://iam.googleapis.com/projects/1004402056084/locations/global/workloadIdentityPools/github-pool/attribute.repository/scale600/ai-agent" \
  --role="roles/iam.workloadIdentityUser" \
  --project=ai-agentic-2026
```

> ⚠️ The WIF Pool project number (`1004402056084`) changes if the project is deleted and recreated. Replace with the new number.

### Step 8: Set GitHub Secrets

Repository `scale600/ai-agent` → **Settings → Secrets and variables → Actions**:

| Secret | Value |
|---|---|
| `WIF_PROVIDER` | `projects/1004402056084/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | `ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com` |
| `GCP_PROJECT_ID` | `ai-agentic-2026` |

---

## ✅ Verification

```bash
# 1. Check Cloud Run service status
gcloud run services describe ai-agent --region=us-central1

# 2. Get service URL
gcloud run services describe ai-agent --region=us-central1 --format="value(status.url)"

# 3. Connection test
curl -I https://ai-agent.techcloudup.com

# 4. Streamlit health check
curl https://ai-agent.techcloudup.com/_stcore/health
```

---

## 📊 Infrastructure Summary

| Resource | Name | Details |
|---|---|---|
| Project | `ai-agentic-2026` | Project Number: `1004402056084` |
| Billing | `010684-CD0CA1-65C083` | AI Agentic Demo |
| Region | `us-central1` | |
| Service Account | `ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com` | IAM Reviewer, SA Viewer, Vertex AI User |
| Cloud Run | `ai-agent` | 1 CPU, 1Gi RAM, min=0, max=1 |
| Artifact Registry | `us-central1-docker.pkg.dev/ai-agentic-2026/ai-agent` | DOCKER format |
| Domain | `ai-agent.techcloudup.com` | CNAME → ghs.googlehosted.com |
| WIF Pool | `github-pool` (global) | GitHub Actions OIDC |
| WIF Provider | `github-provider` | issuer: token.actions.githubusercontent.com |
| Docker Image | `python:3.11-slim` based | Streamlit port 8080 |
| Gemini Model | `gemini-2.5-flash` | via Vertex AI |

---

## 🗑️ Resource Cleanup (Shutdown)

```bash
# 1. Delete Cloud Run service
gcloud run services delete ai-agent --region=us-central1 --quiet

# 2. Delete domain mappings
gcloud beta run domain-mappings delete ai-agent.techcloudup.com --region=us-central1 --quiet

# 3. Delete Artifact Registry images then repository
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/ai-agentic-2026/ai-agent/app --delete-tags --quiet
gcloud artifacts repositories delete ai-agent --location=us-central1 --quiet

# 4. Delete service account
gcloud iam service-accounts delete \
  ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com --quiet

# 5. Delete WIF
gcloud iam workload-identity-pools providers delete github-provider \
  --workload-identity-pool=github-pool --location=global --quiet
gcloud iam workload-identity-pools delete github-pool --location=global --quiet

# 6. (Optional) Disable unused APIs
gcloud services disable run.googleapis.com --project=ai-agentic-2026 --force
```
