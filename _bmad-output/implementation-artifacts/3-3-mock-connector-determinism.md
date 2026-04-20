---
story_key: 3-3-mock-connector-determinism
epic: 3
status: done
sprint: 1
story_prepared_on: '2026-04-20'
---

# Story 3.3: MOCK connector determinism

Status: **done** - deterministic mock behavior accepted after code review.

## Story

As a **CI pipeline**,  
I can **run workflows in MOCK_MODE** without external network,  
So that **tests are stable** (FR24, NFR-I2).

## Acceptance criteria

1. **Given** MOCK_MODE true, **when** workflows run, **then** outbound provider calls use mock implementations with deterministic outcomes.

## Tasks / subtasks

- [x] Remove nondeterministic UUID usage from mock adapter outputs.
- [x] Replace wall-clock timestamps in mock order creation with deterministic sequence-based stamps.
- [x] Keep outputs unique per call sequence (so repeated calls in one run do not collide).
- [x] Add tests proving deterministic behavior across fresh adapter instances with identical call sequence.

## Dev notes

### Implementation summary

- Updated adapters:
  - `backend/app/adapters/banxa/client.py`
  - `backend/app/adapters/privy/client.py`
  - `backend/app/adapters/coinbase/client.py`
- Mock behavior now uses:
  - deterministic internal call sequence counters
  - stable SHA-256 digests from call inputs + sequence index
  - deterministic monotonic timestamp generation for Banxa mock order results (no sequence clamp at 60+ calls)

### Testing

Added:
- `backend/app/tests/test_mock_connector_determinism.py`
- Regression case for long sequences: `test_banxa_mock_timestamp_is_monotonic_beyond_sixty_calls`

Ran:

```bash
.venv/bin/python -m pytest backend/app/tests/test_mock_connector_determinism.py backend/app/tests -q
```

Result: **18 passed**

## Dev agent record

### Agent model used

Cursor agent (GPT-5.1)

### Completion notes list

- Mock adapters now avoid random UUID and non-repeatable wall-clock output in CI-sensitive paths.
- Determinism is scoped to identical call sequence and inputs across fresh adapter instances.
- Existing mock semantics remain intact (no external network and stable status values).
- Banxa mock timestamps remain deterministic and unique across long call sequences (>60 calls).

### File list

- `backend/app/adapters/banxa/client.py`
- `backend/app/adapters/privy/client.py`
- `backend/app/adapters/coinbase/client.py`
- `backend/app/tests/test_mock_connector_determinism.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/3-3-mock-connector-determinism.md`

## Change Log

- **2026-04-20** - Story 3-3 implemented; status -> review.
- **2026-04-20** - Story 3-3 accepted; status -> done.
- **2026-04-20** - Follow-up hardening: Banxa deterministic timestamp generation made monotonic for long sequences; added `>60` call regression test.
