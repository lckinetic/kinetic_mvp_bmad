---
story_key: 2-1-openapi-for-workflow-surfaces
epic: 2
status: done
sprint: 1
story_prepared_on: '2026-04-13'
---

# Story 2.1: OpenAPI for workflow surfaces

Status: **done** — BMAD code review passed (2026-04-13); acceptance criteria satisfied.

## Story

As an **integration engineer**,  
I can **discover workflow HTTP endpoints** via OpenAPI,  
So that **clients generate correct calls** (FR33, NFR-D1).

## Acceptance criteria

1. **Given** a running API, **when** I open `/docs` or the served OpenAPI JSON, **then** workflow list/start/status routes are described with request/response schemas.

## Tasks / subtasks

- [x] **Models** — Add Pydantic response models for template catalog, template detail, and run steps (previously untyped dict returns).
- [x] **Routes** — Attach `response_model`, summaries, and `Query` metadata on list/start/status (and steps for run inspection).
- [x] **Tests** — `app/tests/test_workflows_openapi.py` asserts key paths and `components.schemas` include workflow DTOs.

## Dev notes

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 2, Story 2.1]
- [Source: `backend/app/api/workflows.py`]

### Testing

```bash
cd backend && .venv/bin/python -m pytest app/tests/test_workflows_openapi.py -q
```

## Dev agent record

### Agent model used

Cursor agent (GPT-5.1)

### Completion notes list

- Introduced `WorkflowTemplateSummary`, `WorkflowTemplateDetail`, `WorkflowRunStepResponse`; wired `response_model` on `GET /templates`, `GET /templates/{name}`, `GET /runs/{id}/steps`.
- Enriched `POST /run/{template_name}`, `GET /runs`, `GET /runs/{id}` with summaries / `Query` descriptions for OpenAPI.
- Tests use a minimal FastAPI app mounting only the workflows router (no DB) to validate `/openapi.json`.

### File list

- `backend/app/api/workflows.py`
- `backend/app/tests/test_workflows_openapi.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/2-1-openapi-for-workflow-surfaces.md`

### Review Findings

- [x] [Review][Patch] **Missing newline at end of `workflows.py`** — POSIX text file convention; **fixed** during review (`backend/app/api/workflows.py`).

## Change Log

- **2026-04-13** — Story 2-1 implemented; status → review.
- **2026-04-13** — BMAD code review: AC verified; `pytest app/tests/test_workflows_openapi.py` **2 passed** (use `backend/.venv`); EOF newline fixed; status → **done**.
