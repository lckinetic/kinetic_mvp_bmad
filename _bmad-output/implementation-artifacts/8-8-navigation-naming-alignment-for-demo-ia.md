---
story_key: 8-8-navigation-naming-alignment-for-demo-ia
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-28'
---

# Story 8.8: Navigation naming alignment for demo IA

Status: **done** - code review completed and story accepted.

## Story

As a **demo stakeholder**,  
I want **the main navigation labels to match business language**,  
So that **screen names are clearer during walkthroughs and reduce translation overhead**.

## Acceptance criteria

1. **Given** the primary app navigation, **when** the UI renders, **then** the four labels are `Workflows`, `Operations`, `AI Assistant`, and `Workflow Builder`.
2. **Given** route transitions, **when** navigating between tabs, **then** display-name changes do not alter route identifiers or break existing navigation behavior.

## Completion notes

- Updated `APP_ROUTES` display labels and titles in `ui_kits/app/index.html`:
  - `Templates` -> `Workflows`
  - `Runs` -> `Operations`
  - `Assistant` -> `AI Assistant`
  - `Builder (mock)` -> `Workflow Builder`
- Kept route IDs unchanged (`templates`, `runs`, `assistant`, `builder`) to preserve navigation behavior and hash routing compatibility.
- Ran lint checks for modified UI file with no errors.

## File list

- `ui_kits/app/index.html`

## Change Log

- **2026-04-28** - Story 8.8 created and implementation captured; status -> review.
- **2026-04-28** - Code review completed; status -> done.
