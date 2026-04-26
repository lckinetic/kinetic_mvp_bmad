---
story_key: 8-1-ai-mode-switching-capabilities
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 8.1: AI mode switching and capabilities

Status: **done** - backend and UI now support clear mock/live AI mode switching.

## Story

As a **demo operator**,  
I want **deterministic mock mode and real AI mode selectable via environment settings**,  
So that **I can run safe demos or live AI experiences on demand**.

## Acceptance criteria

1. **Given** environment configuration, **when** backend starts, **then** AI mode is selected by config and exposed via a capabilities endpoint.
2. **Given** UI app shell and assistant flow, **when** backend mode changes, **then** UI surfaces reflect mock vs live mode correctly.

## Completion notes

- Added AI config fields and runtime validation for live mode requirements.
- Implemented AI service factory with mock interpreter path and OpenAI live path.
- Added `/ai/capabilities` and `/ai/config-status` for non-secret runtime diagnostics.
- Updated UI badge and assistant flow to consume backend AI mode/capabilities.

## File list

- `backend/app/core/config.py`
- `backend/app/ai/service.py`
- `backend/app/api/ai.py`
- `ui_kits/app/index.html`
- `ui_kits/app/AIGenerator.jsx`
- `backend/.env.example`
- `backend/.env.mock.example`
- `backend/.env.live.example`

## Change Log

- **2026-04-26** - Story 8.1 recorded post-implementation; status -> done.
