---
story_key: 5-3-ui-handoff
epic: 5
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 5.3: UI handoff

Status: **done** - UI handoff implementation accepted after code review completion.

## Story

As an **author**,  
I can **open the proposal in the builder** for edits,  
So that **I can refine after chat** (FR13).

## Acceptance criteria

1. **Given** an accepted proposal, **when** I choose "edit in UI", **then** the builder loads equivalent structure for editing.

## Tasks / subtasks

- [x] Define normalized handoff payload contract from assistant proposal to UI builder format.
- [x] Add backend endpoint to produce builder-ready payload from confirmed proposal.
- [x] Ensure handoff endpoint only allows proposals in valid state (confirmed/executed as required by ADR intent).
- [x] Return structured error envelopes for missing proposal, invalid state, or conversion failures.
- [x] Add tests validating handoff shape and state gating.
- [x] Add OpenAPI checks for new handoff route and schema components.

## Dev notes

### Implementation summary

- Added `build_ui_handoff()` in `backend/app/services/assistant_proposals.py` to map proposal workflow steps into builder-style `nodes` and `edges`.
- Added state guardrail in service: UI handoff requires confirmed proposal state (`ProposalInvalidStateError` otherwise).
- Enhanced handoff mapping to preserve explicit branch topology (`next` / `next_steps` / branch-like links) when present; falls back to linear edges only when no explicit links exist.
- Added API route in `backend/app/api/assistant.py`:
  - `GET /assistant/proposals/{proposal_id}/ui-handoff`
- Added structured invalid-state error response:
  - `409` with `code: INVALID_PROPOSAL_STATE`
- Added response schema model `AssistantBuilderHandoffResponse`.

### Expected implementation touchpoints

- `backend/app/api/assistant.py`
- `backend/app/services/assistant_proposals.py`
- `backend/app/tests/` for API/openapi/handoff contract tests

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Implemented proposal-to-builder handoff endpoint and deterministic payload mapping.
- Added API tests for state gating and successful handoff payload shape.
- Added regression test proving branch-aware edge preservation in UI handoff payloads.
- Added OpenAPI coverage for the new `/ui-handoff` route and schema.
- Ran targeted tests: `.venv/bin/python -m pytest backend/app/tests/test_assistant_proposals_api.py backend/app/tests/test_assistant_openapi.py -q` (14 passed).

### File list

- `_bmad-output/implementation-artifacts/5-3-ui-handoff.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/services/assistant_proposals.py`
- `backend/app/api/assistant.py`
- `backend/app/tests/test_assistant_proposals_api.py`
- `backend/app/tests/test_assistant_openapi.py`

## Change Log

- **2026-04-26** - Story 5.3 created and kicked off; status -> in-progress.
- **2026-04-26** - Story 5.3 implemented; status -> review.
- **2026-04-26** - Follow-up hardening: UI handoff now preserves explicit branch edges; added regression test for branched workflow mapping.
- **2026-04-26** - Story 5.3 code review completed; status -> done.
