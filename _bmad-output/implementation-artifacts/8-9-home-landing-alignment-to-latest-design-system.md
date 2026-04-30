---
story_key: 8-9-home-landing-alignment-to-latest-design-system
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-30'
---

# Story 8.9: Home landing alignment to latest design system

Status: **done** - code review completed and story accepted.

## Story

As an **investor-demo audience member**,  
I want **the Home landing page to match the latest approved design-system homepage**,  
So that **Kinetic's narrative, visual quality, and walkthrough guidance are consistent with the investor deck**.

## Acceptance criteria

1. **Given** app load on Home, **when** the page renders, **then** content and layout follow the latest `kinetic-design-system` homepage design for hero, problem/solution, architecture, use cases, and roadmap.
2. **Given** Home CTAs and screen cards, **when** users click them, **then** navigation routes to existing app pages without modifying those pages.
3. **Given** scope control, **when** this story is implemented, **then** only Home is changed while Workflows, Operations, AI Assistant, and Workflow Builder remain functionally unchanged.

## Completion notes

- Added new `ui_kits/app/Home.jsx` by porting and adapting the latest design-system homepage.
- Wired `index.html` to load `/ui-kit/Home.jsx` and render `Home` for the `home` route.
- Mapped Home CTA routing to existing app route IDs (`templates`, `runs`, `assistant`, `builder`) to preserve current navigation structure.
- Replaced only Home-route content; no functional changes were applied to other feature pages.
- Added follow-up UX copy alignment on Workflows template-detail CTAs to reflect updated page naming (`Open in Workflows`, `Edit in Workflow Builder (mock)`).

## File list

- `ui_kits/app/Home.jsx`
- `ui_kits/app/index.html`

## Change Log

- **2026-04-30** - Story 8.9 created and implementation captured; status -> review.
- **2026-04-30** - Code review completed; status -> done.
