---
story_key: 7-2-ci-smoke-for-workflow-api
epic: 7
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 7.2: CI smoke for workflow API

Status: **done** - CI smoke workflow implemented and code review completed.

## Story

As a **tech lead**,  
I want **CI to run contract/smoke tests** on workflow endpoints in MOCK_MODE,  
So that **API parity does not regress** (innovation validation).

## Acceptance criteria

1. **Given** CI pipeline, **when** it runs, **then** at least one test exercises list/start/status for prebuilts in MOCK_MODE.

## Tasks / subtasks

- [x] Identify or create the canonical CI test command for workflow API smoke coverage.
- [x] Ensure smoke test selection includes list/start/status lifecycle for prebuilt workflows.
- [x] Add CI workflow wiring (or update existing workflow) to execute smoke tests on PR/push.
- [x] Keep CI path deterministic in MOCK_MODE and independent of external providers.
- [x] Document CI smoke command and expected behavior for contributors.
- [x] Validate CI config syntax and local command parity.

## Dev notes

### Implementation summary

- Added GitHub Actions workflow at `.github/workflows/workflow-api-smoke.yml`:
  - triggers on pull requests and pushes to `main`/`master`
  - sets up Python 3.11
  - installs backend dev dependencies via `python -m pip install -e "backend[dev]"`
  - runs focused MOCK_MODE lifecycle/openapi smoke tests
- Standardized smoke command to:
  - `python -m pytest backend/app/tests/test_workflows_headless_lifecycle.py backend/app/tests/test_workflows_openapi.py -q`
- Updated `docs/onboarding-local.md` with a CI smoke parity section for contributor visibility.

### Expected implementation touchpoints

- `.github/workflows/` CI definitions
- `backend/app/tests/` smoke test targets
- `docs/onboarding-local.md` or contributor docs for CI command visibility

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Implemented deterministic CI smoke coverage for prebuilt workflow API lifecycle.
- Added contributor-facing docs for CI command parity and local reproduction.
- Validated local parity command:
  - `source .venv/bin/activate && python -m pytest backend/app/tests/test_workflows_headless_lifecycle.py backend/app/tests/test_workflows_openapi.py -q` (3 passed).

### File list

- `_bmad-output/implementation-artifacts/7-2-ci-smoke-for-workflow-api.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `.github/workflows/workflow-api-smoke.yml`
- `docs/onboarding-local.md`

## Change Log

- **2026-04-26** - Story 7.2 created and kicked off; status -> in-progress.
- **2026-04-26** - Story 7.2 implemented; status -> review.
- **2026-04-26** - Code review completed; status -> done.
