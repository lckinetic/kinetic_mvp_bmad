---
phase: phase-2-hero-workflow
status: approved
generated: 2026-05-01
project_name: kinetic-mvp-bmad
primaryPersona: Finance Operations Manager
designPrinciples:
  - Business first
  - Infrastructure hidden
  - Operational visibility
  - AI-assisted (not AI-first)
epicMap: E10-E16
---

# UX Redesign Backlog — Financial Operations Platform

**Problem:** Product feels like a generic workflow builder.  
**Target:** Programmable Financial Operations Platform — first domain: Stablecoin Treasury & Contractor Payout Operations.

**Maps to:** Phase 2 Epics E10–E16 · See also [epic-plan.md](./epic-plan.md)

---

## Prioritised delivery sequence

| Sprint | UX stories | Rationale |
|--------|------------|-----------|
| **1** | UX-01, UX-02, UX-03, UX-04, UX-14, UX-15 | Shell, language, onboarding, empty/error foundations |
| **2** | UX-05, UX-06, UX-07 | Dashboard + Treasury + Recipients — hero steps 2–4 |
| **3** | UX-08 | Workflow management — hero steps 5–6 |
| **4** | UX-09, UX-10, UX-11 | Activity Centre + monitoring — hero step 7 |
| **5** | UX-12, UX-13, UX-16 | AI payout context, settings, a11y polish |

| Priority | Count | Theme |
|----------|-------|-------|
| P0 | 4 | Navigation, onboarding, empty/error systems |
| P1 | 4 | Dashboard, Treasury, Recipients, Workflows |
| P2 | 3 | Activity Centre, alerts, exception recovery |
| P3 | 5 | AI, Settings, Home reposition, copy, a11y |

**Total:** 16 prioritised UX stories

---

## P0 — Foundation (Navigation, Onboarding, Shell)

### UX-01 · Operational navigation redesign

**Priority:** P0 · **Epic:** E10.4

**Problem:** Sidebar reads like a generic builder (`Home`, `Workflows`, `Operations`, `AI Assistant`, `Workflow Builder (mock)`).

**Target:** Financial ops IA aligned to hero journey.

**Requirements**
- Primary nav: **Dashboard**, **Treasury**, **Recipients**, **Workflows**, **Activity Centre**
- Secondary: **Settings** (workspace + provider connections placeholder)
- Demote/rehome: `Home` → marketing/onboarding entry only
- Demote: `Workflow Builder (mock)` → Settings or “Advanced (demo)”
- Rename: `Operations` → **Activity Centre**
- Page titles/subtitles use ops language, not “templates/runner”
- Preserve hash route IDs where possible; document mapping

**Acceptance criteria**
- [ ] User reaches all 5 hero surfaces in ≤2 clicks from Dashboard
- [ ] No primary nav item says “builder”, “template browser”, or “runner”
- [ ] Active state, keyboard nav, and focus order work across new nav

---

### UX-02 · First-time onboarding flow (workspace creation)

**Priority:** P0 · **Epic:** E10.3, E10.5

**Problem:** No workspace concept; user lands on investor Home with no guided ops setup.

**Target:** ≤5 min path: understand product → create workspace → see setup checklist.

**Flow**
1. **Welcome** — Programmable Financial Operations + hero domain one-liner
2. **Who it’s for** — Finance / treasury / ops teams
3. **Create workspace** — name + optional org label
4. **What happens next** — Treasury → Recipients → Payout workflow preview
5. **Setup checklist** — ☐ Treasury ☐ Recipient ☐ Workflow ☐ First run
6. **Land on Dashboard** — checklist visible; empty states link forward
7. **Skip/resume** — returning user skips if workspace exists

**Acceptance criteria**
- [ ] First-time user completes workspace creation without seeing template catalog first
- [ ] Checklist progress updates as hero steps complete
- [ ] Demo completable in <5 minutes with checklist as guide

---

### UX-03 · Global empty-state system

**Priority:** P0 · **Epic:** E10.5 (cross-cutting)

**Problem:** Empty screens feel broken or developer-oriented.

**Target:** Every primary surface explains **what**, **why**, and **next action**.

**Requirements**
- Shared component: icon, headline, explanation, primary CTA, optional secondary link
- Tone: operational, not technical
- Checklist integration on Dashboard

**Surface-specific empty states**

| Surface | Headline (example) | Primary CTA |
|---------|-------------------|-------------|
| Dashboard (new) | “Set up your treasury to start paying contractors” | Create treasury |
| Treasury | “No treasury wallet yet” | Create treasury wallet |
| Recipients | “No contractors added” | Add recipient |
| Workflows | “No payout workflows configured” | Create payout workflow |
| Activity Centre | “No activity yet” | Run your first workflow |
| Alerts widget | “No issues — you’re all clear” | — |

**Acceptance criteria**
- [ ] All 5 primary surfaces use consistent empty-state pattern
- [ ] Each empty state has one primary CTA toward hero journey
- [ ] Empty states never mention providers by name

---

### UX-04 · Global error-state system

**Priority:** P0 · **Epic:** E11.8, E15.6, E15.7

**Problem:** Failures surface as raw API errors or silent 502s.

**Target:** Actionable operational errors with recovery paths.

**Error catalog**

| Error | User message | Recovery action |
|-------|--------------|-----------------|
| Insufficient balance | “Treasury balance is too low for this payout” | Fund treasury |
| Transfer failed | “Payout could not be completed” | View details → retry |
| Recipient invalid | “Recipient wallet address isn’t valid for this network” | Edit recipient |
| Workflow disabled | “This workflow is paused” | Enable workflow |
| Provider unavailable | “Payment service temporarily unavailable” | Try again; view status |
| AI generation failed | “Couldn’t generate workflow — try rephrasing or create manually” | Edit prompt / manual create |

**Requirements**
- Inline (forms), banner (page-level), toast (transient)
- No stack traces, proxy errors, or API keys
- Failed runs link to Activity Centre detail

**Acceptance criteria**
- [ ] Each error in catalog has designed UI
- [ ] Every blocking error offers ≥1 recovery action
- [ ] Error copy avoids infrastructure/provider jargon

---

## P1 — Core Operations Surfaces

### UX-05 · Dashboard redesign (operational home)

**Priority:** P1 · **Epic:** E10.4, E11, E14.7, E15.5

**Problem:** No operational home; `Home` is investor deck.

**Target:** Dashboard = default landing after onboarding.

**Widgets**
1. Treasury summary — balance (USDC), “Fund treasury” link
2. Active workflows — count, next scheduled payout
3. Recent activity — last 5 events
4. Alerts — unacknowledged failures
5. Upcoming payouts — next 7 days
6. Setup checklist (until complete)

**Quick actions:** Fund treasury · Add recipient · Create workflow · View activity

**Acceptance criteria**
- [ ] Dashboard is default route post-onboarding
- [ ] All widgets render with data or empty/error states
- [ ] User assesses ops health in <10 seconds

---

### UX-06 · Treasury screen requirements

**Priority:** P1 · **Epic:** E11.5–E11.7

**Problem:** Treasury exists only as workflow template category.

**Target:** Single operational stablecoin treasury view.

**Sections**
1. Header — “Treasury” + workspace; balance prominent (USDC)
2. Wallet card — address (copy), network, abstracted provider label
3. Fund treasury — deposit instructions, network warning, demo “Simulate deposit”
4. Transaction history — date, type, amount, counterparty, status, link to activity
5. Actions — Create wallet (first time), refresh balance

**Acceptance criteria**
- [ ] Copy funding address in one action
- [ ] Balance and history on same screen without running a workflow
- [ ] Status pills: pending / completed / failed

---

### UX-07 · Recipient management requirements

**Priority:** P1 · **Epic:** E12.3–E12.6

**Problem:** Recipients are form fields in runner, not a directory.

**Target:** Contractor payout address book.

**List:** Name, network, truncated address, status; search; Add recipient CTA

**Form:** Name, wallet address, network (select), notes; inline validation

**Delete/deactivate:** Warning if linked to active workflow

**Detail drawer (optional):** Full address, linked workflows, recent payouts

**Acceptance criteria**
- [ ] CRUD without workflow runner
- [ ] Recipient picker reads from directory
- [ ] Invalid address blocked with plain-language error

---

### UX-08 · Workflow management redesign (hero payout)

**Priority:** P1 · **Epic:** E13.7, E13.9

**Problem:** Generic template browser + technical runner.

**Target:** Payout workflow manager.

**List:** Name, recipient, amount+asset, schedule, enabled/disabled, last/next run; actions: Run, Edit, Pause, View activity

**Create/edit:** Name, recipient picker, amount+asset, schedule, business-language review (hide step IDs)

**Run:** Business steps — “Checking balance” → “Sending payout” → “Complete”; link to Activity

**Legacy:** Demote `treasury_demo` / `managed_treasury` to “Legacy demos”

**Acceptance criteria**
- [ ] Hero list features contractor payout workflows
- [ ] Recurring payout without provider step IDs
- [ ] Manual run shows business-step labels

---

## P2 — Visibility & Monitoring

### UX-09 · Activity Centre requirements

**Priority:** P2 · **Epic:** E14.5, E14.6

**Problem:** Operations tab is run-id list — feels like debug tooling.

**Target:** Unified operational timeline.

**Layout:** Filter bar (type, date, status); chronological feed; detail drawer with links to workflow/recipient/treasury

**Event types:** Payout success/fail, treasury funded, run started/completed, alert raised/acknowledged

**Acceptance criteria**
- [ ] Answer “what happened yesterday?” in one tab
- [ ] Failed payout traceable in ≤3 clicks
- [ ] Feed updates after manual workflow run

---

### UX-10 · Monitoring & alerts UX

**Priority:** P2 · **Epic:** E15.5

**Requirements:** Dashboard alerts widget; acknowledge action; in-context banner for critical alerts; acknowledged state de-emphasized in widget

**Acceptance criteria**
- [ ] Failed payout surfaces on Dashboard same session
- [ ] Acknowledge clears prominence; history in Activity
- [ ] Alert copy matches UX-04 catalog

---

### UX-11 · Exception resolution flows

**Priority:** P2 · **Epic:** E15.7

| Failure | Resolution path |
|---------|-------------------|
| Insufficient balance | Alert → Treasury → fund → retry |
| Invalid recipient | Alert → Edit recipient → retry |
| Transfer failed | Activity detail → Retry if balance OK |
| Workflow paused | Enable workflow → retry |

**Acceptance criteria**
- [ ] Each failure type has multi-step recovery
- [ ] Recovery CTAs deep-link with context

---

## P3 — AI & Advanced

### UX-12 · AI Assistant redesign (hero payout context)

**Priority:** P3 · **Epic:** E16.4, E16.6

**Requirements:** Hero prompt examples; editable form fields (not raw JSON); Save as workflow / Run once after confirm; link to create recipient if name missing

**Acceptance criteria**
- [ ] Demo prompt understandable without JSON editing
- [ ] Confirm before save or run
- [ ] Payout vocabulary, not graph language

---

### UX-13 · Settings & workspace context

**Priority:** P3 · **Epic:** E10.4

**Sections:** Workspace name; demo/sandbox indicator; provider connection placeholders; Advanced → Builder mock, legacy demos

**Acceptance criteria**
- [ ] Workspace visible from Settings and Dashboard header
- [ ] Builder clearly labeled non-production

---

### UX-14 · Marketing Home repositioning

**Priority:** P3 · **Epic:** E10.1

**Requirements:** Financial ops positioning; CTAs Get started / Go to Dashboard; update four-screens walkthrough

**Acceptance criteria**
- [ ] Onboarded users land on Dashboard
- [ ] Home optional, not in primary ops nav

---

### UX-15 · Business-language copy pass

**Priority:** P3 · **Epic:** E10.1, E13.9

| Current | Target |
|---------|--------|
| Templates | Payout workflows |
| Open in runner | Run workflow |
| Operations | Activity Centre |
| Step: wallet.create | Checking wallet / Preparing payout |

**Acceptance criteria**
- [ ] No “runner”, “template catalog”, or raw step IDs on hero paths
- [ ] Glossary for engineering (internal IDs unchanged)

---

### UX-16 · Accessibility & responsive baseline

**Priority:** P3 · **Epic:** E4.3 carry-forward

**Requirements:** Keyboard nav on hero paths; focus visible; responsive Dashboard/Treasury/Activity; status not color-only

**Acceptance criteria**
- [ ] Hero path completable via keyboard
- [ ] Contrast on error/alert states

---

## UX story → engineering epic map

| UX ID | Engineering epics |
|-------|-------------------|
| UX-01 | E10.4 |
| UX-02 | E10.3, E10.5 |
| UX-03 | E10.5 |
| UX-04 | E11.8, E15.6, E15.7 |
| UX-05 | E10.4, E11, E14.7, E15.5 |
| UX-06 | E11.5–E11.7 |
| UX-07 | E12.3–E12.6 |
| UX-08 | E13.7, E13.9 |
| UX-09 | E14.5, E14.6 |
| UX-10 | E15.5 |
| UX-11 | E15.7 |
| UX-12 | E16.4, E16.6 |
| UX-13 | E10.4 |
| UX-14 | E10.1 |
| UX-15 | E10.1, E13.9 |
| UX-16 | E4.3 |
