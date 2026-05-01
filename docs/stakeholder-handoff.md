# Stakeholder Handoff (MVP)

This handoff summarizes where to start, what to demo, and current release-readiness status.

## What is ready

- Backend and UI MVP scope across Epics 1-7 is completed.
- Core workflow, assistant, support inspection, onboarding, compose, CI smoke, and UI accessibility baseline are in place.
- Latest consolidated smoke suite passed locally (`25 passed`).
- AI execution mode can now be switched via env:
  - demo-safe mock mode
  - live mode with real model/API key
- UI static-path hardening was applied to prevent intermittent blank-screen rendering in the runner flow when loading from `/ui-kit`.

## Start here

- Local setup and run path:
  - `docs/onboarding-local.md`
- Canonical demo walkthrough:
  - `docs/demo-mvp-flow.md`
- Release-readiness checkpoint:
  - `docs/release-readiness-checklist.md`

## Demo narrative (recommended)

1. Start on Home to explain Kinetic value proposition and screen sequence.
2. Show workflow browsing and open a template in Workflows.
3. Start a workflow run and show run status + step details.
4. Show run history/detail context from Operations.
5. Show AI Assistant-driven workflow generation.
6. Show Workflow Builder (mock) entry/editability and keyboard accessibility highlights.

## Current risk posture

- No blockers identified for MVP demo/handoff.
- Remaining follow-ups are polish/coverage expansions (non-blocking), tracked in `docs/release-readiness-checklist.md`.

## Suggested immediate next actions

- Run one stakeholder demo using `docs/demo-mvp-flow.md` as script.
- Capture feedback as post-MVP backlog items.
- Keep onboarding/demo/readiness docs as the single source of truth for future handoffs.
