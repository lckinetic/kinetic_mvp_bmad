---
story_key: 8-4-ui-kit-static-path-hardening
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 8.4: UI kit static path hardening (blank-screen fix)

Status: **done** - fixed UI blank-screen regression by hardening script asset paths for same-origin static hosting.

## Story

As a **demo user**,  
I want **the UI kit to load component scripts reliably regardless of URL form**,  
So that **the runner and app shell render consistently without empty-screen failures**.

## Acceptance criteria

1. **Given** the backend static mount at `/ui-kit`, **when** users access `/ui-kit` or `/ui-kit/`, **then** component scripts load from absolute `/ui-kit/...` paths.
2. **Given** the templates screen, **when** the user opens a template in runner, **then** the UI renders and remains interactive instead of blanking.

## Completion notes

- Updated `ui_kits/app/index.html` script tags from relative sources to absolute `/ui-kit/...` sources:
  - `/ui-kit/Components.jsx`
  - `/ui-kit/WorkflowRunner.jsx`
  - `/ui-kit/AIGenerator.jsx`
  - `/ui-kit/WorkflowBuilder.jsx`
- Verified endpoints return HTTP 200 for component scripts.
- Verified `/ui-kit` redirect behavior to `/ui-kit/` remains healthy.
- Confirmed user-visible outcome: runner and template flow now render successfully.

## File list

- `ui_kits/app/index.html`

## Change Log

- **2026-04-26** - Story 8.4 captured and marked done after UI blank-screen mitigation validation.
