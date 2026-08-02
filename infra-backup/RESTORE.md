# 🔄 Infrastructure Restore Guide

> Last backup: **2026-08-02** — Project: `ai-agentic-2026`

이 가이드는 GCP 리소스를 완전히 삭제한 후, 언제든 동일한 구성으로 복구할 수 있도록 작성되었습니다.

---

## 📦 Backup Contents

| 파일 | 설명 |
|---|---|
| `terraform.tfstate` | Terraform state (가장 중요 — 이게 없으면 resource import 필요) |
| `terraform.tfstate.backup` | Terraform state backup |
| `cloud-run-service.yaml` | Cloud Run 서비스 전체 설정 (환경변수, 리소스, 스케일링 등) |
| `domain-mappings.yaml` | 커스텀 도메인 매핑 (`ai-agent.techcloudup.com`, `ai-agentic.techcloudup.com`) |
| `iam-policy.yaml` | 프로젝트 IAM 정책 (SA 권한, 사용자 권한) |
| `service-account.yaml` | Cloud Run용 서비스 계정 (`ai-agent-sa`) |
| `artifact-registry.yaml` | Artifact Registry 저장소 설정 |
| `docker-images.yaml` | 등록된 Docker 이미지 목록 |
| `wif-pool.yaml` | Workload Identity Federation Pool |
| `wif-provider.yaml` | WIF Provider (GitHub OIDC) |

---

## ⚠️ 사전 준비

```bash
# 1. gcloud 인증
gcloud auth login wonhee.lee.ok@gmail.com
gcloud auth application-default login

# 2. 프로젝트 설정
gcloud config set project ai-agentic-2026
gcloud config set compute/region us-central1

# 3. Billing 계정 연결 (새 프로젝트인 경우)
# GCP Console → Billing → Link billing account: 010684-CD0CA1-65C083

# 4. 도메인 DNS 설정 (techcloudup.com)
# ai-agent.techcloudup.com  → CNAME → ghs.googlehosted.com
# ai-agentic.techcloudup.com → CNAME → ghs.googlehosted.com

# 5. GitHub Secrets 설정
# Repo: scale600/ai-agent → Settings → Secrets and variables → Actions
#   WIF_PROVIDER: projects/1004402056084/locations/global/workloadIdentityPools/github-pool/providers/github-provider
#   GCP_SERVICE_ACCOUNT: ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com
#   GCP_PROJECT_ID: ai-agentic-2026
```

---

## 🚀 방법 1: Terraform으로 복구 (권장)

Terraform state 파일이 있으므로 기존 리소스를 그대로 관리할 수 있습니다.

```bash
# 1. 필요한 API 활성화
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  aiplatform.googleapis.com \
  --project=ai-agentic-2026

# 2. Terraform 초기화 및 state 복원
cd terraform
cp ../infra-backup/terraform.tfstate .
cp ../infra-backup/terraform.tfstate.backup .

terraform init
terraform plan -var="project_id=ai-agentic-2026"

# 3. 상태에 차이가 있다면 refresh 후 apply
terraform apply -var="project_id=ai-agentic-2026"
```

> ⚠️ **State 파일이 중요합니다.** 이 파일이 없으면 `terraform import`로 모든 리소스를 수동 import 해야 합니다.

---

## 🛠️ 방법 2: gcloud CLI로 수동 복구

Terraform state가 유실된 경우 아래 순서대로 복구합니다.

### Step 1: API 활성화

```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  iamcredentials.googleapis.com \
  --project=ai-agentic-2026
```

### Step 2: Artifact Registry 생성

```bash
gcloud artifacts repositories create ai-agent \
  --location=us-central1 \
  --repository-format=DOCKER \
  --project=ai-agentic-2026
```

### Step 3: 서비스 계정 생성 및 권한 부여

```bash
# SA 생성
gcloud iam service-accounts create ai-agent-sa \
  --display-name="AI Agent App Service Account" \
  --project=ai-agentic-2026

# IAM 권한 부여
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

### Step 4: Docker 이미지 빌드 & 푸시

```bash
REGISTRY=us-central1-docker.pkg.dev/ai-agentic-2026/ai-agent/app

docker buildx build --platform linux/amd64 \
  -t $REGISTRY:latest \
  --push .
```

### Step 5: Cloud Run 배포

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

### Step 6: 도메인 연결

```bash
gcloud beta run domain-mappings create \
  --service=ai-agent \
  --domain=ai-agent.techcloudup.com \
  --region=us-central1
```

DNS에 `CNAME` 레코드 추가:
- `ai-agent` → `ghs.googlehosted.com`

> SSL 인증서는 자동으로 프로비저닝됩니다 (약 10-15분 소요).

### Step 7: WIF (GitHub Actions CI/CD) 복구

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

# WIF → SA 권한 연결
gcloud iam service-accounts add-iam-policy-binding \
  ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com \
  --member="principalSet://iam.googleapis.com/projects/1004402056084/locations/global/workloadIdentityPools/github-pool/attribute.repository/scale600/ai-agent" \
  --role="roles/iam.workloadIdentityUser" \
  --project=ai-agentic-2026
```

> ⚠️ WIF Pool의 project number(`1004402056084`)는 프로젝트가 삭제/재생성되면 변경됩니다. 새 번호로 대체하세요.

### Step 8: GitHub Secrets 설정

Repository `scale600/ai-agent` → **Settings → Secrets and variables → Actions**:

| Secret | Value |
|---|---|
| `WIF_PROVIDER` | `projects/1004402056084/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | `ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com` |
| `GCP_PROJECT_ID` | `ai-agentic-2026` |

---

## ✅ 복구 확인

```bash
# 1. Cloud Run 서비스 상태 확인
gcloud run services describe ai-agent --region=us-central1

# 2. 서비스 URL 확인
gcloud run services describe ai-agent --region=us-central1 --format="value(status.url)"

# 3. 접속 테스트
curl -I https://ai-agent.techcloudup.com

# 4. Streamlit health check
curl https://ai-agent.techcloudup.com/_stcore/health
```

---

## 📊 인프라 구성 요약

| 리소스 | 이름 | 상세 |
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

## 🗑️ 리소스 삭제 (Shutdown)

```bash
# 1. Cloud Run 서비스 삭제
gcloud run services delete ai-agent --region=us-central1 --quiet

# 2. Domain mappings 삭제
gcloud beta run domain-mappings delete ai-agent.techcloudup.com --region=us-central1 --quiet

# 3. Artifact Registry 이미지 삭제 후 저장소 삭제
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/ai-agentic-2026/ai-agent/app --delete-tags --quiet
gcloud artifacts repositories delete ai-agent --location=us-central1 --quiet

# 4. 서비스 계정 삭제
gcloud iam service-accounts delete \
  ai-agent-sa@ai-agentic-2026.iam.gserviceaccount.com --quiet

# 5. WIF 삭제
gcloud iam workload-identity-pools providers delete github-provider \
  --workload-identity-pool=github-pool --location=global --quiet
gcloud iam workload-identity-pools delete github-pool --location=global --quiet

# 6. (선택) 불필요한 API 비활성화
gcloud services disable run.googleapis.com --project=ai-agentic-2026 --force
```
