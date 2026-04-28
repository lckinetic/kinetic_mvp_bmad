---
story_key: 8-7-builder-default-showcase-workflow-with-logic
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-28'
---

# Story 8.7: Builder default showcase workflow with logic

Status: **done** - code review completed and story accepted.

## Story

As a **demo operator**,  
I want **Builder to open with a prebuilt workflow covering all supported mock components and trigger logic**,  
So that **stakeholders can immediately see end-to-end orchestration patterns without manual setup**.

## Acceptance criteria

1. **Given** the Builder page loads, **when** the canvas initializes, **then** it includes a default multi-step workflow that uses all supported palette component types.
2. **Given** default links on that workflow, **when** inspecting connections, **then** they include both `always` and `conditional` trigger examples.
3. **Given** export JSON action, **when** data is copied, **then** the default workflow name and trigger metadata are present for demo playback.

## Completion notes

- Added a dedicated default workflow builder initializer that composes all supported step types into one demo graph.
- Seeded default edges with both `always` and `conditional` trigger logic and sample expressions.
- Set the Builder default workflow name to `demo_treasury_orchestration`.
- Updated initial Builder state to load from the default demo workflow scaffold at page load.

## File list

- `ui_kits/app/WorkflowBuilder.jsx`

## Change Log

- **2026-04-28** - Story 8.7 created and implementation captured; status -> review.
- **2026-04-28** - Code review completed; status -> done.
