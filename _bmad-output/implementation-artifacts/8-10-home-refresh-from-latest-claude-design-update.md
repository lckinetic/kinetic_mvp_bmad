---
story_key: 8-10-home-refresh-from-latest-claude-design-update
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-05-01'
---

# Story 8.10: Home refresh from latest Claude design update

Status: **done** - code review completed and story accepted.

## Story

As a **demo stakeholder**,  
I want **Home to reflect the most recent Claude design iteration**,  
So that **messaging hierarchy, visual polish, and example content stay current with investor-facing narrative updates**.

## Acceptance criteria

1. **Given** latest design source in `Kinetic Design System`, **when** Home is synced, **then** updated Home visuals/content (cards, copy emphasis, use-case structure, roadmap wording) match that latest version.
2. **Given** app integration constraints, **when** Home is updated, **then** navigation actions still map to existing route IDs and other pages remain untouched.

## Completion notes

- Re-synced `ui_kits/app/Home.jsx` with the latest provided design-system Home page content/style update.
- Preserved route compatibility by mapping CTA and screen-card navigation to existing IDs (`templates`, `runs`, `assistant`, `builder`).
- Left non-Home pages unchanged.

## File list

- `ui_kits/app/Home.jsx`

## Change Log

- **2026-05-01** - Story 8.10 created and implementation captured; status -> review.
- **2026-05-01** - Code review completed; status -> done.
