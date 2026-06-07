---
sprint: 1
status: ready-for-implementation
generated: 2026-05-01
sprintGoal: Transform onboarding and navigation from a generic workflow application into a financial operations platform
architectureContext: _bmad-output/project-context.md
epicPrimary: E10
---

# Sprint 1 — Implementation Stories

## Sprint goal

Transform onboarding and navigation from a generic workflow application into a **financial operations platform**.

## Scope

| In scope | Out of scope (Sprint 2+) |
|----------|----------------------------|
| Landing page repositioning | Treasury API / Privy wallet create |
| Workspace creation (API + wizard) | Recipient CRUD API |
| Operational navigation | Payout workflow execution |
| Dashboard / Treasury / Recipients **shells** | Activity data ingestion |
| Shared empty states + setup checklist | AI payout schema changes |

---

## Architecture compliance (mandatory)

All Sprint 1 work **must** follow `_bmad-output/project-context.md`:

| Rule | Sprint 1 application |
|------|------------------------|
| **Modular monolith** | Workspace API: `api/` → `services/` → `db/` only. No adapter or engine imports in API. |
| **Provider abstraction** | No Privy/Banxa/Coinbase calls in Sprint 1. Treasury/Recipient shells are UI-only; no provider names in user-facing empty states. |
| **Workflow engine reuse** | Do **not** modify `engine/runner.py`, `graph_runner.py`, or template registry in Sprint 1. Legacy `#templates` routes remain reachable via Settings → Advanced. |
| **MOCK_MODE support** | Workspace creation is DB-only — zero network. Demo remains safe with `MOCK_MODE=true`. Do not require live keys for Sprint 1 demo path. |
| **No breaking changes** | Preserve existing route IDs (`templates`, `runs`, `assistant`, `builder`, `home`) as aliases or Settings links. Existing `/workflows/*` and `/ai/*` APIs unchanged. |
| **Extend, don't replace** | Extend `Components.jsx`, `index.html` `APP_ROUTES`, `Home.jsx`. New `.jsx` shells — do not rewrite `WorkflowRunner.jsx` or remove legacy UI. |

### Non-breaking route migration

| Legacy route ID | Sprint 1 behaviour |
|-----------------|-------------------|
| `home` | Marketing/onboarding entry; not default post-workspace |
| `templates` | Reachable via Settings → Advanced; label unchanged internally |
| `runs` | Alias redirect to `activity` shell OR kept in Advanced |
| `assistant` | Reachable via Settings → Advanced |
| `builder` | Settings → Advanced (mock) |
| **New** `dashboard` | Default post-onboarding |
| **New** `treasury`, `recipients`, `activity`, `settings` | Primary ops nav |

---

## S1-01 · Workspace domain model & API

**Maps to:** E10.2 · **Complexity:** M

### User story

As a **Finance Operations Manager**,  
I want **my operational data scoped to a workspace I create**,  
So that **Kinetic feels like my company's financial operations environment**.

### Acceptance criteria

- [ ] `POST /workspaces` persists workspace with `id`, `name`, `created_at`
- [ ] `GET /workspaces/current` returns active workspace (MVP: single workspace or most recent)
- [ ] Invalid input returns structured error envelope (`code`, `message`)
- [ ] OpenAPI documents workspace routes
- [ ] No external provider or LLM calls on workspace endpoints
- [ ] `test_api_layer_no_adapter_imports` still passes for new API module

### Technical notes

- `Workspace` model in `backend/app/db/models.py`; import in `main.py` before `create_all()`
- `backend/app/api/workspaces.py` → `backend/app/services/workspace_service.py`
- UTC timestamps via `datetime.now(timezone.utc)`
- `from __future__ import annotations` on new modules
- Client stores `workspace_id` in `localStorage` (auth deferred)

### Architecture guardrails

- **No adapters, no engine, no AI** in workspace path
- **MOCK_MODE irrelevant** — DB-only; must work identically in mock and live env
- Add `test_workspaces_api.py`; extend Postman collection when docs updated (S1-08)

---

## S1-02 · Hero landing page repositioning

**Maps to:** E10.1 · **UX:** UX-14, UX-15 · **Complexity:** S

### User story

As a **first-time visitor**,  
I want **the landing page to explain Kinetic as a financial operations platform**,  
So that **I understand this is not a generic workflow builder**.

### Acceptance criteria

- [ ] Hero copy: Programmable Financial Operations + Stablecoin Treasury & Contractor Payout Operations
- [ ] Primary CTA: **Get started** → onboarding (S1-03)
- [ ] Secondary CTA when workspace exists: **Go to Dashboard**
- [ ] Walkthrough references Dashboard, Treasury, Recipients, Workflows, Activity Centre
- [ ] Existing Home visual design tokens preserved (`KColors`, layout patterns)
- [ ] No regression to `/workflows/*` or other backend APIs

### Technical notes

- **Extend** `ui_kits/app/Home.jsx` — do not replace with new framework
- Wire `onNavigate` to onboarding route and `#dashboard`
- Demote template/builder CTAs from hero; do not remove files

### Architecture guardrails

- UI-only change; no backend or engine touch
- Preserve absolute script paths `/ui-kit/*.jsx`

---

## S1-03 · First-time onboarding wizard

**Maps to:** E10.3 · **UX:** UX-02 · **Complexity:** M · **Depends on:** S1-01

### User story

As a **Finance Operations Manager**,  
I want **a guided flow to create my workspace and see next steps**,  
So that **I can start operating in under five minutes**.

### Acceptance criteria

- [ ] No workspace → routed to onboarding (not `#templates` default)
- [ ] Wizard: Welcome → Who it's for → Create workspace → Preview → Complete
- [ ] Success calls `POST /workspaces`; lands on `#dashboard` with setup checklist
- [ ] Existing workspace → skip wizard → `#dashboard`
- [ ] API errors show plain-language message + retry (no raw stack traces)
- [ ] Keyboard-navigable steps

### Technical notes

- New `ui_kits/app/Onboarding.jsx`; register in `index.html`
- Bootstrap logic in `App`: check `localStorage` `kinetic_workspace`
- Reuse `KButton`, `KInput` from `Components.jsx`

### Architecture guardrails

- Onboarding calls **workspace API only** — not `/ai/interpret` or `/workflows/run`
- Do not change default engine behaviour

---

## S1-04 · Operational navigation redesign

**Maps to:** E10.4 · **UX:** UX-01 · **Complexity:** M · **Depends on:** S1-05–07

### User story

As a **Finance Operations Manager**,  
I want **navigation matching operational surfaces**,  
So that **I don't translate builder terminology into daily work**.

### Acceptance criteria

- [ ] Primary nav: Dashboard, Treasury, Recipients, Workflows, Activity Centre, Settings
- [ ] No primary nav labels: Operations, runner, template browser, Workflow Builder (mock)
- [ ] All primary destinations load within ≤2 clicks from Dashboard
- [ ] Settings includes workspace name + **Advanced (demo)** links to legacy `templates`, `assistant`, `builder`
- [ ] Legacy hash routes still resolve (non-breaking)
- [ ] Update `test_ui_shell_navigation_smoke.py`

### Technical notes

- **Extend** `APP_ROUTES` and `KSidebar` in `index.html` / `Components.jsx`
- Add route aliases: e.g. `runs` → `activity` redirect in `readRoute()`
- Default route post-onboarding: `dashboard` (change `readRoute()` fallback from `home` only when workspace exists)

### Architecture guardrails

- **Do not delete** legacy route handlers or component script includes
- Workflows shell in Sprint 1 can be thin placeholder — **do not remove** `WorkflowRunner.jsx` from bundle

---

## S1-05 · Dashboard shell

**Maps to:** E10.5 · **UX:** UX-05 (shell) · **Complexity:** M · **Depends on:** S1-03, S1-08

### User story

As a **Finance Operations Manager**,  
I want **an operational Dashboard home**,  
So that **I see where treasury, workflows, and activity will appear**.

### Acceptance criteria

- [ ] Widget placeholders: Treasury summary, Active workflows, Recent activity, Alerts, Upcoming payouts
- [ ] Each widget shows empty/placeholder state — not errors or blank panels
- [ ] Setup checklist visible until hero steps complete (client-side flags OK)
- [ ] Header shows workspace name from localStorage/API
- [ ] Quick actions navigate to Treasury, Recipients, Workflows, Activity shells

### Technical notes

- New `ui_kits/app/Dashboard.jsx`; patterns from `Home.jsx` stat cards
- No new backend endpoints in Sprint 1
- Widget slots designed for Sprint 2 API wiring without layout rework

### Architecture guardrails

- Dashboard **must not** call Privy/adapters for balance in Sprint 1
- Optional: read workspace via `GET /workspaces/current` only

---

## S1-06 · Treasury shell

**Maps to:** E11 (UI shell) · **UX:** UX-06 · **Complexity:** S · **Depends on:** S1-04, S1-08

### User story

As a **Treasury Manager**,  
I want **a dedicated Treasury screen layout**,  
So that **I know where wallet, balance, funding, and history will live**.

### Acceptance criteria

- [ ] Sections: balance summary, wallet card, funding instructions, transaction history table
- [ ] Empty state: "No treasury wallet yet" + CTA (stub OK: "Available next sprint")
- [ ] Header: "Treasury" + workspace context
- [ ] No provider names (Privy) in UI copy
- [ ] Layout matches E11.7 structure for Sprint 2 fill-in

### Technical notes

- New `ui_kits/app/Treasury.jsx`
- Use `KEmptyState` from S1-08
- **No** treasury API calls in Sprint 1

### Architecture guardrails

- **Provider abstraction:** UI shows "Connected wallet" not "Privy wallet"
- Do not add Privy adapter methods in this story

---

## S1-07 · Recipients shell

**Maps to:** E12 (UI shell) · **UX:** UX-07 · **Complexity:** S · **Depends on:** S1-04, S1-08

### User story

As a **Finance Operations Manager**,  
I want **a Recipients screen layout**,  
So that **I have a clear place to manage contractor payout destinations**.

### Acceptance criteria

- [ ] List region with columns: Name, Network, Wallet address, Status
- [ ] Empty state: "No contractors added" + **Add recipient** CTA
- [ ] Add action opens stub modal/form (no `POST` in Sprint 1)
- [ ] Static network options aligned with `domain/catalog.py` display values only
- [ ] Keyboard-accessible empty state and CTA

### Technical notes

- New `ui_kits/app/Recipients.jsx`
- Stub modal with `KInput`, `KSelect` — submit disabled or informational
- **No** recipient API in Sprint 1

### Architecture guardrails

- Validation rules documented for Sprint 2; no duplicate domain logic in UI beyond display

---

## S1-08 · Shared empty states, checklist, ops copy & docs

**Maps to:** E10.5, E10.6 · **UX:** UX-03, UX-15 · **Complexity:** M

### User story

As a **first-time user**,  
I want **consistent empty states and operational language**,  
So that **the product feels cohesive and guides setup without jargon**.

### Acceptance criteria

- [ ] `KEmptyState` in `Components.jsx` used on Dashboard, Treasury, Recipients, Workflows placeholder, Activity placeholder
- [ ] `SetupChecklist` component on Dashboard; progress in `localStorage` keyed by workspace id
- [ ] No "runner", "template catalog", or "open in runner" on primary hero paths
- [ ] Settings shell: workspace name, sandbox indicator, Advanced demo links
- [ ] `docs/demo-mvp-flow.md` updated: Landing → Onboarding → Dashboard → shells
- [ ] Onboarding workspace failure uses plain-language error

### Technical notes

- **Extend** `Components.jsx` — add `KEmptyState`, `SetupChecklist`
- Thin placeholder components or inline shells for Workflows + Activity Centre (empty state only)
- Settings: `ui_kits/app/Settings.jsx` or inline in `index.html`

### Architecture guardrails

- Copy pass **must not** rename API paths or break OpenAPI
- Legacy demo flow documented under Settings → Advanced, not removed

---

## Implementation order

```
S1-01 → S1-08 (KEmptyState/SetupChecklist) → S1-05, S1-06, S1-07 → S1-04 → S1-02 → S1-03 → S1-08 (docs/copy finish)
```

## Sprint 1 exit criteria

- [ ] Landing → Onboarding → Workspace → Dashboard with checklist (<5 min demo)
- [ ] Primary nav loads all ops shells with consistent empty states
- [ ] Legacy workflow/AI/builder paths still reachable via Settings → Advanced
- [ ] All existing backend tests pass; new workspace API tests pass
- [ ] `MOCK_MODE=true` demo path unchanged for `/workflows/*` and `/ai/*`

## Story → epic map

| Sprint story | Engineering epic |
|--------------|------------------|
| S1-01 | E10.2 |
| S1-02 | E10.1 |
| S1-03 | E10.3 |
| S1-04 | E10.4 |
| S1-05 | E10.5 |
| S1-06 | E11 (shell) |
| S1-07 | E12 (shell) |
| S1-08 | E10.5, E10.6 |
