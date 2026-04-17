---
story_key: 2-3-actionable-api-errors
epic: 2
status: done
sprint: 1
story_prepared_on: '2026-04-13'
---

# Story 2.3: Actionable API errors

Status: **done** - BMAD code review completed and accepted.

## Story

As an **integration client**,  
I receive **structured errors** on 4xx/5xx,  
So that **I can fix requests or retry idempotently** (FR22, NFR-R1).

## Acceptance criteria

1. **Given** invalid input or conflict, **when** the API responds, **then** the body includes a **machine-readable code** and message (envelope per ADR-A2).

## Tasks / subtasks

- [x] Introduce centralized FastAPI exception handlers for request validation, HTTP exceptions, and unexpected exceptions.
- [x] Standardize response body shape to `{code, message, details}`.
- [x] Register handlers at app creation so all routes inherit envelope behavior.
- [x] Add integration tests for invalid input and not-found workflow errors asserting machine-readable code + message.

## Dev notes

### Implementation summary

- Added `backend/app/core/errors.py`:
  - `register_error_handlers(app)`
  - `RequestValidationError` -> `{"code":"VALIDATION_ERROR", ...}`
  - `HTTPException` -> code mapping (`BAD_REQUEST`, `NOT_FOUND`, `CONFLICT`, etc.)
  - fallback `Exception` -> `INTERNAL_SERVER_ERROR`
- Updated `backend/app/main.py` to call `register_error_handlers(app)`.
- Added `backend/app/tests/test_api_error_envelope.py` for workflow API assertions.

### Testing

```bash
.venv/bin/python -m pytest backend/app/tests/test_api_error_envelope.py backend/app/tests/test_workflows_headless_lifecycle.py -q
```

Result: **3 passed**

## Dev agent record

### Agent model used

Cursor agent (GPT-5.1)

### Completion notes list

- API responses for 4xx/5xx now return machine-readable error envelopes consistently.
- Existing endpoint-level `HTTPException(detail=...)` messages are preserved as `message`, with standardized `code`.
- Added tests proving invalid input and not-found lifecycle paths are actionable for integration clients.

### File list

- `backend/app/core/errors.py`
- `backend/app/main.py`
- `backend/app/tests/test_api_error_envelope.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/2-3-actionable-api-errors.md`

## Change Log

- **2026-04-14** - Story 2-3 implemented; status -> review.
- **2026-04-14** - BMAD code review completed; status -> done.
