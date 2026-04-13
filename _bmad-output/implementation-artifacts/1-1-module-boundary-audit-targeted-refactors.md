---
story_key: 1-1-module-boundary-audit-targeted-refactors
epic: 1
status: done
sprint: 1
story_prepared_on: '2026-04-12'
implementation_do_not_start_before: '2026-04-13'
# Scheduled kickoff: 09:00 local Central European Time (Europe/Berlin). April 2026 = CEST (UTC+2).
scheduled_kickoff_local: '2026-04-13 09:00 Europe/Berlin'
scheduled_kickoff_iso: '2026-04-13T09:00:00+02:00'
---

# Story 1.1: Module boundary audit & targeted refactors

Status: **done** — story 1.1 completed after BMAD code review (2026-04-13). (Original planned kickoff was **2026-04-13, 09:00 Europe/Berlin**; work started early on **2026-04-12** per team go-ahead.)

## Story

As a **developer**,  
I want **clear packages and import rules** for `api` / `services` / `adapters` / `engine` / `db`,  
So that **changes stay localized** and reviewers can enforce layering.

## Acceptance criteria

1. **Given** the repo after this story’s work, **when** a reviewer inspects `backend/app`, **then** API route modules do **not** import **`app.adapters.*`** directly **except** where explicitly listed as a documented exception (or those imports are refactored away in favour of services).
2. **And** layering rules are written down in **`docs/`** (add or extend a short section) **and** cross-referenced from **`_bmad-output/planning-artifacts/architecture.md`** (or a single “Layering” subsection there).

## Tasks / subtasks

- [x] **Audit** (AC: 1) — Map imports from `backend/app/api/**/*.py` to `app.adapters`, `app.services`, `app.engine`, `app.db` (spreadsheet or bullet list in PR / story update).
- [x] **Known issue** — `app/api/ai.py` previously imported `PrivyClient`, `CoinbaseClient` from `app.adapters.*`. **Resolved:** thin re-exports under `app.services` (same pattern as `banxa_client.py`).
- [x] **Refactor** — Apply **minimal** refactors to meet AC (avoid unrelated cleanups).
- [x] **Document** — Added **`docs/architecture-layers.md`** with allowed edges, forbidden edges, exceptions table, and pytest guard reference.
- [x] **Link** — Pointer from `_bmad-output/planning-artifacts/architecture.md` §3 to `docs/architecture-layers.md`.

## Dev notes

### Intent

Align runtime code with [Source: `docs/ai/architecture-principles.md` §1] and [Source: `_bmad-output/planning-artifacts/architecture.md` §3]. PRD does not mandate a linter gate in MVP; **documentation + consistent imports** satisfy the story unless you add optional `import-linter` later.

### Initial findings (audit starting point)

- Several API modules use **services** and **db** appropriately (`onramp.py`, `offramp.py`, `webhooks.py`).
- **`app/api/ai.py`** was the **only** API module importing **`app.adapters.*`** directly (addressed in this story).

### Final audit — `backend/app/api/**/*.py` (post-change)

| Module | `app.adapters` | `app.services` | `app.engine` | `app.db` | `app.ai` / other |
|--------|----------------|----------------|--------------|----------|------------------|
| `ai.py` | **none** | banxa, coinbase, privy clients | graph_runner, metrics | engine, models | interpreter |
| `onramp.py` | none | banxa_client, onramp_service | — | engine, models | — |
| `offramp.py` | none | banxa_client, offramp_service | — | engine, models | — |
| `webhooks.py` | none | — | — | engine, models | — |
| `workflows.py` | none | — | metrics, runner | engine, models | `app.workflows` |

### Testing

- No new behaviour required for pure refactor; run **existing** tests if any; **smoke** `GET /health` and one **AI** or **workflow** path if touched.

### Out of scope for this story

- **Secrets / logging** → Story **1-2**.
- **New features** or broad rewrites outside import boundaries.

## Dev agent record

### Agent model used

Cursor agent (GPT-5.1)

### Debug log references

_(none)_

### Completion notes list

- Sprint 1 kicked off; **epic-1** → `in-progress`; story **1-1** → `review` then **`done`** in `sprint-status.yaml` after code review (2026-04-13).
- Added `app/services/privy_client.py` and `coinbase_client.py` mirroring `banxa_client.py`; `ai.py` now imports clients only from `app.services`.
- Added AST-based guard test `app/tests/test_api_layer_no_adapter_imports.py` so CI can catch regressions.
- Authored `docs/architecture-layers.md` and linked from planning `architecture.md` §3.

### File list

- `backend/app/api/ai.py`
- `backend/app/services/privy_client.py`
- `backend/app/services/coinbase_client.py`
- `backend/app/tests/test_api_layer_no_adapter_imports.py`
- `docs/architecture-layers.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/1-1-module-boundary-audit-targeted-refactors.md`

### Review Findings

- [x] [Review][Defer] AST import guard is syntactic only [`backend/app/tests/test_api_layer_no_adapter_imports.py`] — deferred, pre-existing class of limitation (dynamic/`importlib` / string-based imports are not detected); optional follow-up: `import-linter` or runtime policy tests.

## Change Log

- **2026-04-12** — Story 1-1: API layer free of direct `app.adapters` imports; layering doc + test guard; status → review.
- **2026-04-13** — BMAD code review (`bmm:workflows:code-review`): no patch or decision items; one deferred limitation noted; status → done.
