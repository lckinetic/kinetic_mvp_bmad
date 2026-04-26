---
story_key: 4-1-app-shell-navigation
epic: 4
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 4.1: App shell and navigation

Status: **done** - app shell route map and navigation landings are implemented for Templates, Runs, Assistant, and Builder.

## Story

As a **user**,  
I can **navigate templates, runs, and assistant entry**,  
So that **core areas are reachable** (FR18).

## Acceptance criteria

1. **Given** logged-in or dev access model, **when** I use the app, **then** I reach list/detail flows for definitions and runs without dead ends.

## Tasks / subtasks

- [x] Define the canonical app shell route map for Templates, Runs, and Assistant entry.
- [x] Wire sidebar/top-level navigation to those canonical routes.
- [x] Ensure each top-level destination has an implemented landing view (no placeholders that dead-end navigation).
- [x] Align navigation labels and structure with `_bmad-output/planning-artifacts/ux-design-epic-4.md`.
- [x] Verify UI behavior in MOCK_MODE-compatible local flow.
- [x] Add/update lightweight UI smoke checks for shell navigation stability.
- [x] Document any route assumptions for Story 4.2 integration.

## Dev notes

### Implementation checklist (recommended order)

1. Audit existing `ui_kits/app` screens and identify reusable shell/navigation components.
2. Decide the route and state model that can evolve into Story 4.2 without rework.
3. Implement navigation wiring first (shell), then destination view handoff.
4. Verify every nav item has a reachable rendered destination.
5. Perform a focused smoke pass to confirm no runtime errors in primary nav paths.

### Expected implementation touchpoints

- `ui_kits/app/index.html`
- `ui_kits/app/Components.jsx`
- `ui_kits/app/*.jsx` screens used by app-shell navigation
- Optional docs note if route conventions need to be captured

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Implemented route-style app shell with canonical top-level destinations:
  - `templates`, `runs`, `assistant`, `builder`.
- Added hash-based route sync (`#templates`, `#runs`, `#assistant`, `#builder`) to make navigation state explicit and shareable.
- Added Templates landing with list/detail flow and explicit actions to open Runner or Builder.
- Added Runs landing with list/detail flow and status pills to remove dead-end top-level navigation.
- Kept existing Runner/Assistant/Builder screens intact and reachable from the new shell.
- Generalized `KSidebar` to accept dynamic nav items for Story 4.x evolution.
- Story 4.2 route assumptions captured: Templates and Runs route scaffolding is now present and can be wired to real API-backed data/state.

### File list

- `_bmad-output/implementation-artifacts/4-1-app-shell-navigation.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `ui_kits/app/index.html`
- `ui_kits/app/Components.jsx`

## Change Log

- **2026-04-26** - Story 4.1 kicked off; status -> in-progress.
- **2026-04-26** - Story 4.1 implemented; status -> review.
- **2026-04-26** - Story 4.1 code review completed; status -> done.
