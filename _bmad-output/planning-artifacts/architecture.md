---
stepsCompleted:
  - synthesized-2026-04-12
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/project-context.md
  - docs/architecture.md
  - docs/ai/architecture-principles.md
workflowType: architecture
project_name: kinetic-mvp-bmad
user_name: Leonachen
date: '2026-04-12'
---

# Architecture — kinetic-mvp-bmad

_Solution design aligned to `prd.md`. Implementation lives primarily under `backend/app/`._

## 1. System context

- **Actors:** Authors/operators (web UI), integration clients (HTTP), internal ops/support, provider webhooks.
- **External systems:** Partner APIs (Banxa, Privy, Coinbase, …) via **adapters**; optional LLM provider for **assistant** (out of band from core money path).
- **Posture:** **Integration technology**—Kinetic **does not** perform KYC/AML as the regulated party; **connectors** invoke partners per PRD.

## 2. Container view (logical)

| Container | Responsibility |
|-----------|----------------|
| **Web SPA** (new/ evolving) | Workflow authoring, runs, assistant UI; talks to **API** only. |
| **API service** (FastAPI) | HTTP + OpenAPI; auth boundary (MVP minimal); routes to **services**. |
| **Workflow engine** | Template/graph execution, `WorkflowRun` lifecycle, step dispatch. |
| **Adapters** | Provider-specific I/O; **MOCK** vs live per configuration. |
| **PostgreSQL** | Orders, webhook events, workflow runs, domain state. |

## 3. Layering (non-negotiable)

Authoritative import edges and exception process: **`docs/architecture-layers.md`**.

Matches `docs/ai/architecture-principles.md` and PRD:

1. **API** — HTTP models, validation, routing; **no** business rules or raw provider soup.
2. **Services** — Orchestration, use-cases, cross-cutting workflow steps.
3. **Adapters** — Single place for external API shapes and retries/timeouts (`NFR-I1`).
4. **DB** — SQLModel models, sessions; **canonical statuses** only on persisted entities.

## 4. Key architectural decisions

### ADR-A1 — Modular monolith (MVP)

- **Decision:** Single deployable with **clear module boundaries** (`api`, `services`, `adapters`, `engine`, `db`, `workflows`, `ai`).
- **Rationale:** PRD phased delivery; avoid distributed complexity until **NFR-SC1** scale triggers.
- **Consequence:** Extract services later if needed; **stateless** API tier allowed to scale horizontally later.

### ADR-A2 — API standardisation

- **Decision:** **OpenAPI** as source of truth for **workflow** and **run** surfaces; **consistent error envelope** (code, message, optional details) for UI and **Raj** API-only path (`FR19–FR22`, `NFR-D1`).
- **Rationale:** Dual clients (SPA + integrations) must not diverge.

### ADR-A3 — Prebuilt workflow API parity

- **Decision:** **Same** domain operations for **list templates / start run / get status** whether called from SPA or **headless** client (`FR19–FR21`).
- **Rationale:** PRD MVP goal—**no UI-only** exclusivity for prebuilts.

### ADR-A4 — Assistant vs engine

- **Decision:** Assistant produces **proposals** validated against **engine/registry schema** before persist or run (`FR14`, innovation risks).
- **Rationale:** Prevent invalid graphs; **LLM** is not a second runtime.

### ADR-A5 — MOCK_MODE

- **Decision:** First-class config; **deterministic** adapter behaviour in mock; **no live secrets** required for demos (`FR24`, `NFR-S1`).
- **Rationale:** Fintech-adjacent safety and CI.

### ADR-A6 — Webhooks

- **Decision:** **Store-then-process**; **idempotency** keys; payloads retained for audit (`FR27–FR29`).
- **Rationale:** Domain PRD + existing principles.

### ADR-A7 — Auth / tenancy (MVP)

- **Decision:** **Minimal** access model (keys, network, feature flags); **RBAC** hooks in services/API without full productization (`SaaS B2B` section, PRD scope).
- **Rationale:** Explicit out-of-scope for production auth; **design for** future roles.

## 5. Data architecture

- **Entities (illustrative):** `Order`, `WebhookEvent`, `WorkflowRun` (existing direction); extend only with migration strategy when schema changes exceed `create_all` MVP tolerance.
- **Rules:** **Normalise** provider statuses before persist; **no** unknown provider strings on core `Order` rows.

## 6. Deployment & local dev

- **Docker Compose** for Postgres (+ optional app container per phase C).
- **Environment:** `DATABASE_URL`, `MOCK_MODE`, provider secrets; **secrets** not logged (`NFR-S1`).

## 7. Observability

- **Structured logging** with **run/request correlation** (`NFR-O1`).
- **Metrics:** Engine step timings—incremental; **no** full APM requirement in MVP PRD.

## 8. Risks & follow-ups

| Risk | Mitigation |
|------|------------|
| SPA + API drift | Contract tests + OpenAPI gate in CI |
| Assistant invalid output | Schema validation + confirm step |
| Schema evolution | Introduce migrations when MVP stability requires |

## References

- `prd.md` — requirements authority  
- `_bmad-output/project-context.md` — agent implementation rules  
- `docs/ai/architecture-principles.md` — MVP guardrails  
