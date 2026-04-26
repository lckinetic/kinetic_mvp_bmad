# kinetic-mvp-bmad — Documentation Index

**Type:** Monolith (FastAPI backend + docs + BMad tooling)  
**Primary language:** Python 3.11+  
**Last updated:** 2026-04-12

## Project overview

Kinetic MVP is a **FastAPI** backend for **crypto on/off-ramp** flows, **webhooks**, and **workflow** execution, with **PostgreSQL** persistence and a strong emphasis on **`MOCK_MODE`** for safe demos. Narrative scope and goals: **`overview.md`**.

## Quick reference

| Topic | Location |
|--------|----------|
| Product scope | [`overview.md`](./overview.md) |
| Architecture (short) | [`architecture.md`](./architecture.md) |
| Architecture principles (guardrails) | [`ai/architecture-principles.md`](./ai/architecture-principles.md) |
| Local onboarding (canonical path) | [`onboarding-local.md`](./onboarding-local.md) |
| MVP demo walkthrough | [`demo-mvp-flow.md`](./demo-mvp-flow.md) |
| Release readiness checkpoint | [`release-readiness-checklist.md`](./release-readiness-checklist.md) |
| Stakeholder handoff one-pager | [`stakeholder-handoff.md`](./stakeholder-handoff.md) |
| Onramp | [`onramp.md`](./onramp.md) |
| Offramp feature notes | [`features/offramp-mvp.md`](./features/offramp-mvp.md) |
| Mock mode ADR | [`adr-001-mock-mode.md`](./adr-001-mock-mode.md) |
| AI / QA checklist | [`ai/qa-checklist.md`](./ai/qa-checklist.md), [`ai/feature-template.md`](./ai/feature-template.md) |
| Postman | [`postman/`](./postman/) |
| Diagrams | `kinetic_system_overview.drawio`, `kinetic_workflow_engine.drawio` |

## BMad alignment (this pass)

| Artifact | Purpose |
|----------|---------|
| [`project-overview.md`](./project-overview.md) | Executive summary and classification for agents |
| [`source-tree-analysis.md`](./source-tree-analysis.md) | Annotated tree and critical folders |
| [`../_bmad-output/project-context.md`](../_bmad-output/project-context.md) | **Lean rules for AI implementers** — read before coding |
| [`project-scan-report.json`](./project-scan-report.json) | Scan state for `document-project` workflow resume |

## Generated / canonical docs

- **BMad project context (rules for agents):** [`../_bmad-output/project-context.md`](../_bmad-output/project-context.md)
- **This index, overview, source tree:** BMad `document-project` alignment (2026-04-12)

## Getting started

1. Follow [`onboarding-local.md`](./onboarding-local.md) end-to-end.
2. Keep `MOCK_MODE=true` for local demos.
3. Open **`/docs`** for OpenAPI; use Postman collections under **`docs/postman/`**.

## For AI-assisted development

1. **Always read** [`../_bmad-output/project-context.md`](../_bmad-output/project-context.md) before implementation work.
2. For layering and MVP constraints, follow [`ai/architecture-principles.md`](./ai/architecture-principles.md).
3. For new HTTP surface area, update docs and Postman per principles (section 7 in architecture-principles).

---

_Documentation index maintained for BMad Method alignment; full `document-project` workflow can extend this with API/data model deep dives on request._
