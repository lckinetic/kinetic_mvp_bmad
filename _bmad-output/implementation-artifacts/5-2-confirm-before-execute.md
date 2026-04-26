---
story_key: 5-2-confirm-before-execute
epic: 5
status: done
sprint: 1
story_prepared_on: '2026-04-24'
---

# Story 5.2: Confirm before execute

Status: **done** - confirmation gate accepted after code review completion.

## Story

As an **author**,  
I must **confirm** before a proposed workflow **runs or persists**,  
So that **mistakes are caught** (FR12, ADR-A4).

## Acceptance criteria

1. **Given** a proposal, **when** I have not confirmed, **then** no run side effects occur.

## Tasks / subtasks

- [x] Extend proposal model with explicit confirmation state and metadata (confirmed flag, timestamp).
- [x] Add confirmation endpoint to transition a proposal from draft/proposed -> confirmed.
- [x] Prevent any execute/persist operation unless proposal is confirmed.
- [x] Return structured, actionable error payload when execution/persist is attempted without confirmation.
- [x] Add tests for pre-confirmation block, confirmation success, and post-confirmation allow path.
- [x] Document confirmation-first contract in API/OpenAPI surfaces.

## Dev notes

### Implementation summary

- Extended proposal state in `backend/app/services/assistant_proposals.py`:
  - `confirmed`, `confirmed_at`, `executed_at`
  - `confirm_proposal()` and `execute_proposal()` service methods
- Replaced in-memory proposal store with DB-backed persistence via `AssistantProposal` (`backend/app/db/models.py`) so confirmation/execution state survives process restarts.
- Added explicit execution gate: unconfirmed proposals raise `ProposalNotConfirmedError`.
- Added new assistant API endpoints in `backend/app/api/assistant.py`:
  - `POST /assistant/proposals/{proposal_id}/confirm`
  - `POST /assistant/proposals/{proposal_id}/execute`
- Execution before confirmation now returns structured `409` with code `CONFIRMATION_REQUIRED`.
- Confirm-after-execute behavior is explicitly idempotent no-op (re-confirm returns the unchanged executed proposal).

### Expected implementation touchpoints

- `backend/app/api/assistant.py`
- `backend/app/services/assistant_proposals.py`
- `backend/app/tests/` for API and service flow coverage

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Implemented confirmation-first workflow and explicit pre-execution guard rails.
- Added API tests for blocked execute-before-confirm, confirm success, and execute-after-confirm success.
- Added persistence test proving proposals remain retrievable after app recreation (same DB backend).
- Added explicit idempotency test for confirm-after-execute no-op contract.
- Extended OpenAPI route coverage for new confirm/execute endpoints.
- Ran targeted tests: `python -m pytest backend/app/tests/test_assistant_proposals_api.py backend/app/tests/test_assistant_openapi.py -q` (11 passed).

### File list

- `_bmad-output/implementation-artifacts/5-2-confirm-before-execute.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/services/assistant_proposals.py`
- `backend/app/db/models.py`
- `backend/app/api/assistant.py`
- `backend/app/tests/test_assistant_proposals_api.py`
- `backend/app/tests/test_assistant_openapi.py`

## Change Log

- **2026-04-24** - Story 5.2 created and kicked off; status -> in-progress.
- **2026-04-24** - Story 5.2 implemented; status -> review.
- **2026-04-26** - Follow-up hardening: assistant proposals moved to DB-backed persistence; confirm-after-execute idempotency contract + tests added.
- **2026-04-26** - Story 5.2 code review completed; status -> done.
