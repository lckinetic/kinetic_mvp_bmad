---
story_key: 6-1-run-inspection-ui-api
epic: 6
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 6.1: Run inspection UI/API

Status: **done** - run inspection implementation accepted after code review completion.

## Story

As a **support user**,  
I can **inspect run history, steps, and webhook payloads**,  
So that **I can explain failures** (FR30-FR31).

## Acceptance criteria

1. **Given** a failed run, **when** I inspect it, **then** I see status history and relevant stored payloads where applicable.

## Tasks / subtasks

- [x] Define inspection response contract covering run summary, step timeline, and related webhook context.
- [x] Add or extend API endpoint(s) to fetch run-centric inspection data in one support-friendly payload.
- [x] Ensure filtering/query options make troubleshooting practical (status, run id, template, date windows as needed).
- [x] Keep secrets hygiene and structured error envelope behavior intact for inspection paths.
- [x] Add tests for failed-run inspection paths including webhook payload linkage.
- [x] Add OpenAPI checks for any new/expanded inspection routes and schemas.

## Dev notes

### Implementation summary

- Added support-facing inspection models and endpoint in `backend/app/api/workflows.py`:
  - `GET /workflows/runs/{run_id}/inspection`
  - Returns run summary, ordered steps, linked order IDs, and related webhook events.
- Added deterministic order-id extraction from run input/output and step data to connect run failures to stored webhook records.
- Reused existing structured error behavior (`404 Workflow run not found`) through current workflow API patterns.
- Kept implementation API-first for future UI and support tool consumers.

### Expected implementation touchpoints

- `backend/app/api/` (likely workflow/support inspection routes)
- `backend/app/services/` for aggregation/query orchestration if needed
- `backend/app/tests/` for inspection and error-envelope validation

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Implemented consolidated run inspection payload for support workflows.
- Added integration test proving failed-run inspection includes linked webhook payloads.
- Added OpenAPI path/schema assertions for the inspection route.
- Ran targeted tests: `.venv/bin/python -m pytest backend/app/tests/test_run_inspection_ui_api.py backend/app/tests/test_workflows_openapi.py -q` (3 passed).

### File list

- `_bmad-output/implementation-artifacts/6-1-run-inspection-ui-api.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/api/workflows.py`
- `backend/app/tests/test_run_inspection_ui_api.py`
- `backend/app/tests/test_workflows_openapi.py`

## Change Log

- **2026-04-26** - Story 6.1 created and kicked off; status -> in-progress.
- **2026-04-26** - Story 6.1 implemented; status -> review.
- **2026-04-26** - Story 6.1 code review completed; status -> done.
