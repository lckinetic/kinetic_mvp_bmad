---
story_key: 8-5-builder-node-linking-visuals-ui-only-enhancement
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 8.5: Builder node-linking visuals (UI-only enhancement)

Status: **done** - code review completed and story accepted.

## Story

As a **demo user**,  
I want **to draw linking arrows between workflow boxes on the Builder canvas**,  
So that **the workflow path is visually understandable during demos even without backend persistence**.

## Acceptance criteria

1. **Given** the Builder page in demo mode, **when** I add two or more boxes and select a source/target pair, **then** a visible directional arrow is rendered between those boxes.
2. **Given** linked boxes, **when** I reposition linked nodes, **then** arrow positions update to remain connected to the correct nodes.
3. **Given** this is a UI-only enhancement, **when** links are created or removed, **then** no backend API calls are required for the interaction.

## Completion notes

- Preserved existing drag-from-output-port to input-port connection flow.
- Added explicit **Connections** controls in the right-side properties panel for selected node:
  - choose a target step and create a link via button
  - view outgoing links   and remove them inline
- Reused existing SVG edge layer so directional arrows remain visible and auto-update when nodes move.
- Confirmed no backend calls are introduced; behavior remains local demo-only state.
- Improved drag-to-link reliability by allowing link drop on the full target node card (not only the small input port).
- Post-review hardening:
  - added an explicit labeled target-step selector and contextual remove-link `aria-label`s for better screen-reader support
  - added static smoke coverage for builder connection controls and add/remove handler wiring (`backend/app/tests/test_ui_builder_linking_smoke.py`)

## File list

- `ui_kits/app/WorkflowBuilder.jsx`

## Change Log

- **2026-04-26** - Story 8.5 kicked off; status set to in-progress.
- **2026-04-26** - Implemented UI-only node link add/remove controls; status -> review.
- **2026-04-26** - Applied review follow-up hardening for Connections panel accessibility and added builder-linking smoke tests.
- **2026-04-26** - Code review completed; status -> done.
- **2026-04-28** - Added follow-up UX reliability fix so dragging from output port can connect when released anywhere on target node.
