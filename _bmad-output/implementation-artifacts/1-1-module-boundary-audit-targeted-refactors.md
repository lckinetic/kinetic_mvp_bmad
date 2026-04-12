---
story_key: 1-1-module-boundary-audit-targeted-refactors
epic: 1
status: ready-for-dev
sprint: 1
story_prepared_on: '2026-04-12'
implementation_do_not_start_before: '2026-04-13'
# Scheduled kickoff: 09:00 local Central European Time (Europe/Berlin). April 2026 = CEST (UTC+2).
scheduled_kickoff_local: '2026-04-13 09:00 Europe/Berlin'
scheduled_kickoff_iso: '2026-04-13T09:00:00+02:00'
---

# Story 1.1: Module boundary audit & targeted refactors

Status: **ready-for-dev** (prepared for pickup). **Scheduled dev kickoff:** **2026-04-13, 09:00** in **Europe/Berlin** (Central European **summer** time, **CEST**, `+02:00` — common “CET” wall-clock in April). **No implementation before that instant** unless you change this file.

_Add a calendar reminder yourself: this repo cannot trigger alarms. Use ISO **2026-04-13T09:00:00+02:00** or “9:00 Europe/Berlin” in your calendar app._

## Story

As a **developer**,  
I want **clear packages and import rules** for `api` / `services` / `adapters` / `engine` / `db`,  
So that **changes stay localized** and reviewers can enforce layering.

## Acceptance criteria

1. **Given** the repo after this story’s work, **when** a reviewer inspects `backend/app`, **then** API route modules do **not** import **`app.adapters.*`** directly **except** where explicitly listed as a documented exception (or those imports are refactored away in favour of services).
2. **And** layering rules are written down in **`docs/`** (add or extend a short section) **and** cross-referenced from **`_bmad-output/planning-artifacts/architecture.md`** (or a single “Layering” subsection there).

## Tasks / subtasks

- [ ] **Audit** (AC: 1) — Map imports from `backend/app/api/**/*.py` to `app.adapters`, `app.services`, `app.engine`, `app.db` (spreadsheet or bullet list in PR / story update).
- [ ] **Known issue** — `app/api/ai.py` currently imports `PrivyClient`, `CoinbaseClient` from `app.adapters.*` [verify at implementation time]. Decide: **move construction/usage behind services** or **document as time-boxed exception** with removal ticket.
- [ ] **Refactor** — Apply **minimal** refactors to meet AC (avoid unrelated cleanups).
- [ ] **Document** — Add **`docs/ai/layering.md`** or **`docs/architecture-layers.md`** (your choice of name) with: allowed edges (API→services→adapters→…), forbidden edges, exceptions table.
- [ ] **Link** — Add a pointer from `architecture.md` (planning artifact) to the doc above.

## Dev notes

### Intent

Align runtime code with [Source: `docs/ai/architecture-principles.md` §1] and [Source: `_bmad-output/planning-artifacts/architecture.md` §3]. PRD does not mandate a linter gate in MVP; **documentation + consistent imports** satisfy the story unless you add optional `import-linter` later.

### Initial findings (audit starting point)

- Several API modules use **services** and **db** appropriately (`onramp.py`, `offramp.py`, `webhooks.py`).
- **`app/api/ai.py`** imports **`app.adapters.privy.client`** and **`app.adapters.coinbase.client`** directly—likely **primary refactor target** or **documented exception**.

### Testing

- No new behaviour required for pure refactor; run **existing** tests if any; **smoke** `GET /health` and one **AI** or **workflow** path if touched.

### Out of scope for this story

- **Secrets / logging** → Story **1-2**.
- **New features** or broad rewrites outside import boundaries.

## Dev agent record

### Agent model used

_(filled at dev time)_

### Debug log references

### Completion notes list

### File list
