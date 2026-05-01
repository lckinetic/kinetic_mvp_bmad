# Story 8.11: Documentation hygiene and naming/path alignment

## Status
done

## Story
As a project operator, I want core project docs to reflect the current UI naming, routing paths, and agent context entry points, so that contributors and demo stakeholders can follow accurate guidance without drift or confusion.

## Scope implemented
- Updated `readme.md` to include an "Agent Context Files" pointer to `claude.md`.
- Aligned UI route/path references to `/ui-kit/` where relevant.
- Updated `docs/demo-mvp-flow.md` to reflect current app IA and walkthrough sequence from `Home`.
- Updated `docs/stakeholder-handoff.md` to align naming and demo narrative with current tabs.

## Acceptance criteria check
1. Current tab names and `/ui-kit/` pathing reflected in canonical docs: **pass**
2. `readme.md` links users to `claude.md` for agent context: **pass**
3. No backend/API or runtime UI behavior changes introduced by this story: **pass**

## Notes
- This story tracks documentation consistency only; implementation work was intentionally limited to docs and context files.
