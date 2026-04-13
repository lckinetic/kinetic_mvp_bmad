---
story_key: 1-2-settings-secrets-hygiene
epic: 1
status: done
sprint: 1
story_prepared_on: '2026-04-12'
---

# Story 1.2: Settings & secrets hygiene

Status: **done** — code review completed (2026-04-13); patch item resolved by centralizing redaction in `step_fail`.

## Story

As an **operator**,  
I want **secrets excluded from logs and API errors**,  
So that **demos and logs stay safe** (NFR-S1, FR32).

## Acceptance criteria

1. **Given** startup and error paths, **when** logs and client errors are emitted, **then** no raw API keys or webhook secrets appear in payloads documented as user-visible.

## Tasks / subtasks

- [x] **Inventory** — List settings-backed secrets and startup log paths (`main.py`, `safe_settings_log`).
- [x] **DATABASE_URL** — Never log raw credentials; use URL-level redaction.
- [x] **Structured startup log** — Extend `safe_settings_log` for `DATABASE_URL` + suffix-based keys (`*_SECRET`, `*_API_KEY`, …).
- [x] **Persisted / API-visible errors** — Redact known secret substrings before writing `WorkflowRun.error`, `WorkflowStep.error`, and AI `run-graph` error field (`runner.py`, `graph_runner.py`, `ai.py`).
- [x] **Document** — `docs/ai/architecture-principles.md` §9; cross-links in `docs/architecture-layers.md` and planning `architecture.md`.
- [x] **Tests** — `app/tests/test_secrets_redact.py` for URL redaction, `safe_settings_log`, and `redact_secrets_in_text`.

## Dev notes

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 1, Story 1.2]
- [Source: `_bmad-output/project-context.md` — logging / NFR-S1]

### Testing

```bash
cd backend && python -m pytest app/tests -q
```

## Dev agent record

### Agent model used

Cursor agent (GPT-5.1)

### Debug log references

_(none)_

### Completion notes list

- Added `app/core/secrets_redact.py` (`redact_database_url`, `redact_secrets_in_text`, `_secret_substrings` from `Settings`).
- Hardened `safe_settings_log` for `DATABASE_URL` and suffix-based sensitive keys.
- Applied redaction on template run failures and AI graph run failures; **`step_fail`** applies `redact_secrets_in_text` for every persisted `WorkflowStep.error` (templates + graph runner).
- Documented rules in architecture principles §9; linked from layering doc and planning architecture.

### File list

- `backend/app/core/secrets_redact.py`
- `backend/app/core/logging.py`
- `backend/app/engine/runner.py`
- `backend/app/engine/graph_runner.py`
- `backend/app/services/workflow_steps.py`
- `backend/app/api/ai.py`
- `backend/app/tests/test_secrets_redact.py`
- `docs/ai/architecture-principles.md`
- `docs/architecture-layers.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/1-2-settings-secrets-hygiene.md`

### Review Findings

- [x] [Review][Patch] **Template `WorkflowStep` errors bypass redaction** — Resolved: `step_fail` in `workflow_steps.py` now always runs `redact_secrets_in_text(..., get_settings())` before persisting `WorkflowStep.error`; `graph_runner` passes raw exception text into `step_fail` (single choke point).

- [x] [Review][Patch] **`sprint-status.yaml` timestamp regression** — corrected during review sync. [`_bmad-output/implementation-artifacts/sprint-status.yaml`]

## Change Log

- **2026-04-12** — Story 1-2 implemented; status → review.
- **2026-04-13** — BMAD `bmad-code-review` on this story: **2** patch findings recorded; status → **in-progress** until resolved.
- **2026-04-13** — Patch: centralize redaction in `step_fail`; story and **epic-1** marked **done** after review sign-off.
