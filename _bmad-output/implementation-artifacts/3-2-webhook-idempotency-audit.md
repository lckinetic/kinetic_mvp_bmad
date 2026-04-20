---
story_key: 3-2-webhook-idempotency-audit
epic: 3
status: done
sprint: 1
story_prepared_on: '2026-04-14'
---

# Story 3.2: Webhook idempotency & audit

Status: **done** - BMAD code review completed and accepted.

## Story

As a **support engineer**,  
I can **rely on stored payloads and idempotency keys**,  
So that **duplicate deliveries do not double-process** (FR27-FR29).

## Acceptance criteria

1. **Given** duplicate webhook delivery with same idempotency key, **when** processed, **then** side effects occur at most once.

## Tasks / subtasks

- [x] Keep webhook payload persistence as first step (store-before-process audit trail).
- [x] Ensure duplicate webhook deliveries with same idempotency key short-circuit and return duplicate response.
- [x] Ensure order side effects are not re-applied on duplicate deliveries.
- [x] Add integration test covering duplicate webhook behavior and event persistence expectations.

## Dev notes

### Implementation summary

- `backend/app/api/webhooks.py` updates:
  - narrowed duplicate handling catch from broad `Exception` to `IntegrityError` (explicit idempotency collision path)
  - marks `WebhookEvent.processed = True` after first successful processing path and commits the flag
- Added integration test `backend/app/tests/test_webhook_idempotency_audit.py`:
  - seeds an order
  - sends same webhook twice with identical `X-Idempotency-Key`
  - asserts first call `received`, second call `duplicate_ignored`
  - asserts event row count remains 1 and order update is not re-applied

### Testing

```bash
.venv/bin/python -m pytest backend/app/tests/test_webhook_idempotency_audit.py -q
.venv/bin/python -m pytest backend/app/tests -q
```

Results:
- webhook idempotency test: **1 passed**
- full backend suite: **14 passed**

## Dev agent record

### Agent model used

Cursor agent (GPT-5.1)

### Completion notes list

- Idempotency path now explicitly handles only uniqueness collisions (safer than broad exception swallow).
- Audit event `processed` state is now flipped on successful first-time processing.
- Duplicate deliveries with same key are proven to avoid duplicate side effects.

### File list

- `backend/app/api/webhooks.py`
- `backend/app/tests/test_webhook_idempotency_audit.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/3-2-webhook-idempotency-audit.md`

## Change Log

- **2026-04-14** - Story 3-2 implemented; status -> review.
- **2026-04-14** - BMAD code review completed; status -> done.
