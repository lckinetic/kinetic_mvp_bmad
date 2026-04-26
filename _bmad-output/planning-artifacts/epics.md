---
stepsCompleted:
  - synthesized-2026-04-12
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
---

# kinetic-mvp-bmad — Epic Breakdown

## Overview

Epics decompose `prd.md` **FR1–FR35** and architecture decisions into phased delivery aligned with **Project Scoping** (refactor -> engine/API -> Docker/polish). A UX baseline is now available in `_bmad-output/planning-artifacts/ux-design-epic-4.md`, and the UI kit baseline has been imported under `ui_kits/app`.

## Requirements inventory

### Functional requirements (from PRD)

FR1–FR4: Workflow definition & catalog  
FR5–FR9: Workflow execution & lifecycle  
FR10–FR14: Conversational authoring (assistant)  
FR15–FR18: Web application  
FR19–FR22: HTTP API (prebuilt, headless)  
FR23–FR26: Provider & connector integration  
FR27–FR29: Webhooks & inbound events  
FR30–FR32: Observability, support & audit  
FR33–FR34: Documentation & discoverability  
FR35: Administration & tenancy (MVP posture)

### Non-functional requirements (from PRD)

NFR-P1–P3 Performance · NFR-S1–S4 Security · NFR-R1–R2 Reliability · NFR-I1–I2 Integration · NFR-O1–O2 Observability · NFR-SC1 Scalability posture · NFR-A1 Accessibility · NFR-D1 Documentation

### Additional / UX

- **UX spec:** Available at `_bmad-output/planning-artifacts/ux-design-epic-4.md`.
- **UI freeze decision (2026-04-24):** Keep the current `ui_kits/app` implementation as a frozen MVP UI baseline for testing; defer deeper UI integration/polish until backend epics are completed.

### FR coverage map

| Epic | FR range (primary) |
|------|-------------------|
| E1 Foundations | FR layering, NFR-O2, NFR-D1 (partial), project-context alignment |
| E2 Workflow API | FR19–FR22, FR33, NFR-P2, NFR-D1 |
| E3 Engine & connectors | FR5–FR9, FR23–FR26, FR27–FR29, NFR-R1–R2, NFR-I1–I2 |
| E4 Web app | FR15–FR18, FR1–FR4 (UI path), NFR-P1, NFR-A1 |
| E5 Assistant | FR10–FR14, NFR-P3 |
| E6 Ops & observability | FR30–FR32, FR34, NFR-O1, NFR-S1–S4 |
| E7 Docker & hardening | Local deploy, phased C, NFR-SC1 |

---

## Epic list

1. **E1 — Platform foundations & refactor** (monolith boundaries, hygiene)  
2. **E2 — Workflow HTTP API (prebuilts)** (headless parity)  
3. **E3 — Engine, connectors & webhooks** (execution + integrations)  
4. **E4 — Customer web app** (React-direction authoring & runs; currently frozen at UI baseline)  
5. **E5 — Conversational assistant** (authoring assistance)  
6. **E6 — Observability, support & documentation**  
7. **E7 — Docker, local env & release discipline**

### Sprint sequencing update (2026-04-24)

Execution order for the next phase is:

1. Continue backend-heavy delivery with **E5 -> E6 -> E7**
2. Keep **E4** in maintenance-only mode (blocker fixes for testing only)
3. Return to full **E4** integration/polish after backend epics stabilize

---

## Epic 1: Platform foundations & refactor

**Goal:** Enforce **API → services → adapters → DB** boundaries; reduce coupling; align with `project-context.md` and ADR-A1.

### Story 1.1: Module boundary audit & targeted refactors

As a **developer**,  
I want **clear packages and import rules** for api/services/adapters/engine/db,  
So that **changes stay localized** and reviewers can enforce layering.

**Acceptance criteria**

- **Given** the repo after refactor, **when** a reviewer inspects `backend/app`, **then** API modules do not import adapters directly except via services (documented exceptions listed if any).  
- **And** `docs/` or `architecture.md` references the boundary rules.

### Story 1.2: Settings & secrets hygiene

As an **operator**,  
I want **secrets excluded from logs and API errors**,  
So that **demos and logs stay safe** (NFR-S1, FR32).

**Acceptance criteria**

- **Given** startup and error paths, **when** logs and client errors are emitted, **then** no raw API keys or webhook secrets appear in payloads documented as user-visible.

---

## Epic 2: Workflow HTTP API (prebuilts)

**Goal:** **Raj** journey—list/start/status for **prebuilt** definitions (`FR19–FR22`).

### Story 2.1: OpenAPI for workflow surfaces

As an **integration engineer**,  
I can **discover workflow HTTP endpoints** via OpenAPI,  
So that **clients generate correct calls** (FR33, NFR-D1).

**Acceptance criteria**

- **Given** a running API, **when** I open `/docs` or the served OpenAPI JSON, **then** workflow list/start/status routes are described with request/response schemas.

### Story 2.2: Headless run lifecycle

As an **integration client**,  
I can **list prebuilts, start a run, poll to completion**,  
Without **using the SPA** (FR19–FR21).

**Acceptance criteria**

- **Given** MOCK_MODE, **when** I start a run via HTTP, **then** status and final state match canonical statuses and are retrievable without browser session.

### Story 2.3: Actionable API errors

As an **integration client**,  
I receive **structured errors** on 4xx/5xx,  
So that **I can fix requests or retry idempotently** (FR22, NFR-R1).

**Acceptance criteria**

- **Given** invalid input or conflict, **when** the API responds, **then** the body includes a **machine-readable code** and message (envelope per ADR-A2).

---

## Epic 3: Engine, connectors & webhooks

**Goal:** Reliable **WorkflowRun** lifecycle; **MOCK** adapters; **webhook** store/dedupe (`FR5–FR9`, `FR23–FR29`).

### Story 3.1: Canonical status enforcement

As a **system**,  
I **persist only normalised statuses** on core entities,  
So that **UI, API, and DB stay consistent** (FR25, NFR-R2).

**Acceptance criteria**

- **Given** provider callbacks with heterogeneous strings, **when** persisted on domain tables, **then** values map to the documented canonical set only.

### Story 3.2: Webhook idempotency & audit

As a **support engineer**,  
I can **rely on stored payloads and idempotency keys**,  
So that **duplicate deliveries do not double-process** (FR27–FR29).

**Acceptance criteria**

- **Given** duplicate webhook delivery with same idempotency key, **when** processed, **then** side effects occur at most once.

### Story 3.3: MOCK connector determinism

As a **CI pipeline**,  
I can **run workflows in MOCK_MODE** without external network,  
So that **tests are stable** (FR24, NFR-I2).

**Acceptance criteria**

- **Given** MOCK_MODE true, **when** workflows run, **then** outbound provider calls use mock implementations with deterministic outcomes.

---

## Epic 4: Customer web app

**Goal:** **Maya** journey—author/run in UI; migrate off ad hoc HTML/JS toward **maintainable** stack (FR15–FR18, FR1–FR4 UI path).
**Status note (2026-04-24):** UI baseline is frozen for now (`ui_kits/app/index.html` + imported sibling `.jsx` files). Remaining Epic 4 scope is deferred until backend epics are complete.
**UX baseline artifact:** `_bmad-output/planning-artifacts/ux-design-epic-4.md` (use this before pixel-level implementation for stories 4.1-4.3).

### Story 4.1: App shell & navigation

As a **user**,  
I can **navigate templates, runs, and assistant entry**,  
So that **core areas are reachable** (FR18).

**Acceptance criteria**

- **Given** logged-in or dev access model, **when** I use the app, **then** I reach list/detail flows for definitions and runs without dead ends.

### Story 4.2: Template browse & run (UI)

As an **operator**,  
I can **start a prebuilt workflow from the UI** in MOCK_MODE,  
So that **I can demo without Postman** (FR1–FR2, FR5–FR7).

**Acceptance criteria**

- **Given** MOCK_MODE, **when** I start a run from UI, **then** status updates are visible through completion or failure with reason.

### Story 4.3: Accessibility baseline

As a **user**,  
I can **use keyboard navigation** on primary flows,  
So that **we meet NFR-A1** for core paths.

**Acceptance criteria**

- **Given** core authoring/run pages, **when** navigating by keyboard, **then** focus order is logical and interactive controls are reachable.

---

## Epic 5: Conversational assistant

**Goal:** **Alex** journey—NL → validated proposal → optional handoff to UI (`FR10–FR14`).

### Story 5.1: Chat session & proposal

As an **author**,  
I can **describe intent in chat** and **receive a structured proposal**,  
So that **I draft workflows faster** (FR10–FR11).

**Acceptance criteria**

- **Given** assistant enabled, **when** I submit a prompt, **then** the system returns a proposal artefact the engine can validate or rejects with reason.

### Story 5.2: Confirm before execute

As an **author**,  
I must **confirm** before a proposed workflow **runs or persists**,  
So that **mistakes are caught** (FR12, ADR-A4).

**Acceptance criteria**

- **Given** a proposal, **when** I have not confirmed, **then** no run side effects occur.

### Story 5.3: UI handoff

As an **author**,  
I can **open the proposal in the builder** for edits,  
So that **I can refine after chat** (FR13).

**Acceptance criteria**

- **Given** an accepted proposal, **when** I choose “edit in UI”, **then** the builder loads equivalent structure for editing.

---

## Epic 6: Observability, support & documentation

**Goal:** **Jordan/Sam** journeys; engineer onboarding (`FR30–FR34`, `NFR-O1`).

### Story 6.1: Run inspection UI/API

As a **support user**,  
I can **inspect run history, steps, and webhook payloads**,  
So that **I can explain failures** (FR30–FR31).

**Acceptance criteria**

- **Given** a failed run, **when** I inspect it, **then** I see status history and relevant stored payloads where applicable.

### Story 6.2: Onboarding documentation

As a **new engineer**,  
I can **run the stack locally** using documented steps,  
So that **I onboard in one session** (FR34, NFR-O2).

**Acceptance criteria**

- **Given** the README/docs path, **when** I follow steps, **then** I reach healthy API and DB with MOCK_MODE demo path.

---

## Epic 7: Docker, local env & release discipline

**Goal:** Phase C—**Dockerised** app + polish; reproducibility (`NFR-O2`, PRD operations).

### Story 7.1: Compose stack for app + DB

As a **developer**,  
I can **`docker compose up`** the dependencies (and optionally app),  
So that **my environment matches team defaults**.

**Acceptance criteria**

- **Given** compose files, **when** I run them per docs, **then** Postgres (and app if included) start with documented ports and env wiring.

### Story 7.2: CI smoke for workflow API

As a **tech lead**,  
I want **CI to run contract/smoke tests** on workflow endpoints in MOCK_MODE,  
So that **API parity does not regress** (innovation validation).

**Acceptance criteria**

- **Given** CI pipeline, **when** it runs, **then** at least one test exercises list/start/status for prebuilts in MOCK_MODE.

---

## Epic 8: Post-MVP hardening and demo reliability

**Goal:** Lock in demo-safe operations and eliminate high-friction runtime failures discovered during end-to-end MVP validation.

### Story 8.1: AI mode switching and capabilities

As a **demo operator**,  
I want **deterministic mock mode and real AI mode selectable via environment settings**,  
So that **I can run safe demos or live AI experiences on demand**.

### Story 8.2: Secret safety and error hardening

As an **operator**,  
I want **structured AI failure envelopes and strict secret redaction**,  
So that **keys are never exposed in logs, responses, or diagnostics**.

### Story 8.3: Demo operations tooling and docs

As a **project lead**,  
I want **simple mode-switch scripts and canonical demo/release docs**,  
So that **team and stakeholder walkthroughs stay repeatable**.

### Story 8.4: UI kit static path hardening (blank-screen fix)

As a **demo user**,  
I want **the UI kit to load component scripts reliably regardless of URL form**,  
So that **the runner does not render a blank screen during MVP demos**.

**Acceptance criteria**

- **Given** the UI is served at `/ui-kit` or `/ui-kit/`, **when** the page loads, **then** all JSX component scripts are requested from stable absolute paths and return HTTP 200.
- **And** **given** Templates -> Open in runner, **when** opening the runner view, **then** the app shell and runner content render without a blank screen regression.

### Story 8.5: Builder node-linking visuals (UI-only enhancement)

As a **demo user**,  
I want **to draw linking arrows between workflow boxes on the Builder canvas**,  
So that **the workflow path is visually understandable during demos even without backend persistence**.

**Acceptance criteria**

- **Given** the Builder page in demo mode, **when** I add two or more boxes and select a source/target pair, **then** a visible directional arrow is rendered between those boxes.
- **And** **given** linked boxes, **when** I reposition linked nodes, **then** arrow positions update to remain connected to the correct nodes.
- **And** **given** this is a UI-only enhancement, **when** links are created or removed, **then** no backend API calls are required for the interaction.
