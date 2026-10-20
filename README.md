# ResolutionOps

> **AI-Powered Customer Issue Investigation & Resolution Workbench for B2B SaaS**

ResolutionOps is an investigation workspace that bridges Tier-2/Tier-3 customer support and core engineering. Instead of tossing vague tickets, unverified logs, and scattered context over the fence, ResolutionOps unifies fragmented evidence, runs deterministic diagnostic tools, uses Gemini AI to formulate and rank root-cause hypotheses, produces structured engineering handoffs, and enforces verification gates before any incident can be resolved.

---

## 🌟 The Core Problem

When an enterprise customer reports an issue such as:
> *"Our API returned 200 for order ORD-98421 at 04:15 UTC, but dashboard says pending. Please fix ASAP!"*

Support engineers typically spend hours:
1. Asking repetitive questions back to the customer for request IDs, timestamps, and environments.
2. Manually grepping scattered application and gateway logs across disparate tools.
3. Escalating half-baked tickets to engineering with missing diagnostic evidence.
4. Prematurely marking cases "Resolved" without verifiable proof that the fix actually worked.

**ResolutionOps solves this end-to-end.**

---

## 🚀 Key Features

### 1. Intelligent Issue Intake & Triage
- Converts messy, free-text customer complaints into structured issue reports.
- Extracts correlation IDs (`order_id`, `request_id`, timestamps, environment).
- Identifies missing diagnostic evidence and automatically generates targeted customer clarification questions.

### 2. Unified Correlated Evidence Timeline
- Integrates customer messages, internal engineering notes, API traces, sanitized logs, runbooks, and diagnostic query outputs into a single chronological timeline.
- Every claim cites a verifiable evidence ID (e.g., `ev-001`, `ev-004`).

### 3. Deterministic Diagnostic Workbench
- Five safe, read-only diagnostic tools querying synthetic databases and dispatcher queues:
  - `inspect_webhook_logs`: Inspects delivery failures and HTTP 503 retry exhaustion.
  - `get_order_status`: Reconciles primary Postgres DB vs replica vs outbox state.
  - `search_application_logs`: Scans service and ingress gateway logs for status codes.
  - `compare_source_and_downstream`: Detects state divergence between source and client systems.
  - `probe_webhook_endpoint`: Read-only health probe of customer receiver endpoints.
- Every diagnostic execution automatically appends its output to the case evidence timeline.

### 4. Grounded AI Root-Cause Investigation (Gemini 2.5 Flash)
- Synthesizes timeline evidence against historical incidents and runbooks.
- Generates ranked root-cause hypotheses with confidence scores, supporting facts, contradictory evidence, and recommended tests.
- **Strict Anti-Hallucination Guardrails:** AI must ground claims in timeline IDs. If `GEMINI_API_KEY` is not provided, seamlessly falls back to a deterministic heuristic engine.

### 5. Interactive Conversational Investigation Assistant
- Slide-out assistant drawer in the case workspace allowing engineers to ask natural-language questions about case evidence in real time.
- Answers are strictly grounded in case evidence, diagnostic results, and runbooks.

### 6. Structured Engineering Handoff Dossier
- Generates a reproduction dossier for engineering escalations: customer impact, suspected root cause, sanitized log snippets, request traces, suggested owner team, and explicit acceptance criteria.
- One-click copy formatted in clean Markdown.

### 7. Resolution Verification Gate
- **Enforced Closure Gate:** Prevents premature case resolution. Attempting to mark a case as `Resolved` without passing verification criteria or documenting an authorized exception triggers an `HTTP 422 Unprocessable Content` response.

### 8. Role-Based Access Control (RBAC) & Demo Persona Switcher
- Instant persona switcher in the sidebar to simulate three enterprise roles:
  - **Support Engineer:** View cases, run diagnostic tools, add evidence notes, run AI triage.
  - **Support Lead:** Approve hypotheses, sign off on handoffs, authorize case closures.
  - **Platform Engineer:** Full system access, audit trail inspection, and synthetic data reset.

### 9. Live Operational Telemetry & Reports
- Live Mean Time to Understanding (MTTU) vs. Mean Time to Resolution (MTTR) metrics.
- Incident status distribution, priority breakdown, and customer SLA tiers.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Tailwind CSS v4, Vite 8, Lucide React, React Router 7 |
| **Backend** | Python 3.15, FastAPI, Pydantic v2, Uvicorn |
| **AI Orchestration** | Google Gen AI SDK (`google-genai`), Gemini 2.5 Flash, Defensive System Prompts |
| **Data Layer** | In-memory thread-safe data store with pre-seeded enterprise synthetic datasets |
| **Testing & Quality** | Python `unittest`, ESLint, TypeScript compiler (`tsc -b`), Vitest |

---

## 🏁 Quickstart & Local Setup

### Prerequisites
- **Node.js** (v18+)
- **Python** (v3.11+)
- **uv** (recommended) or standard Python `venv`

### 1. Clone the Repository
```bash
git clone https://github.com/valor0506/ResolutionOps.git
cd ResolutionOps
```

### 2. Install Frontend Dependencies
```bash
npm install
```

### 3. Setup Python Backend Environment
```bash
# Using uv (recommended)
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Or using standard python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
To use live Gemini AI models:
```bash
cp .env.example .env
# Edit .env and add your key:
# GEMINI_API_KEY=your_gemini_api_key_here
```
*(If no key is configured, the application automatically runs in deterministic fallback mode with full functionality.)*

### 5. Start Development Servers
Open two terminal windows:

**Terminal 1 — Backend API:**
```bash
npm run server
# FastAPI running at http://127.0.0.1:8000
```

**Terminal 2 — Frontend:**
```bash
npm run dev
# Vite running at http://localhost:5173
```

Visit **http://localhost:5173** to explore ResolutionOps.

---

## 🧪 Testing & Verification

Run the comprehensive test suite and code quality checks:

```bash
# Run backend API & integration tests (11 tests)
npm test

# Run ESLint
npm run lint

# Run TypeScript build verification
npm run build
```

---

## 🔍 Flagship Demonstration Incident: Northstar Commerce (`CASE-2026-0891`)

To test the entire investigation workflow:
1. Open **Cases** and click on `CASE-2026-0891` (*"Order created in API returns 200 but customer dashboard displays pending status"*).
2. Review the **Customer Context** (Northstar Commerce, Enterprise 99.99% SLA).
3. Open the **Diagnostic Workbench** tab and run `inspect_webhook_logs` to see the HTTP 503 downstream failure.
4. Click **Ask Assistant** to query the case via natural language Q&A.
5. Review the **Ranked Root-Cause Hypotheses** generated by Gemini AI.
6. Inspect the **Engineering Handoff** tab to review reproduction steps and acceptance criteria.
7. Attempt to resolve the case in the **Resolution & Verification** tab to verify that the verification gate blocks unverified closure.

---

## 📄 License
MIT License. Built for enterprise SaaS reliability engineering.
