---
story_key: 8-2-secret-safety-error-hardening
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 8.2: Secret safety and error-envelope hardening

Status: **done** - AI failure handling and secret redaction were hardened for live mode safety.

## Story

As a **platform owner**,  
I want **AI errors to follow structured envelopes and never leak secrets**,  
So that **live-mode failures stay safe and diagnosable**.

## Acceptance criteria

1. **Given** AI interpret failures, **when** API responds, **then** response uses structured error envelope with sanitized details.
2. **Given** startup logs and API errors, **when** secrets are present in config, **then** sensitive values are masked.

## Completion notes

- Added structured `AI_INTERPRET_FAILED` error response path in `/ai/interpret`.
- Ensured failure reasons pass through secret redaction before exposure.
- Included OpenAI key in redaction coverage.
- Added tests to verify no API key leakage in responses or safe logs.

## File list

- `backend/app/api/ai.py`
- `backend/app/core/secrets_redact.py`
- `backend/app/main.py`
- `backend/app/tests/test_ai_mode_switching.py`
- `backend/app/tests/test_secrets_redact.py`

## Change Log

- **2026-04-26** - Story 8.2 recorded post-implementation; status -> done.
