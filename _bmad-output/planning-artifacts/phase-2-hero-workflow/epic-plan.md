---
phase: phase-2-hero-workflow
status: approved
approved: 2026-05-01
project_name: kinetic-mvp-bmad
brownfieldBaseline: Epics 1–9 complete
---

# Epic Plan — Stablecoin Treasury & Contractor Payout Operations

## Transformation Goal

Transform the existing Kinetic MVP into a **Stablecoin Treasury & Contractor Payout Operations** platform — the first operational domain of a Programmable Financial Operations Platform.

**Hero journey:** Create Workspace → Create Treasury Wallet → Fund Treasury → Add Recipient → Create Payout Workflow → Execute Workflow → Monitor Operations.

**Positioning:** Kinetic orchestrates and monitors; it does not compete as wallet, custody, or payment-rail infrastructure.

---

## Epic Sequencing

| Priority | Epic | Theme |
|----------|------|-------|
| 1 | **E10** | Onboarding & Workspace Foundation |
| 2 | **E11** | Treasury Management |
| 3 | **E12** | Recipient Management |
| 4 | **E13** | Workflow Management (Hero Contractor Payout) |
| 5 | **E14** | Activity Centre |
| 6 | **E15** | Monitoring & Alerts |
| 7 | **E16** | AI Workflow Assistant (Hero Payout Templates) |

**Build order:** E10 → E11 → E12 → E13 → E14/E15 → E16

---

## Cross-Cutting Technical Dependencies

| Layer | Reuse | Extend |
|-------|-------|--------|
| Engine | `runner.py`, `workflow_steps.py`, `metrics.py` | `contractor_payout` template |
| Adapters | Mock pattern, `MOCK_MODE` | Privy wallet/balance/transfer |
| DB | `WorkflowRun`, `WorkflowStep` | Workspace, Treasury, Recipient, WorkflowDefinition, Transfer, Activity, Alert |
| API | `/workflows`, `/ai`, error envelope | Domain routes scoped by `workspace_id` |
| AI | `AI_MOCK_MODE`, confirm-before-run | Payout NL schema; save draft → E13 |
| UI | `Components.jsx`, hash routing | Dashboard, Treasury, Recipients, Activity Centre |

---

# Epic 10 — Onboarding & Workspace Foundation

## Epic Definition

First-run onboarding, workspace creation, and operational navigation for the hero journey.

## Business Objectives

- Replace generic workflow-builder framing with treasury+payout operations narrative.
- Sub-5-minute demo from landing to first meaningful action.
- Introduce `Workspace` as scoping boundary for all hero-domain data.
- Navigation IA: Dashboard, Treasury, Recipients, Workflows, Activity Centre, Settings.

## User Value

Finance Ops Manager gets guided setup; demo operators get repeatable investor narrative.

## Dependencies

E4 app shell, E8 demo reliability, Product Vision v2, UX User Journey Spec.

## Technical Dependencies

`Workspace` model + API; onboarding state machine; extend `APP_ROUTES`; update demo docs.

## Suggested Story Breakdown

| Story | Title |
|-------|-------|
| 10.1 | Hero landing & positioning refresh |
| 10.2 | Workspace domain model & API |
| 10.3 | Onboarding wizard — create workspace |
| 10.4 | Operational navigation IA |
| 10.5 | Onboarding progress & empty states |
| 10.6 | Demo script & docs alignment |

---

# Epic 11 — Treasury Management

## Epic Definition

Treasury wallet lifecycle: create, balance, funding instructions, transaction history.

## Business Objectives

Hero steps 2–3; infrastructure hidden; mock-first with live Privy path later.

## User Value

Treasury Manager sees balance and funding path; Finance Ops knows treasury is funded before payouts.

## Dependencies

**E10** workspace.

## Technical Dependencies

`Treasury`, `Wallet`, `Transfer` models; Privy adapter extensions; treasury API; Treasury UI; dashboard widget.

## Suggested Story Breakdown

| Story | Title |
|-------|-------|
| 11.1 | Treasury & wallet domain models |
| 11.2 | Privy adapter — treasury wallet create |
| 11.3 | Treasury create API & service |
| 11.4 | Treasury balance read |
| 11.5 | Funding instructions UI |
| 11.6 | Transaction history |
| 11.7 | Treasury screen (UI) |
| 11.8 | Insufficient balance error state |

---

# Epic 12 — Recipient Management

## Epic Definition

CRUD contractor payout recipients (name, wallet address, network, notes).

## Business Objectives

Hero step 4; decouple recipients from one-off form fields.

## User Value

Finance Ops maintains contractor directory; reusable in workflows and AI.

## Dependencies

**E10** workspace.

## Technical Dependencies

`Recipient` model; validation via domain catalog; CRUD API; Recipients UI; picker component.

## Suggested Story Breakdown

| Story | Title |
|-------|-------|
| 12.1 | Recipient domain model & validation |
| 12.2 | Recipient API (CRUD) |
| 12.3 | Recipients list UI |
| 12.4 | Add/edit recipient flows |
| 12.5 | Delete/deactivate recipient |
| 12.6 | Recipient picker component |

---

# Epic 13 — Workflow Management (Hero Contractor Payout)

## Epic Definition

User-configurable contractor payout workflows — configure, schedule, execute via `contractor_payout` template.

## Business Objectives

Hero steps 5–6; recurring payout config; enable/disable; primary demo workflow.

## User Value

“Pay Alice 50 USDC every Friday” as managed operational workflow.

## Dependencies

**E11** treasury, **E12** recipients; workflow engine (existing).

## Technical Dependencies

`WorkflowDefinition` model; `contractor_payout` template (balance check → transfer → complete); CRUD + run API; scheduling MVP; guardrails; bridge `execute_proposal()` to engine.

## Suggested Story Breakdown

| Story | Title |
|-------|-------|
| 13.1 | WorkflowDefinition domain model |
| 13.2 | Hero contractor_payout template |
| 13.3 | Payout workflow CRUD API |
| 13.4 | Manual workflow execution |
| 13.5 | Schedule configuration |
| 13.6 | Enable/disable workflow |
| 13.7 | Workflows management UI |
| 13.8 | Pre-execution guardrails |
| 13.9 | Hero demo migration |

---

# Epic 14 — Activity Centre

## Epic Definition

Unified operational timeline for runs, transfers, errors, and events.

## Business Objectives

Hero step 7; FR7–FR8; replace fragmented run-only view.

## User Value

One feed for payouts, failures, treasury movements.

## Dependencies

**E11** transfers, **E13** runs; existing run inspection API.

## Technical Dependencies

Activity model/projection; ingestion from runs and transfers; filtered API; Activity Centre UI; dashboard widget.

## Suggested Story Breakdown

| Story | Title |
|-------|-------|
| 14.1 | Activity event taxonomy & model |
| 14.2 | Ingest workflow run events |
| 14.3 | Ingest transfer events |
| 14.4 | Activity API with filters |
| 14.5 | Activity Centre UI |
| 14.6 | Activity detail & cross-links |
| 14.7 | Dashboard recent-activity widget |

---

# Epic 15 — Monitoring & Alerts

## Epic Definition

Failure visibility, alerts, exception resolution (FR9).

## Business Objectives

Monitoring native; failures on Dashboard and Activity Centre.

## User Value

Proactive awareness; actionable failure reasons.

## Dependencies

**E13** failures, **E14** activity; E8 error hardening.

## Technical Dependencies

`Alert` model; generation on workflow/transfer failure; alerts API; dashboard widget; error UX patterns.

## Suggested Story Breakdown

| Story | Title |
|-------|-------|
| 15.1 | Alert domain model |
| 15.2 | Alerts on workflow failure |
| 15.3 | Alerts on transfer failure |
| 15.4 | Alerts API |
| 15.5 | Dashboard alerts widget |
| 15.6 | Error state UX patterns |
| 15.7 | Exception resolution flow |

---

# Epic 16 — AI Workflow Assistant (Hero Payout Templates)

## Epic Definition

NL → editable hero payout draft; confirm before save (FR10).

## Business Objectives

AI accelerates config; maps to E12/E13; `AI_MOCK_MODE` independent of adapters.

## User Value

“Pay Alice 50 USDC every Friday” → editable draft → save as workflow.

## Dependencies

**E12**, **E13**; E5 assistant, E9 AI decoupling.

## Technical Dependencies

Payout NL schema; mock deterministic prompts; recipient resolution; review UI; save via E13; no auto-run.

## Suggested Story Breakdown

| Story | Title |
|-------|-------|
| 16.1 | Hero payout NL schema & prompt |
| 16.2 | Mock AI payout draft generator |
| 16.3 | Recipient name resolution |
| 16.4 | AI draft review UI |
| 16.5 | Save AI draft as WorkflowDefinition |
| 16.6 | AI Assistant hero context & examples |
| 16.7 | Live OpenAI path & error handling |

---

## FR Coverage

| FR | Epic |
|----|------|
| FR1 Create workspace | E10 |
| FR2 Create treasury wallet | E11 |
| FR3 Display balance | E11 |
| FR4 Manage recipients | E12 |
| FR5 Create payout workflow | E13 |
| FR6 Execute workflow | E13 |
| FR7 Monitor execution | E14, E15 |
| FR8 Activity history | E14 |
| FR9 Failure notifications | E15 |
| FR10 AI workflow generation | E16 |

---

## 4-Week Delivery Sequence

| Week | Epics |
|------|-------|
| 1 | E10 |
| 2 | E11, E12 |
| 3 | E13 |
| 4 | E14, E15, E16 |

---

## Success Metrics

- Hero journey completable in <5 minutes (mock mode).
- Failure states visible and actionable.
- AI generates editable payout draft; user confirms before save.
- Narrative reflects financial operations, not infrastructure.
