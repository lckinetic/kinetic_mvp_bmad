# Release Readiness Checklist

Current status: **MVP ready** for controlled demos and internal handoff.

## Gate checks

- [x] Sprint tracking complete for Epics 1-7 and retrospectives.
- [x] Core backend smoke coverage passes in local parity run.
- [x] Workflow API smoke path in CI (`.github/workflows/workflow-api-smoke.yml`) exists and is scoped.
- [x] Local onboarding has canonical path (`docs/onboarding-local.md`).
- [x] UI shell supports templates, runs, assistant, and builder route flow.
- [x] AI mode switching is available via env (`MOCK_MODE` + AI settings), with backend capability endpoint support.
- [x] Accessibility baseline for keyboard/focus on core UI paths is implemented.

## Latest verification snapshot

- Command:
  - `python -m pytest backend/app/tests/test_workflows_headless_lifecycle.py backend/app/tests/test_workflows_openapi.py backend/app/tests/test_assistant_proposals_api.py backend/app/tests/test_assistant_openapi.py backend/app/tests/test_run_inspection_ui_api.py backend/app/tests/test_ui_shell_navigation_smoke.py -q`
- Result:
  - `21 passed`

## Known non-blocking follow-ups

- Expand UI smoke automation beyond shell wiring as richer interactions evolve.
- Keep API fallback and API-backed behaviors in sync during future UI polish.
- Track accessibility regression checks in routine review for all new controls.

## Blockers

- None identified for MVP demo/release-readiness checkpoint.
