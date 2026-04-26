---
story_key: 6-2-onboarding-documentation
epic: 6
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 6.2: Onboarding documentation

Status: **done** - onboarding documentation accepted after code review completion.

## Story

As a **new engineer**,  
I can **run the stack locally** using documented steps,  
So that **I onboard in one session** (FR34, NFR-O2).

## Acceptance criteria

1. **Given** the README/docs path, **when** I follow steps, **then** I reach healthy API and DB with MOCK_MODE demo path.

## Tasks / subtasks

- [x] Audit current README/docs for local prerequisites, env setup, and run commands.
- [x] Document clean start path: venv setup, dependency install, DB setup, API startup, and health verification.
- [x] Document MOCK_MODE end-to-end demo flow including key API calls.
- [x] Add troubleshooting section for common setup/runtime issues (dependency mismatch, DB connection, env variables).
- [x] Validate doc steps against current repo scripts and command paths.
- [x] Add testability note/checklist so onboarding can be verified consistently.

## Dev notes

### Implementation summary

- Added canonical onboarding guide at `docs/onboarding-local.md` with:
  - prerequisites, Postgres startup, venv + dependency install, env config, API startup
  - MOCK_MODE demo flow for workflows and assistant endpoints
  - troubleshooting section for common setup failures
- Updated `docs/index.md` to add `onboarding-local.md` in quick reference and make it the default getting-started path.
- Updated root `readme.md` with explicit pointer to the canonical onboarding document.

### Expected implementation touchpoints

- `README.md` and/or `docs/` onboarding pages
- `_bmad-output/planning-artifacts/` cross-links if needed
- Validation by executing documented commands in local dev environment

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Standardized onboarding around one canonical path under `docs/`.
- Removed ambiguity between mixed run instructions by centralizing setup + verification steps.
- Validated documented verification command:
  - `source .venv/bin/activate && python -m pytest backend/app/tests/test_workflows_openapi.py backend/app/tests/test_assistant_openapi.py -q` (3 passed).

### File list

- `_bmad-output/implementation-artifacts/6-2-onboarding-documentation.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `docs/onboarding-local.md`
- `docs/index.md`
- `readme.md`

## Change Log

- **2026-04-26** - Story 6.2 created and kicked off; status -> in-progress.
- **2026-04-26** - Story 6.2 implemented; status -> review.
- **2026-04-26** - Story 6.2 code review completed; status -> done.
