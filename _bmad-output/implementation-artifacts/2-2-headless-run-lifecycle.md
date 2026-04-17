---
story_key: 2-2-headless-run-lifecycle
epic: 2
status: done
sprint: 1
story_prepared_on: '2026-04-13'
---

# Story 2.2: Headless run lifecycle

Status: **done** - code review completed and follow-up patch applied (temp DB FD/file cleanup in test).

## Story

As an **integration client**,  
I can **list prebuilts, start a run, poll to completion**,  
Without **using the SPA** (FR19-FR21).

## Acceptance criteria

1. **Given** MOCK_MODE, **when** I start a run via HTTP, **then** status and final state match canonical statuses and are retrievable without browser session.

## Tasks / subtasks

- [x] Verify API supports headless flow: list templates, start run, poll status, list runs.
- [x] Add integration test coverage for HTTP lifecycle (`GET /workflows/templates`, `POST /workflows/run/{template_name}`, `GET /workflows/runs/{run_id}`, `GET /workflows/runs`).
- [x] Confirm response status lands in terminal state for headless run and can be retrieved by ID.

## Dev notes

### Technical approach

- Existing workflow API routes already satisfied the lifecycle behavior.
- Added a dedicated lifecycle integration test using a temporary SQLite database and router-level dependency override for `get_db`.
- Test drives the real HTTP endpoints without any SPA dependency.

### Testing

Added: `backend/app/tests/test_workflows_headless_lifecycle.py`

Run command (from repo root):

```bash
python -m pytest backend/app/tests/test_workflows_headless_lifecycle.py -q
```

Validation run:
- `python -m pytest backend/app/tests/test_workflows_headless_lifecycle.py -q` -> **passed**.

## Dev agent record

### Agent model used

Cursor agent (GPT-5.1)

### Completion notes list

- Implemented integration test coverage for headless API lifecycle in MOCK mode.
- Kept API behavior unchanged because lifecycle endpoints were already in place.
- Updated sprint status to move story to `review`.

### File list

- `backend/app/tests/test_workflows_headless_lifecycle.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/2-2-headless-run-lifecycle.md`

### Review Findings

- [x] [Review][Low] Temp file descriptor leak and leftover temp DB artifact in lifecycle test setup.
  - Resolved by closing `mkstemp()` descriptor and removing temp DB file in `finally`.

## Change Log

- **2026-04-13** - Story 2-2 implemented via integration test coverage; status -> review.
- **2026-04-13** - Code review follow-up applied (FD/file cleanup), lifecycle test verified passed; status -> done.
