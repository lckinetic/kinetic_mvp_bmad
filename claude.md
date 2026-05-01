# Kinetic MVP — Claude Code Context

This file is the working context guide for coding agents (Claude Code) in this repository.

## 1) Project Purpose (Business + Product)

Kinetic is an AI-assisted workflow automation platform for crypto operations.

Core business idea:
- Make digital/crypto operations as simple as consumer apps.
- Let teams run treasury/trading/payment workflows without building every integration themselves.
- Provide an investor/demo-safe MVP in sandbox/mock mode, with a path to live providers.

Current positioning:
- MVP with end-to-end flows, API + UI, and demo tooling.
- Focused on fast validation, reliability, and clear demo narrative.

## 2) Current Product Surfaces

Primary UI tabs/pages (same-origin at `/ui-kit`):
- `Home`
- `Workflows`
- `Operations`
- `AI Assistant`
- `Workflow Builder (mock)`

Notes:
- `Home` is investor/deck-aligned and recently refreshed from latest design-system iteration.
- Builder is intentionally mock/demo oriented.

## 3) Technical Architecture

Backend stack:
- FastAPI
- SQLModel / SQLAlchemy
- PostgreSQL (preferred local path)
- Mock/live AI mode switching

Frontend stack:
- UI kit under `ui_kits/app`
- React via Babel-loaded JSX in `index.html`
- Hash-based navigation
- Same-origin static hosting from backend (`/ui-kit`)

High-level layering:
- API routes -> services/engine/adapters -> DB

## 4) Key Paths

Backend:
- `backend/app/main.py`
- `backend/app/api/`
- `backend/app/ai/`
- `backend/app/core/`
- `backend/app/db/`
- `backend/app/tests/`

UI:
- `ui_kits/app/index.html` (shell + route metadata)
- `ui_kits/app/Home.jsx`
- `ui_kits/app/WorkflowRunner.jsx`
- `ui_kits/app/AIGenerator.jsx`
- `ui_kits/app/WorkflowBuilder.jsx`
- `ui_kits/app/Components.jsx`

Planning / tracking:
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/*.md` (story artifacts)

Canonical onboarding:
- `docs/onboarding-local.md`

## 5) Runtime Modes + Environment

Important env behavior:
- `MOCK_MODE=true` is the safe demo default.
- Live mode requires valid AI settings and secrets.

Common local startup gotcha:
- If `DATABASE_URL` points to Railway-internal host (e.g. `postgres.railway.internal`), local startup will fail.
- For local unblock, run with SQLite override:

```bash
source .venv/bin/activate
DATABASE_URL=sqlite:///./backend/dev-ui.sqlite python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
```

## 6) Run / Verify Commands

Preferred local setup: follow `docs/onboarding-local.md`.

Common run:

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --reload --app-dir backend
```

Health checks:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/
curl -I http://127.0.0.1:8000/ui-kit/
```

## 7) Testing + Quality Expectations

Minimum expectations for changes:
- Keep behavior deterministic in mock mode.
- Preserve route IDs and navigation wiring when changing labels/content.
- Run targeted tests/lint relevant to changed files.
- Avoid introducing secret leakage in logs/errors.

Useful quick checks:
- UI lint diagnostics on touched files.
- API smoke tests in `backend/app/tests/` (especially workflows + openapi).

## 8) Current Scope Guidance

In practice, this repo has evolved beyond earliest MVP-only notes.
Treat current source-of-truth as:
- `epics.md` and `sprint-status.yaml`
- implemented code behavior
- onboarding docs

When changing UI:
- Keep visual style consistent with existing Kinetic UI tokens/components.
- Use `Home` as narrative landing, and keep other pages stable unless requested.

## 9) Agent Guardrails

- Do not make destructive git/history operations.
- Do not commit secrets or expose keys.
- Prefer minimal, surgical edits over broad refactors.
- If user asks to track work, update both:
  - story artifact markdown
  - `sprint-status.yaml`

## 10) Quick Session Checklist (for Claude Code)

1. Read this file + `docs/onboarding-local.md`.
2. Check `sprint-status.yaml` + relevant story artifact.
3. Confirm server mode/db reachability.
4. Implement requested change in smallest safe diff.
5. Run lint/tests for touched areas.
6. Update tracking artifacts if requested.

