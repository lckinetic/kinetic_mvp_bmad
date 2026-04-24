---
story_key: 5-1-chat-session-proposal
epic: 5
status: done
sprint: 1
story_prepared_on: '2026-04-24'
---

# Story 5.1: Chat session & proposal

Status: **done** - implementation accepted after code review completion.

## Story

As an **author**,  
I can **describe intent in chat** and **receive a structured proposal**,  
So that **I draft workflows faster** (FR10-FR11).

## Acceptance criteria

1. **Given** assistant enabled, **when** I submit a prompt, **then** the system returns a proposal artefact the engine can validate or rejects with reason.

## Tasks / subtasks

- [x] Define assistant proposal schema for API and internal service boundary (proposal id, workflow summary, normalized steps, validation hints).
- [x] Implement a chat proposal service flow that maps natural-language prompt -> structured proposal in mock-safe mode.
- [x] Expose HTTP endpoint(s) for proposal creation and retrieval with structured success/error envelopes.
- [x] Add validation and rejection reasons for malformed or un-executable proposals.
- [x] Add tests for happy path, invalid prompt path, and deterministic mock behavior.
- [x] Document API contract in OpenAPI and update relevant planning/architecture notes if needed.

## Dev notes

### Implementation summary

- Added `backend/app/api/assistant.py` with:
  - `POST /assistant/proposals` to create a structured workflow proposal from a chat prompt
  - `GET /assistant/proposals/{proposal_id}` to retrieve stored proposals
- Added `backend/app/services/assistant_proposals.py` with deterministic proposal IDs, prompt actionability guardrails, workflow validation, and in-memory proposal storage.
- Registered assistant router in `backend/app/main.py`.
- Kept HTTP failures aligned with existing structured error envelope via `HTTPException` detail payloads (`INVALID_PROMPT`, `INVALID_PROPOSAL`, `NOT_FOUND`).

### Expected implementation touchpoints

- `backend/app/api/` for assistant proposal routes
- `backend/app/services/` for orchestration and proposal building
- `backend/app/engine/` only if proposal validation needs execution graph compatibility checks
- `backend/app/tests/` for API and service-level coverage

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Implemented assistant proposal API + service layer with deterministic proposal artifacts.
- Added rejection reasons for non-actionable prompts and invalid generated proposals.
- Added API tests for create/get/error paths and OpenAPI schema/path coverage.
- Ran targeted tests: `python -m pytest backend/app/tests/test_assistant_proposals_api.py backend/app/tests/test_assistant_openapi.py -q` (5 passed).

### File list

- `_bmad-output/implementation-artifacts/5-1-chat-session-proposal.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/api/assistant.py`
- `backend/app/services/assistant_proposals.py`
- `backend/app/main.py`
- `backend/app/tests/test_assistant_proposals_api.py`
- `backend/app/tests/test_assistant_openapi.py`

## Change Log

- **2026-04-24** - Story 5.1 created and kicked off; status -> in-progress.
- **2026-04-24** - Story 5.1 implemented; status -> review.
- **2026-04-24** - Story 5.1 code review completed; status -> done.
