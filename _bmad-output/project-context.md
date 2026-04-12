---
project_name: kinetic-mvp-bmad
user_name: Leonachen
date: '2026-04-12'
sections_completed:
  - technology_stack
  - language_rules
  - framework_rules
  - testing_rules
  - quality_rules
  - workflow_rules
  - anti_patterns
status: complete
rule_count: 42
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

| Area | Choice | Notes |
|------|--------|--------|
| Language | Python **≥ 3.11** | `backend/pyproject.toml` |
| API | **FastAPI** ≥ 0.111, **Uvicorn** [standard] ≥ 0.30 | App factory in `backend/app/main.py` |
| Data | **SQLModel** ≥ 0.0.21, **PostgreSQL** via `psycopg2-binary` | Models in `backend/app/db/models.py` |
| Config | **python-dotenv** | `DATABASE_URL` required; load via `get_settings()` |
| Validation | **Pydantic** v2 (`pydantic[email]`) | |
| Templates | **Jinja2** ≥ 3.1 | |
| HTTP testing (dev) | **pytest** ≥ 8, **httpx** ≥ 0.27 | Optional dev deps; `testpaths = ["app/tests"]`, `pythonpath = ["."]` |

**Runtime flags**

- **`MOCK_MODE`** (default **true** via env parsing): mocked providers, demo-safe. Real integrations when false.
- **`DATABASE_URL`**: required at startup or `get_settings()` raises.

---

## Critical Implementation Rules

### Language-Specific Rules

- Use **`from __future__ import annotations`** where the codebase already does for forward references and consistency.
- Prefer **explicit UTC** datetimes: `datetime.now(timezone.utc)` — see `utcnow()` in `models.py`.
- **Settings access**: always go through `get_settings()` after `load_dotenv()`; do not read `os.environ` for app config in scattered places.
- **SQLModel / SQLAlchemy**: register models by importing `app.db.models` in `main.py` before `create_all()` — comment in `main.py` is mandatory for new tables.
- Use **`Field(sa_column=Column(JSON))`** for JSON payloads when matching existing `WebhookEvent` / `WorkflowRun` patterns.

### Framework-Specific Rules (FastAPI)

- **Routers** live under `backend/app/api/`; include them in `create_app()` in `main.py`.
- **Lifespan**: DB engine creation and `create_db_and_tables` belong in the lifespan handler, not in module import side effects (except model import for metadata).
- **Logging**: use module logger `logging.getLogger("kinetic")` and `configure_logging` / `safe_settings_log` for startup — **never log raw secrets**; secrets are redacted via `safe_settings_log` patterns.
- **Root route** `/` returns minimal discovery JSON; preserve `/docs` and `/health` references.

### Domain & Layering (from `docs/ai/architecture-principles.md`)

- **API layer** (`app/api`): HTTP, validation, DI only — no provider-specific logic or heavy SQL.
- **Services** (`app/services`): orchestration and business rules.
- **Adapters / clients** (`app/adapters/*`, `*client.py`): external API details only.
- **DB** (`app/db`): models, engine, sessions — persistence only.

### Status & Idempotency

- Persist only **canonical** order statuses: `pending` | `processing` | `completed` | `failed` | `cancelled`. Normalize provider strings in one place.
- **Idempotency**: respect DB constraints — `WebhookEvent.idempotency_key`, and `(provider, direction, client_reference)` on `Order` when `client_reference` is used.

### Testing Rules

- Tests belong under **`backend/app/tests/`** per `pyproject.toml` (when added). Use **pytest** + **httpx** for API tests.
- **No test suite exists yet** — new tests should follow `testpaths` and avoid importing the app before env is set if integration tests need DB.

### Code Quality & Style Rules

- Match existing module layout: **`app/core`**, **`app/api`**, **`app/services`**, **`app/db`**, **`app/engine`**, **`app/workflows`**, **`app/adapters`**, **`app/ai`**.
- New endpoints: update **`docs/`** (see workflow rules), and Postman under **`docs/postman/`** per project principles.
- Keep **MOCK_MODE** paths deterministic and free of network when `true`.

### Development Workflow Rules

- **Local DB**: `infra/docker-compose.yml` for Postgres; **`DATABASE_URL`** in `backend/.env` (see `.env.example` if present).
- **Docs are source of truth** (`docs/`); align `overview.md`, `architecture.md`, and feature docs when behavior changes.
- **BMad**: planning artifacts → `_bmad-output/planning-artifacts`; this file → `_bmad-output/project-context.md`.

### Critical Don't-Miss Rules

- **Do not** persist raw provider status strings on `Order` without normalization.
- **Do not** skip storing webhook payloads — audit trail first; **do not delete** webhook events in MVP.
- **Do not** break demo safety: when `MOCK_MODE=true`, avoid accidental real provider calls.
- **Workflow engine / graph runner** code: preserve **component registry** and **validation** patterns under `app/engine` and `app/workflows` when extending.
- **Privy / Coinbase / Banxa** clients: keep secrets out of logs and error messages surfaced to clients.

---

## Usage Guidelines

**For AI Agents**

- Read this file before implementing backend or workflow changes.
- Prefer the more restrictive option when unsure (especially status normalization, idempotency, and MOCK_MODE).
- Update this file if new stack versions or non-obvious conventions are introduced.

**For Humans**

- Keep this file lean; bump versions when `pyproject.toml` or runtime constraints change.
- Re-run **`bmad-generate-project-context`** when the architecture shifts materially.

Last Updated: 2026-04-12
