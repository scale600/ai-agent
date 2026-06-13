# ai-agentic — PRD (Product Requirements Document)

> **목적:** Google ADK + Gemini on Vertex AI 기반 Agentic AI 데모 프로젝트  
> **작성일:** 2026-06-13  
> **상태:** 실행 중

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | `ai-agentic` |
| GitHub Repo | `github.com/scale600/ai-agentic` |
| Live Demo | `ai-agentic.techcloudup.com` |
| 한 줄 설명 | GCP IAM 감사(Audit) 자동화 Agentic AI — 자연어 요청 → 실제 GCP API 실행 → 리포트 생성 |

---

## 2. 목표 (Goals)

- Google ADK + Gemini on Vertex AI 스택으로 Agentic AI가 실제로 어떻게 동작하는지 데모
- 자연어 → GCP API 실행 → 리포트 생성까지 end-to-end 흐름을 직접 구현해서 보여주기
- ReAct 패턴, tool calling, multi-agent 구조를 실제 동작하는 코드로 확인
- `ai-agentic.techcloudup.com` 에서 누구나 바로 실행해볼 수 있는 라이브 데모 제공

## 3. 비목표 (Non-Goals)

- ~~AWS 비용 최적화, 보안 스캔, 리소스 추천 등 복수 기능~~ → v2로 이동
- ~~Vertex AI Agent Engine 배포~~ → 비용/안정성 이유로 Cloud Run 우선
- ~~CrewAI 통합~~ → ADK + LangChain 조합으로 충분

---

## 4. 데모 시나리오 (v1 Scope)

> **단 하나의 시나리오를 깊고 완성도 있게** — "GCP IAM Audit Agent"

### 사용자 흐름

```
[사용자 자연어 입력]
"프로젝트 my-project-123의 IAM 정책 감사해줘.
 과도한 권한 가진 서비스 계정 찾아서 리포트 만들어줘."

        ↓

[Agent — Perceive]
→ LlmAgent가 요청을 분석, 필요한 Tool 결정

        ↓

[Agent — Reason (Gemini 2.5 Flash)]
→ ReAct 패턴: Think → Act → Observe → Think...
→ 호출 Tool 순서 계획: get_iam_policy → analyze_roles → generate_report

        ↓

[Agent — Act (Tool Calling)]
→ get_iam_policy(project_id)     # GCP Resource Manager API
→ list_service_accounts(project) # GCP IAM API
→ check_role_permissions(roles)  # 권한 분석

        ↓

[Agent — Report]
→ 과도한 권한 목록 + 개선 권고사항 Markdown 리포트 생성
→ Streamlit UI에 표시
```

### v2 확장 계획 (v1 완성 후)

- AWS IAM audit 추가 (boto3)
- GCP 비용 이상 감지 (Cloud Billing API)
- Slack 알림 연동

---

## 5. 기술 스택

### ⭐ Core (핵심)

| 계층 | 기술 | 버전 | 비고 |
|------|------|------|------|
| **Platform** | **Vertex AI** | — | GCP 관리형 AI 플랫폼 — Gemini 엔드포인트, 모니터링, 스케일링 제공 |
| **AI Framework** | **Google ADK** | `>=1.0.0` | 메인 Agent 오케스트레이션 — multi-agent, ReAct, tool calling 지원 |
| **AI Framework** | **LangChain** | `>=0.3.0` | Tool wrapper — ADK와 결합해 확장 가능한 Tool 생태계 구성 |
| LLM | Gemini 2.5 Flash | `gemini-2.5-flash` | Vertex AI 통해 호출 — 빠른 응답속도로 라이브 데모 적합 |
| Language | Python | `3.11+` | |

### Infrastructure

| 계층 | 기술 | 비고 |
|------|------|------|
| 배포 | Cloud Run | 서버리스, 커스텀 도메인, 콜드스타트 주의 |
| 인증 | Workload Identity / Service Account | SA key 파일 사용 금지 — Secret Manager 사용 |
| 도메인 | Cloudflare DNS → Cloud Run | CNAME 설정 |
| UI | Streamlit | `>=1.35.0` |
| IaC | Terraform | Cloud Run, IAM, Secret Manager 관리 |
| CI/CD | GitHub Actions | main push → Cloud Run 자동 배포 |

### 보안 (필수)

```
❌ 금지: SA key JSON 파일을 코드/환경변수에 직접 포함
✅ 허용: 
  - 로컬: gcloud auth application-default login
  - Cloud Run: Workload Identity 또는 Secret Manager
  - GitHub Actions: Workload Identity Federation (OIDC)
```

---

## 6. 프로젝트 구조

```
ai-agentic/
├── app/
│   ├── main.py               # Streamlit Chat UI
│   └── agent_client.py       # ADK Agent 호출 래퍼
├── agents/
│   ├── supervisor.py         # ADK LlmAgent (오케스트레이터)
│   └── iam_audit_agent.py    # IAM Audit 전용 Agent (sub-agent)
├── tools/
│   ├── gcp_iam_tools.py      # GCP IAM API 래퍼 (Tool 정의)
│   └── report_tools.py       # Markdown 리포트 생성
├── config/
│   └── settings.py           # 환경변수 로드 (python-dotenv)
├── terraform/
│   ├── main.tf               # Cloud Run, IAM, Secret Manager
│   ├── variables.tf
│   └── outputs.tf
├── .github/
│   └── workflows/
│       └── deploy.yml        # Cloud Run 자동 배포
├── Dockerfile
├── requirements.txt
├── .env.example              # 환경변수 템플릿 (실제 값 제외)
└── README.md
```

---

## 7. 구현 로드맵

### Day 1 — 환경 설정

```bash
# GCP 설정
gcloud projects create ai-agentic-demo --name="AI Agentic Demo"
gcloud services enable \
  aiplatform.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com

# Python 환경
python -m venv .venv && source .venv/bin/activate

# 패키지 설치 전 버전 확인
pip index versions google-adk
pip install google-adk langchain langchain-google-vertexai streamlit python-dotenv

# 로컬 인증
gcloud auth application-default login
```

### Day 2~3 — Core Agent 구현

- `tools/gcp_iam_tools.py`: `get_iam_policy()`, `list_service_accounts()`, `analyze_permissions()` Tool 정의
- `agents/iam_audit_agent.py`: ADK `LlmAgent` + ReAct 패턴
- `agents/supervisor.py`: 멀티 에이전트 오케스트레이션 (Supervisor → IAM Audit Agent)
- 로컬 테스트: `python -m pytest tests/` + 실제 GCP 프로젝트에서 수동 검증

### Day 4~5 — UI + 연동

- `app/main.py`: Streamlit Chat 인터페이스
  - 사이드바: 프로젝트 ID 입력, 예시 프롬프트
  - 메인: 대화 + Agent 실행 과정(Reasoning trace) 표시
  - 결과: Markdown 리포트 렌더링
- 로컬 실행: `streamlit run app/main.py`

### Day 6~7 — 배포

- `Dockerfile` 작성 및 `docker build` 로컬 테스트
- Terraform으로 Cloud Run + IAM 프로비저닝
- GitHub Actions `deploy.yml` 설정 (Workload Identity Federation)
- Cloudflare DNS: `ai-agentic.techcloudup.com` CNAME → Cloud Run URL

### Day 8 — 문서화 & 마무리

- `README.md`: Architecture diagram, 데모 GIF, 시작 가이드
- GitHub Topics 설정: `agentic-ai` `vertex-ai` `google-adk` `gemini` `langchain` `gcp` `python`

---

## 8. 비용 예상

| 서비스 | 예상 비용 | 비고 |
|--------|----------|------|
| Vertex AI (Gemini 2.5 Flash) | ~$1~5/월 | 데모 트래픽 기준 |
| Cloud Run | ~$0~2/월 | 요청 기반 과금 |
| Secret Manager | ~$0.06/월 | |
| **합계** | **~$5~10/월** | 라이브 데모 운영에 충분 |

> Gemini 2.5 Pro는 Flash 대비 5~10배 비쌈. 데모는 Flash로 시작, 필요시 전환.

---

## 9. 완성 기준

- [ ] 자연어 입력 → GCP IAM 실제 API 호출 → 리포트 생성 end-to-end 동작 확인
- [ ] `ai-agentic.techcloudup.com` 에서 외부 접속 + 실행 가능
- [ ] Agent의 Reasoning trace(생각 과정)가 UI에 실시간으로 표시됨
- [ ] ADK multi-agent (Supervisor + Sub-agent) 구조 실제 동작
- [ ] GitHub README에 Architecture diagram + 데모 스크린샷 포함

---

## 10. 다음 단계 선택

실행 준비 완료. 아래 중 원하는 것부터 시작:

| # | 작업 | 예상 시간 |
|---|------|----------|
| A | `tools/gcp_iam_tools.py` 전체 코드 작성 | 1시간 |
| B | `agents/` ADK Agent 코드 초안 | 1시간 |
| C | `app/main.py` Streamlit UI 초안 | 30분 |
| D | `Dockerfile` + `terraform/` 설정 | 1시간 |
| E | `GitHub Actions` CI/CD 파이프라인 | 30분 |

---

## 11. 구축 체크리스트

> 위에서 아래 순서대로 진행. 각 단계 완료 후 체크.

### Phase 1 — GCP 환경 준비

- [x] GCP 프로젝트 생성 (`ai-agentic-2026`)
- [x] Vertex AI API 활성화 (`aiplatform.googleapis.com`)
- [x] IAM API 활성화 (`iam.googleapis.com`)
- [x] Cloud Resource Manager API 활성화 (`cloudresourcemanager.googleapis.com`)
- [x] Cloud Run API 활성화 (`run.googleapis.com`)
- [x] Secret Manager API 활성화 (`secretmanager.googleapis.com`)
- [x] 로컬 인증 설정 (`gcloud auth application-default login`)

### Phase 2 — 로컬 개발 환경

- [x] 프로젝트 폴더 생성 (`ai-agentic/`)
- [x] Python 가상환경 생성 및 활성화 (`.venv`)
- [x] ADK 버전 확인 → `2.2.0` 최신 확인
- [x] 패키지 설치 (`google-adk==2.2.0`, `langchain`, `langchain-google-vertexai`, `streamlit`, `python-dotenv`)
- [x] `requirements.txt` 작성
- [x] `.env.example` 작성 (환경변수 템플릿)
- [x] `.gitignore` 설정 (`.env`, `*.json` 키파일 제외)
- [x] GitHub 레포 생성 (`ai-agentic`) 및 초기 커밋

### Phase 3 — Tools 구현

- [x] `tools/gcp_iam_tools.py` — `get_iam_policy()` 구현 및 단독 실행 테스트
- [x] `tools/gcp_iam_tools.py` — `list_service_accounts()` 구현 및 테스트
- [x] `tools/gcp_iam_tools.py` — `analyze_permissions()` 구현 및 테스트
- [x] `tools/report_tools.py` — Markdown 리포트 생성 함수 구현
- [x] 각 Tool을 실제 GCP 프로젝트에 실행해서 응답 확인

### Phase 4 — Agent 구현

- [ ] `agents/iam_audit_agent.py` — ADK `LlmAgent` 기본 구조 작성
- [ ] `agents/iam_audit_agent.py` — Tool 연결 및 ReAct 패턴 동작 확인
- [ ] `agents/supervisor.py` — Supervisor Agent 작성
- [ ] `agents/supervisor.py` — Sub-agent(`iam_audit_agent`) 오케스트레이션 연결
- [ ] CLI로 end-to-end 실행 테스트 (`python agents/supervisor.py`)

### Phase 5 — Streamlit UI

- [ ] `app/agent_client.py` — Agent 호출 래퍼 작성
- [ ] `app/main.py` — 기본 Chat 인터페이스 작성
- [ ] 사이드바: GCP 프로젝트 ID 입력 필드 + 예시 프롬프트 버튼
- [ ] 메인: Reasoning trace 실시간 표시 구현
- [ ] 결과: Markdown 리포트 렌더링 확인
- [ ] `streamlit run app/main.py` 로컬 동작 최종 확인

### Phase 6 — 컨테이너화 & 배포

- [ ] `Dockerfile` 작성 및 `docker build` 로컬 테스트
- [ ] `docker run` 으로 컨테이너 정상 동작 확인
- [ ] `terraform/main.tf` 작성 (Cloud Run, IAM, Secret Manager)
- [ ] `terraform init && terraform plan` 확인
- [ ] `terraform apply` — Cloud Run 서비스 프로비저닝
- [ ] Secret Manager에 환경변수 등록
- [ ] Cloud Run 배포 후 URL 정상 접속 확인

### Phase 7 — CI/CD + 도메인

- [ ] GitHub Actions `deploy.yml` 작성
- [ ] Workload Identity Federation 설정 (SA key 없이 배포)
- [ ] main 브랜치 push → 자동 배포 동작 확인
- [ ] Cloudflare DNS: `ai-agentic.techcloudup.com` CNAME 레코드 추가
- [ ] HTTPS 접속 및 외부 실행 최종 확인

### Phase 8 — 문서화

- [ ] `README.md` 작성 (프로젝트 설명, Architecture diagram, 시작 가이드)
- [ ] 데모 스크린샷 또는 GIF 캡처해서 README에 삽입
- [ ] GitHub Topics 설정: `agentic-ai` `vertex-ai` `google-adk` `gemini` `langchain` `gcp` `python`
- [ ] 완성 기준 9개 항목 전체 체크 완료 확인
