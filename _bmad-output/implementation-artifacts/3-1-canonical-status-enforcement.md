---
story_key: 3-1-canonical-status-enforcement
epic: 3
status: review
sprint: 1
story_prepared_on: '2026-04-14'
---

# Story 3.1: Canonical status enforcement

Status: **review** - canonical status normalization is now centralized and enforced before persistence.

## Story

As a **system**,  
I **persist only normalised statuses** on core entities,  
So that **UI, API, and DB stay consistent** (FR25, NFR-R2).

## Acceptance criteria

1. **Given** provider callbacks with heterogeneous strings, **when** persisted on domain tables, **then** values map to the documented canonical set only.

## Tasks / subtasks

- [x] Centralize canonical status vocabulary and normalization mappings in a shared service module.
- [x] Ensure onramp/offramp order creation persists normalized canonical status only.
- [x] Reuse shared normalization in webhook update path to avoid drift.
- [x] Add tests for mapping behavior and persistence outcomes on order creation services.

## Dev notes

### Implementation summary

- Added `backend/app/services/order_status.py`:
  - `CANONICAL_ORDER_STATUSES`
  - `normalize_order_status(raw)`
  - `normalize_order_status_or_default(raw, default="pending")`
- Updated order creation services:
  - `backend/app/services/orders/onramp_service.py`
  - `backend/app/services/orders/offramp_service.py`
  - Persist `order_status` via `normalize_order_status_or_default(...)`.
- Updated webhook normalization:
  - `backend/app/api/webhooks.py` now uses shared normalization helper and canonical set.

### Testing

Added: `backend/app/tests/test_order_status_normalization.py`

Suite run:

```bash
.venv/bin/python -m pytest backend/app/tests -q
```

Result: **13 passed**

## Dev agent record

### Agent model used

Cursor agent (GPT-5.1)

### Completion notes list

- Canonical status logic is now single-sourced, reducing drift risk between webhook and order-creation paths.
- Unknown provider statuses no longer persist raw values on order creation; they fall back to canonical `pending`.
- Existing webhook handling still ignores unusable statuses (no overwrite), preserving current behavior while sharing mappings.

### File list

- `backend/app/services/order_status.py`
- `backend/app/services/orders/onramp_service.py`
- `backend/app/services/orders/offramp_service.py`
- `backend/app/api/webhooks.py`
- `backend/app/tests/test_order_status_normalization.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/3-1-canonical-status-enforcement.md`

## Change Log

- **2026-04-14** - Story 3-1 implemented; status -> review.
