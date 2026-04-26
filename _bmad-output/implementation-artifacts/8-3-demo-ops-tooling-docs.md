---
story_key: 8-3-demo-ops-tooling-docs
epic: 8
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 8.3: Demo operations tooling and docs

Status: **done** - mode-switch scripts, demo flow docs, and handoff docs were finalized for investor/demo readiness.

## Story

As a **project lead**,  
I want **simple operational scripts and canonical docs for demo/readiness flow**,  
So that **internal and external demos are repeatable and low-risk**.

## Acceptance criteria

1. **Given** repo root scripts, **when** operator switches mode, **then** env selection is one command.
2. **Given** documentation index, **when** reviewers prepare demo/release checks, **then** canonical paths are clearly linked.

## Completion notes

- Added executable mode-switch scripts:
  - `scripts/use-mock.sh`
  - `scripts/use-live.sh`
- Added and updated docs for demo and release operations:
  - demo walkthrough
  - release-readiness checklist
  - stakeholder handoff
  - onboarding quick-switch guidance

## File list

- `scripts/use-mock.sh`
- `scripts/use-live.sh`
- `docs/onboarding-local.md`
- `docs/demo-mvp-flow.md`
- `docs/release-readiness-checklist.md`
- `docs/stakeholder-handoff.md`
- `docs/index.md`

## Change Log

- **2026-04-26** - Story 8.3 recorded post-implementation; status -> done.
