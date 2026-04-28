---
story_key: 8-6-builder-usability-polish-and-mock-labeling
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-28'
---

# Story 8.6: Builder usability polish and mock labeling

Status: **done** - code review completed and story accepted.

## Story

As a **demo user**,  
I want **newly dropped nodes to reliably stay selected and clearly see that Builder is mock-only**,  
So that **the config panel behavior feels predictable and demo expectations are set correctly**.

## Acceptance criteria

1. **Given** a node is added from the palette via drag/drop or keyboard add, **when** it appears on the canvas, **then** the node remains selected and its configuration panel is visible.
2. **Given** a drop/link interaction just completed, **when** the next click event occurs, **then** selection is not immediately cleared by accidental click bubbling.
3. **Given** app navigation and page header labels, **when** Builder is shown, **then** it is labeled as `Builder (mock)`.

## Completion notes

- Added post-drop selection stabilization in Builder so newly created nodes are auto-selected and remain selected.
- Added a short-lived canvas click suppression guard to avoid immediate deselection after drop/link completion.
- Updated navigation/page metadata label from `Builder` to `Builder (mock)` and title to `Workflow builder (mock)`.
- Changes are UI-only and do not add backend dependencies.
- Added static smoke-test hardening to guard selection-stability click suppression wiring (`test_builder_post_drop_click_suppression_wiring_is_present`).

## File list

- `ui_kits/app/WorkflowBuilder.jsx`
- `ui_kits/app/index.html`

## Change Log

- **2026-04-28** - Story 8.6 created and implementation captured; status -> review.
- **2026-04-28** - Added review follow-up smoke-test coverage for post-drop click suppression/selection stability wiring.
- **2026-04-28** - Code review completed; status -> done.
