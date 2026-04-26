---
story_key: 4-2-template-browse-run-ui
epic: 4
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 4.2: Template browse and run UI

Status: **done** - template browse/list and run lifecycle UI now use workflow API paths with fallback behavior.

## Story

As an **operator**,  
I can **start a prebuilt workflow from the UI** in MOCK_MODE,  
So that **I can demo without Postman** (FR1-FR2, FR5-FR7).

## Acceptance criteria

1. **Given** MOCK_MODE, **when** I start a run from UI, **then** status updates are visible through completion or failure with reason.

## Tasks / subtasks

- [x] Wire template listing in UI to `GET /workflows/templates` with robust fallback.
- [x] Preserve template browse and detail selection flow from Story 4.1 shell.
- [x] Wire run start in runner to `POST /workflows/run/{template_name}`.
- [x] Display run status and run ID from API-backed execution response.
- [x] Load and render run steps from `GET /workflows/runs/{run_id}/steps` when available.
- [x] Keep deterministic fallback behavior when API is unavailable to avoid dead-end demos.
- [x] Ensure routes and runner entry handoff remain compatible with shell navigation.

## Dev notes

### Implementation summary

- Updated `ui_kits/app/index.html`:
  - Added lightweight API helper (`apiGet`) using `window.KINETIC_API_BASE` override.
  - Templates landing now attempts API template loading and falls back to local templates if unavailable.
  - Runs landing now attempts API run loading and falls back to local runs if unavailable.
  - Template -> Runner handoff now passes selected template name into `WorkflowRunner`.
  - Navigation hardening: explicit sidebar navigation always exits runner subview so `Templates` consistently returns to template list/detail landing.
- Updated `ui_kits/app/WorkflowRunner.jsx`:
  - Added API helpers (`apiGet`, `apiPost`) for run path integration.
  - Added template loading from `GET /workflows/templates` with fallback to local constants.
  - Replaced local-only simulated run with API run start (`POST /workflows/run/{template_name}`).
  - Added step loading from `GET /workflows/runs/{run_id}/steps`.
  - Preserved deterministic fallback completion path when API is not reachable.

### Expected implementation touchpoints

- `ui_kits/app/index.html`
- `ui_kits/app/WorkflowRunner.jsx`
- `ui_kits/app/Components.jsx` (unchanged in this story but compatible with route shell)

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Story 4.2 UI wiring is now API-first while preserving demo-safe fallback behavior.
- Route-shell integration from Story 4.1 remained intact and reusable.
- Runner now consumes selected template context from Templates landing.
- Added lightweight shell navigation smoke test coverage to guard route/hash wiring and templates-runner reset behavior.

### File list

- `_bmad-output/implementation-artifacts/4-2-template-browse-run-ui.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `ui_kits/app/index.html`
- `ui_kits/app/WorkflowRunner.jsx`
- `backend/app/tests/test_ui_shell_navigation_smoke.py`

## Change Log

- **2026-04-26** - Story 4.2 implemented; status -> review.
- **2026-04-26** - Follow-up hardening: fixed Templates navigation dead-end and added UI shell smoke tests.
- **2026-04-26** - Story 4.2 code review completed; status -> done.
