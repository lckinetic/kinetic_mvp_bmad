---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
inputDocuments:
  - _bmad-output/project-context.md
  - docs/index.md
  - docs/overview.md
  - docs/architecture.md
  - docs/project-overview.md
  - docs/source-tree-analysis.md
  - docs/onramp.md
  - docs/adr-001-mock-mode.md
  - docs/ai/architecture-principles.md
  - docs/ai/feature-template.md
  - docs/ai/qa-checklist.md
  - docs/features/offramp-mvp.md
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 11
workflowType: prd
classification:
  primaryProjectType: saas_b2b
  secondaryTypes:
    - api_backend
    - web_app
  domain: fintech
  complexity: high
  projectContext: brownfield
  productPillars:
    - Workflow engine and APIs (execution, persistence, integrations)
    - Customer-facing UI platform for authoring workflows (replacing ad hoc HTML/JS with a proper front-end stack, e.g. React)
    - AI assistant (chat-style) as a key path to build or refine workflows via conversation
    - API access to prebuilt workflows (list, instantiate, run) without requiring the UI
  scopeNotes:
    - PDF one-pager under-scoped the AI assistant; it remains a first-class requirement in this PRD.
    - Customers use the web application to build workflows, not only developers via API/Postman.
    - MVP must support leveraging prebuilt workflows entirely via API (headless / integration clients); UI is not required for that path.
    - Kinetic is a pure integration/technology layer; KYC/AML and regulatory obligations are fulfilled by partner connectors and customer relationships—not by Kinetic acting as the KYC/AML or licensed party.
prdStatus: complete
completedAt: '2026-04-12'
---

# Product Requirements Document - kinetic-mvp-bmad

**Author:** Leonachen
**Date:** 2026-04-12

## Executive Summary

Kinetic is an **AI-assisted workflow automation platform** for **fintech and crypto-native** organizations. It lets teams **author**, **run**, and **iterate** on **multi-step financial workflows** that span **multiple providers** (e.g. on/off-ramp, custody, trading) with **persistent execution state**, **adapter-based integrations**, and **audit-friendly** handling of money movement. Kinetic is **integration technology** only: **KYC/AML** and **licensed regulatory acts** are **not** performed by Kinetic itself—workflows may **invoke partner connectors** so **customers** and **partners** satisfy those obligations.

**Target users:** Product and operations teams who need **repeatable, governable automation** across providers—not one-off scripts, ad hoc API calls, or spreadsheets—plus engineers who extend integrations and behaviour.

**Problem:** Composing and operating these workflows is slow and error-prone when every change requires bespoke code or brittle glue. Teams need **fast iteration** with **clear guardrails** (idempotency, canonical statuses, safe demo modes) appropriate to **regulated, high-stakes** flows.

**This phase (brownfield):** Evolve the existing MVP into a **clean modular monolith**: **production-oriented** backend structure, **standardized APIs**, **Dockerized** local environments, and a **real customer-facing web application** so users **build workflows in the UI**. The **chat-style AI assistant** remains a **first-class** way to **author or refine workflows** alongside the UI—not a side experiment. In parallel, the MVP must retain and clarify an **API-only path** so users can **discover, trigger, and run prebuilt workflows** without the UI—supporting **integrations, automation, and headless** clients.

### What Makes This Special

- **Conversational authoring:** Users can **shape workflows through natural-language chat** with the assistant, lowering the barrier between intent and executable workflow.
- **Unified platform:** **Same product** combines a **workflow engine**, **provider adapters**, and **in-product authoring**—moving beyond **Postman-as-UI** and **minimal HTML/JS** toward a **maintainable front-end** (e.g. **React**) suitable for a **workflow builder** experience.
- **API parity for prebuilt workflows:** **Prebuilt** (template) workflows remain **fully usable via HTTP API**—list available definitions, start runs, poll status—**without requiring the visual UI**, so programmatic and integration-first users are first-class.
- **Engineering discipline for fintech:** **MOCK_MODE**, **DB-level idempotency**, **normalized internal statuses**, and **audit-first webhook handling** align the product with **crypto/fintech** expectations for **safety and traceability**.

**Core insight:** Value is not a single integration—it is **composable, operable automation** across providers with **human-friendly authoring** (UI + chat) on a **strict backend contract**.

## Project Classification

| Dimension | Classification |
|-----------|----------------|
| **Primary type** | **SaaS B2B platform** (teams build and run workflows in-product) |
| **Secondary** | **API / backend** (FastAPI, persistence, integrations); **Web app** (customer UI for workflow authoring) |
| **Domain** | **Fintech** (payments-adjacent, crypto-native workflows) |
| **Complexity** | **High** (compliance, security, and operational rigor—even for MVP-grade shipping) |
| **Context** | **Brownfield** (existing MVP codebase, docs, and engine; extend and refactor toward platform + production foundation) |

### Traceability

**Vision → success criteria → journeys → requirements:** Executive Summary and classification anchor **Success Criteria** and **Product Scope**; **User Journeys** drive **Functional Requirements**; **Non-Functional Requirements** constrain how well those capabilities perform. **Domain**, **Innovation**, **SaaS B2B**, and **Project Scoping** sections add constraints and phasing without replacing the FR capability contract.

## Success Criteria

### User Success

- **Authoring:** A user can **create or materially refine** a workflow using **either** the **web UI** or the **chat assistant** (or both), without touching raw API tools for core authoring flows.
- **API-only (prebuilt workflows):** A user or integration can **discover available prebuilt (template) workflows**, **start runs**, and **track execution to completion** using **only the HTTP API**—no UI required. This path must remain **documented**, **stable**, and **demoable** in **MOCK_MODE** (or equivalent) for the MVP.
- **Clarity:** Users can **see execution state** (running / failed / completed) and **understand what ran** (steps, key outputs) for a workflow run—sufficient for demos and internal pilot customers.
- **Trust (MVP-appropriate):** Idempotent behaviour and **canonical statuses** are observable in product behaviour (no “mystery” duplicate orders or stuck states in normal operation).
- **Time-to-value:** A new internal user can complete a **first meaningful workflow** (author + run in **MOCK_MODE** or equivalent safe path) within **one working session** once the environment is up.

### Business Success

- **Foundation:** By end of this phase, the codebase is **credible for continued investment**—modular monolith, documented run path, **Dockerized** local stack, **stable API** surface for UI, integrations, and **headless** clients.
- **Adoption signal (pilot):** At least **one repeatable demo or pilot narrative** (“customer builds workflow in UI + assistant” **and/or** “integration drives prebuilt workflows via API only”) that stakeholders can run **without developer babysitting**.
- **Velocity:** Refactors **do not block** shipping incremental workflow/UI features; regressions are **caught** by basic automated checks where agreed (target: expand from current minimal tests).

### Technical Success

- **Structure:** Clear separation—**API**, **services**, **adapters**, **DB**, **engine**—with **API standardization** (errors, versioning posture, consistency) as defined in implementation.
- **API surface:** Public (or product) **workflow APIs** support **prebuilt template discovery and execution** independently of the SPA; contract documented (e.g. OpenAPI) and kept in sync with behaviour.
- **Local dev:** **Docker-based** (or equivalent) **reproducible** environment; new engineer can run the stack from documented steps.
- **Safety defaults:** **MOCK_MODE** remains **demo-safe**; secrets and sensitive config are **not leaked** in logs; webhook **audit trail** behaviour preserved or improved—not regressed.
- **Observability:** Minimum viable **logging/metrics hooks** for workflow execution suitable for debugging engine and integration issues.

### Measurable Outcomes

| Horizon | Outcome |
|---------|---------|
| **End of phase (this engagement)** | **Clean backend**, **Dockerized app**, **stable API**, **documentation** updated; **UI path** exists for workflow authoring (not Postman-only); **API-only path** for **prebuilt workflows** is explicit and shippable. |
| **3-month window (per plan)** | Phased delivery: **refactor** → **engine + API** → **Docker + polish**; each phase has **reviewable milestones**. |
| **Quality bar** | No known **P0** gaps for **idempotency**, **status normalization**, or **MOCK safety** introduced by new UI/assistant work; **API-only** workflow flows do not regress. |

## Product Scope

### MVP — Minimum Viable Product (this phase)

- **Backend:** Refactor and **structure cleanup**; **workflow engine** improvements; **API standardisation**; preserve or strengthen **adapter** boundaries (mocked integrations acceptable).
- **Platform UI:** **Customer-usable** path to **build workflows** in the **web app**; migrate off **HTML + vanilla JS** toward a **maintainable** stack (**React preferred**).
- **AI assistant:** **Chat-style** flow remains **first-class** for **authoring/refining** workflows (exact LLM depth may stay constrained—see out of scope).
- **API (prebuilt workflows):** MVP **must** support **using prebuilt (template) workflows entirely via API**—e.g. list templates, create/run instances, retrieve status and outputs—so **integrations and headless automation** do not depend on the UI.
- **Operations:** **Docker** + **local deployment** story; **documentation** for setup, architecture, and key flows (including **API-only** workflow usage).

### Growth features (post-MVP)

- **Deeper UI:** Rich **workflow builder** (visual graph, templates marketplace, collaboration).
- **Real integrations:** Live provider traffic beyond mocks where commercially and legally ready.
- **Production hardening:** Auth/RBAC, full cloud deployment, SRE-grade monitoring.

### Vision (future)

- **Scalable multi-tenant** platform with **strong compliance** and **enterprise** workflows across many providers.

### Explicitly out of scope (this phase)

- **Full cloud deployment** to production.
- **Full production-grade authentication / RBAC** (may stub or defer per architecture).
- **“Advanced AI”** beyond assistant flows needed for **workflow authoring** (no open-ended research agents required for MVP).
- **Real** end-to-end provider integrations if not required for the agreed pilot (mocks remain valid).

## User Journeys

### User types

| Type | Role |
|------|------|
| **Maya** | Product / ops — builds and runs workflows in the **web app** |
| **Alex** | Power user — **chat assistant** to draft or refine a workflow |
| **Raj** | Integration engineer — **API-only** use of **prebuilt** workflows (no UI) |
| **Jordan** | Internal ops / engineer — **monitors runs**, reads logs, safe **MOCK** demos |
| **Sam** | Support / debugging — **investigates** a failed run (status, steps, webhook trail) |

### Journey 1 — Maya (primary): first workflow in the UI (happy path)

**Opening:** Maya needs a repeatable on-ramp demo for investors. She is tired of one-off Postman calls and spreadsheets.

**Rising action:** She opens the app, picks a **prebuilt template** (or starts from an empty flow), configures steps with clear labels, saves, and starts a run in **MOCK_MODE**. She watches **status** move to completed and sees **step-level** output.

**Climax:** She runs the same flow twice without duplicate chaos—**idempotency** and **canonical statuses** behave as expected.

**Resolution:** She can **demo the story** without a developer in the room. Emotional arc: **relief** → **confidence**.

**Failure / recovery:** Run fails mid-flight; she sees **failed** with a **reason** and can **retry** or fix inputs without corrupting history.

### Journey 2 — Alex (primary): assistant-led authoring

**Opening:** Alex knows the business outcome (“when fiat lands, notify treasury”) but not the exact graph of steps.

**Rising action:** In **chat**, they describe intent; the assistant proposes a **structured workflow** (or edits an existing one). They **confirm** before execution.

**Climax:** The assistant’s proposal **maps to real engine steps**—not fantasy nodes—and can be **opened or adjusted** in the UI later.

**Resolution:** Alex ships faster without reading every adapter detail first. Arc: **uncertainty** → **clarity**.

**Failure / recovery:** Assistant suggests something unsafe or invalid; **validation** blocks or warns; Alex corrects in chat or switches to UI.

### Journey 3 — Raj (API / integration): prebuilts only via API

**Opening:** Raj’s service must **trigger a prebuilt workflow** from a backend job—**no browser**, **no SSO to your SPA** in MVP.

**Rising action:** Using **documented API** (e.g. OpenAPI), they **list templates**, **start a run** with inputs, **poll status**, and read **outputs**. All in **MOCK_MODE** for staging.

**Climax:** Same behaviours Maya gets in UI—**status**, **completion**, **errors**—are available **purely over HTTP**.

**Resolution:** Integration is **testable in CI** and **demoable** to their team. Arc: **skepticism** → **trust in the contract**.

**Failure / recovery:** **4xx/5xx** with **actionable error body**; idempotent **retry** does not double-charge logical work.

### Journey 4 — Jordan (ops): observe and demo safely

**Opening:** Jordan runs internal **demos** and must never leak secrets or hit real providers by mistake.

**Rising action:** They confirm **MOCK_MODE**, scan **logs** (no raw keys), and compare **WorkflowRun** records to expectations.

**Climax:** A run **fails**; they can **trace** engine + adapter boundaries without raw provider noise in client-facing errors.

**Resolution:** Demos are **predictable**. Arc: **anxiety** → **control**.

### Journey 5 — Sam (support): debug a stuck or failed run

**Opening:** A stakeholder says “it’s stuck.” Sam has minutes to explain what happened.

**Rising action:** Sam finds the **run**, **status history**, **step outputs**, and **webhook / event** trail where applicable. They determine **user error vs system defect**.

**Climax:** Enough **audit** to answer “what did we receive?” without deleting history.

**Resolution:** Clear **next step** for Maya or engineering. Arc: **confusion** → **accountability**.

### Journey requirements summary

| Capability area | Driven by |
|-----------------|-----------|
| **Web app** — templates, configure, save, run, history | Maya, Alex (handoff to UI) |
| **Chat assistant** — NL → workflow proposal, confirm, validate | Alex |
| **Workflow HTTP API** — list prebuilts, start run, status, outputs | Raj |
| **Execution model** — states, steps, idempotency, MOCK | All |
| **Observability & audit** — logs, run records, webhook storage | Jordan, Sam |
| **Errors & recovery** — clear failures, retry semantics | Maya, Raj, Sam |

## Domain-Specific Requirements

Kinetic is a **pure technology and integration** product: it **orchestrates workflows** and **connects customers** to **partner systems** (on/off-ramp, custody, identity, etc.). It does **not** position itself as the regulated entity that performs **KYC**, **AML**, or broader **compliance programs** on behalf of end users.

### Regulatory and identity posture

- **KYC / AML:** Kinetic **does not** run its own KYC or AML programs. Where a workflow includes identity or compliance steps, those are implemented as **connector integrations** to **partner** services; **obligations and decisions** sit with the **partner** and **Kinetic’s customer** (the deployer), not with Kinetic as a substitute regulated party.
- **Regulation:** The same principle applies to **jurisdiction-specific** or **license-dependent** requirements: Kinetic provides **plumbing** (routing, state, audit hooks, adapter boundaries). **Interpretation**, **licensing**, and **end-customer obligations** remain **outside** Kinetic’s scope except as **documented assumptions** about what connectors are invoked.
- **Product copy and contracts:** Customer-facing materials and agreements should **not** imply Kinetic is performing regulated activities; **integration platform** language is accurate.

### Compliance & regulatory (MVP-appropriate, tech layer)

- **Proportionality:** This phase does **not** target full production attestation (e.g. SOC 2, full PCI); requirements below are **design and documentation** hooks so later hardening is tractable.
- **Data in transit and at rest:** Treat **PII**, **financial references**, and **integration payloads** as **sensitive**; **secrets** never in logs or client-visible errors; define **retention** posture in architecture (even if enforcement is partial in MVP).
- **Audit & traceability:** **Store-then-process** for webhooks; support investigation journeys (runs, steps, payloads) **without** silent deletion—consistent with **integration** accountability, not with Kinetic acting as **money transmitter** or **identity verifier**.

### Technical constraints

- **Connector boundaries:** Adapters encapsulate **partner-specific** behaviour; **normalize** external statuses to **internal canonical** values on **Kinetic-owned** entities; unknown provider strings are **not** persisted on core domain tables (per architecture principles).
- **MOCK_MODE:** Remains **first-class** for demos and CI; deterministic behaviour for API-only and UI paths.

### Risk mitigations

| Risk | Mitigation (MVP) |
|------|------------------|
| Implied regulated role | Clear **positioning**: integration tech + connectors; **no** in-product KYC/AML **execution** by Kinetic |
| Partner / customer confusion | **Document** which **connector** owns which step; **errors** reference **partner** context where useful |
| Data handling | **Minimize** sensitive fields; **document** what flows through **WorkflowRun** / **webhooks** for audit |

## Innovation & Novel Patterns

### Detected innovation areas

- **Workflow automation + conversational authoring:** Pairing a **graph/template execution engine** with a **chat-style assistant** so users can move from **natural language** to **executable workflow structure** is the primary novelty—not generic “AI chat,” but **grounded proposals** that map to **real engine steps** and **adapter** boundaries.
- **Triple delivery mode:** **Web UI**, **HTTP API (prebuilt workflows)**, and **assistant** as **peer** ways to author and run—reduces lock-in to a single interaction pattern for fintech teams.
- **Integration-first fintech:** **MOCK_MODE**, **canonical statuses**, **idempotent** persistence, and **audit-first** webhooks as **first-class** product features—not afterthoughts—suited to **money-adjacent** workflows.
- **Pure tech / connector posture:** Innovation is in **orchestration and UX of composition**, not in Kinetic becoming the **KYC/AML** or **licensed** party—**partner connectors** carry regulated acts.

### Market context & competitive landscape

- **iPaaS / automation** tools and **banking APIs** exist; fewer combine **crypto-native ramp/custody patterns**, **open adapter** model, and **assistant-led** workflow authoring in one **brownfield** codebase aimed at **fast iteration** with **demo-safe** defaults.
- **Differentiation** will hinge on **execution quality** (reliability, observability, API clarity) and **authoring speed** (UI + chat + templates), not on claiming net-new financial licenses.

### Validation approach

- **Assistant:** Measure **time-to-first-valid-workflow**, **validation failure rate**, and **user correction loops** (chat ↔ UI); **shadow** proposals against engine **schema** before run.
- **Engine + API:** **Contract tests** and **MOCK** scenarios for **Raj** journey; **CI** runs for **idempotency** and **status** transitions.
- **Pilots:** One **UI-led** and one **API-only** narrative demonstrable without **developer babysitting** (per success criteria).

### Risk mitigation

| Risk | Mitigation |
|------|------------|
| Assistant **hallucinates** invalid graphs | **Strict validation** against engine/registry; **confirm** step before execute; **fallback** to manual UI edit |
| **Overpromising** “AI” | Scope **advanced LLM** explicitly out of MVP except **authoring assistance** |
| **Commodity** workflow engine | Double down on **fintech-specific** adapters, **audit**, and **dual API/UI** parity |

## SaaS B2B Platform Specific Requirements

### Project-type overview

Kinetic is positioned as a **B2B workflow platform**: **customer organizations** (or internal teams) **author** and **run** automations across **provider connectors**. Delivery surfaces are **web UI**, **chat assistant**, and **HTTP API** (prebuilt workflows).

### Tenant model

- **MVP:** Target **single-organization** or **single-deployment** usage: one **logical customer** per environment unless/until multi-tenant data isolation is explicitly prioritized. **Future:** Document **tenant_id**-style isolation for **data** and **credentials** when moving to **hosted multi-tenant** SaaS.

### Permission model (RBAC)

- **MVP:** **Full production RBAC** is **out of scope** (per product scope). Use **minimal** protection (e.g. **dev-only** keys, **network** boundaries, **feature flags**) and **design hooks** so **roles** (e.g. author, operator, viewer, integration) can attach later without rewiring the **workflow** or **run** model.

### Subscription tiers

- **MVP:** **Not** productized—no **billing** or **tier-gated** features in this phase. **Post-MVP:** **Tiers** may bundle **run volume**, **connector** packs, or **SLA**—TBD.

### Integration list

- **Required:** **Provider adapters** (Banxa, Privy, Coinbase, etc.) behind **stable interfaces**; **workflow HTTP API** for **list/run/status** of **prebuilt** templates; **webhooks** ingestion where applicable. **MOCK_MODE** for all **external** calls in demo/CI.
- **KYC/AML:** **Only** via **partner connectors**—Kinetic does **not** perform regulated identity programs itself (see Domain-Specific Requirements).

### Compliance requirements

- **Product:** **Integration tech** posture—**audit** trails, **no secret** leakage, **data minimization** in **runs** and **logs**. **Legal/compliance** programs for **end users** sit with **customers** and **partners**, not Kinetic as substitute regulated entity.

### Technical architecture considerations

- **API:** **OpenAPI**-documented **workflow** and **run** surfaces; **consistent errors** and **versioning** posture for **UI**, **API-only**, and **integrations**.
- **Separation:** **API** → **services** → **adapters** → **DB**; **assistant** outputs must **validate** against **engine** capabilities.

### Implementation considerations

- **Skip** **CLI-first** and **mobile-first** UX unless priorities change; **web** + **API** are primary.

## Project Scoping & Phased Development

### MVP strategy & philosophy

- **Approach:** **Platform MVP**—prove a **credible workflow stack** (author + run + observe) with **three entry points** (UI, assistant, API for prebuilts), **integration-tech** posture, and **demo-safe** defaults—not full enterprise SaaS billing or production cloud in this phase.
- **Resource profile:** Small **full-stack** team: strong **Python/FastAPI**, **workflow engine**, **front-end** (React direction), **DevOps/Docker** for local; **LLM** integration scoped to **authoring assistance** only.

### MVP feature set (Phase 1 — this engagement)

**Core user journeys supported (minimum):**

- **Maya:** Author/run in **UI** with **prebuilts** and **MOCK_MODE**.
- **Alex:** **Chat** proposes/refines workflows with **validation** before run.
- **Raj:** **API-only** list/run/status for **prebuilt** workflows.
- **Jordan / Sam:** **Observe**, **demo**, **debug** with **audit-friendly** runs and webhooks.

**Must-have capabilities:**

- **Modular monolith** cleanup; **workflow engine** improvements; **API standardisation**; **Dockerised** local stack; **documentation**.
- **Web app** path for **workflow authoring** (replacing ad hoc HTML/JS with a **maintainable** stack).
- **Assistant** path for **authoring/refinement** (bounded LLM scope).
- **Prebuilt workflows fully usable via API** (no UI dependency).
- **Connector** model preserved; **KYC/reg** via **partners only** (see domain section).

### Post-MVP features

**Phase 2 (growth)**

- **Richer builder** (visual graph, templates marketplace, collaboration).
- **Real provider** traffic where agreed; **auth/RBAC** hardening.
- **Subscription / tiers** if productized.

**Phase 3 (expansion)**

- **Hosted multi-tenant** SaaS, **enterprise** compliance artefacts, **scale** and **SRE**-grade ops.

### Phased timeline (aligned with engagement plan)

| Phase | Focus | Weeks (indicative) |
|-------|--------|---------------------|
| **A** | **Refactor** structure, foundations | ~1–4 |
| **B** | **Engine + API** improvements, **standardisation** | ~5–8 |
| **C** | **Docker**, polish, **docs**, **stabilisation** | ~9–12 |
| **D** | TBD after first three phases | — |

### Risk mitigation strategy

| Category | Mitigation |
|----------|------------|
| **Technical** | **MOCK-first** CI; **contract tests** on workflow API; **incremental** refactors; **validation** on assistant output |
| **Market** | Two **pilots**: **UI+assistant** and **API-only** prebuilts; measurable **time-to-first workflow** |
| **Resource** | **Cut scope** to **prebuilt + MOCK** before cutting **API parity** or **audit** trails; **defer** auth/billing/cloud |

## Functional Requirements

### Workflow definition & catalog

- **FR1:** An **author** can **browse** available **prebuilt workflow definitions** (templates) exposed by the product.
- **FR2:** An **author** can **instantiate** a run from a **prebuilt** definition with **inputs** appropriate to that definition.
- **FR3:** An **author** can **persist** and **re-open** workflow definitions or configurations the product supports for authoring (within MVP limits of the builder).
- **FR4:** An **author** can **see** whether a definition is **safe for demo** (e.g. mock-capable) versus requiring **live integrations**, when the product surfaces that distinction.

### Workflow execution & lifecycle

- **FR5:** An **operator** can **start** a workflow run from an **authorised** definition.
- **FR6:** An **operator** can **view** the **status** of a run (e.g. pending, running, completed, failed, cancelled) using **canonical** statuses.
- **FR7:** An **operator** can **view** **step-level** progress or outputs the product exposes for that run.
- **FR8:** A **system** can **resume or retry** behaviour where the product defines it, without violating **idempotency** rules for the same logical request.
- **FR9:** An **operator** can **distinguish** **user/configuration error** from **system/integration error** when the product provides that distinction.

### Conversational authoring (assistant)

- **FR10:** An **author** can **describe** desired workflow behaviour in **natural language** through a **chat-style** interface.
- **FR11:** An **author** can **receive** a **structured proposal** (e.g. steps or graph) derived from that conversation, when the assistant is enabled.
- **FR12:** An **author** can **confirm or reject** a proposal before it is **executed** or **saved**, when the product requires confirmation.
- **FR13:** An **author** can **move** from an assistant proposal to **editing** in the **visual builder** (or equivalent UI) when both exist.
- **FR14:** The **product** can **reject or flag** assistant output that does not **validate** against the **engine’s** allowed structure.

### Web application (customer UI)

- **FR15:** A **user** can **authenticate or access** the web application according to the **MVP access model** (which may be minimal).
- **FR16:** An **author** can **author** or **adjust** workflows through the **web UI** without using the **HTTP API** for that path.
- **FR17:** An **operator** can **run** and **monitor** workflows from the **web UI**.
- **FR18:** A **user** can **navigate** core areas: **definitions/templates**, **runs**, and **assistant** (if enabled), at a level appropriate to MVP.

### HTTP API (prebuilt workflows, headless)

- **FR19:** An **integration client** can **list** available **prebuilt workflow definitions** via **HTTP** without using the web UI.
- **FR20:** An **integration client** can **start** a run from a **prebuilt** definition via **HTTP** with a **documented** request shape.
- **FR21:** An **integration client** can **retrieve** **run status** and **outputs** (where exposed) via **HTTP**.
- **FR22:** An **integration client** receives **actionable error responses** for **failed** or **invalid** requests, when the product defines error semantics.

### Provider & connector integration

- **FR23:** The **product** can **invoke** **partner connectors** (adapters) for **external** steps according to **workflow** configuration.
- **FR24:** The **product** can **operate** in a **mocked** mode where **external** calls are **deterministic** and **do not** require live provider credentials.
- **FR25:** The **product** **normalises** external **status** values to **internal canonical** values before **persisting** to core domain entities.
- **FR26:** The **product** does **not** perform **KYC/AML** programs itself; **identity or compliance** steps are **delegated** to **partner** connectors when configured.

### Webhooks & inbound events

- **FR27:** The **product** can **accept** **webhook** payloads from **providers** where supported.
- **FR28:** The **product** can **store** inbound webhook payloads **before** or **as part of** processing, to support **audit** and **replay** investigation.
- **FR29:** The **product** can **deduplicate** webhook processing using **idempotency** keys or equivalent **product** rules.

### Observability, support & audit

- **FR30:** An **internal operator** can **view** **run records** sufficient to **demo** or **audit** a workflow execution path in **mock** mode.
- **FR31:** A **support user** can **inspect** **run history**, **step outcomes**, and **stored webhook** payloads (where applicable) to **explain** failures.
- **FR32:** The **product** avoids exposing **secrets** in **user-visible** errors or **logs** surfaced to clients.

### Documentation & discoverability

- **FR33:** A **consumer** can **discover** **HTTP** capabilities via **machine-readable API description** (e.g. OpenAPI) for **workflow** surfaces the product exposes.
- **FR34:** A **new engineer** can **follow** **documented** steps to **run** the product **locally** using the **containerised** or **scripted** setup provided.

### Administration & tenancy (MVP posture)

- **FR35:** The **product** supports **single-organisation / single-deployment** usage assumptions documented for MVP, without requiring **multi-tenant** isolation unless explicitly added later.

## Non-Functional Requirements

### Performance

- **NFR-P1:** **Interactive** UI actions (navigate, open run, submit form) complete within **under 2 seconds** for primary page transitions under **local** deployment and **MOCK** backends unless blocked by user network.
- **NFR-P2:** **Workflow HTTP API** paths for **list definition**, **start run**, and **get status** respond within **under 3 seconds at p95** under the **local** stack with **MOCK** providers for representative payloads (formal load testing deferred).
- **NFR-P3:** **Assistant** round-trips depend on **LLM** latency; the product **surfaces progress** (e.g. streaming or explicit “working”) so users are not left **without feedback for more than 10 seconds** without messaging.

### Security

- **NFR-S1:** **Secrets** (API keys, webhook secrets, DB credentials) are **never** returned in **API responses** or **client-visible** error payloads; **never** logged in **clear text** in application logs intended for developers.
- **NFR-S2:** **Transport:** External-facing deployments use **TLS** for HTTP; **local dev** may use HTTP with **documented** risk.
- **NFR-S3:** **Sensitive fields** (PII, financial references, integration payloads) are **minimised** in persistence and logs per **data-minimisation** posture; retention expectations are **documented**.
- **NFR-S4:** **Webhook** endpoints and **admin** surfaces use **appropriate** authentication for the **MVP model** (may be **minimal**, but **not** wide-open in documented deployment patterns).

### Reliability & correctness

- **NFR-R1:** **Idempotent** operations (as defined for orders, webhooks, runs) remain **correct** across **retries** and **process restarts** for **documented** MVP behaviours.
- **NFR-R2:** **Canonical status** values are **consistent** across **UI**, **API**, and **persistence** for the same run.

### Integration

- **NFR-I1:** **Outbound** partner calls use **documented timeouts** and **error mapping** so users see **actionable** failures, not hung requests.
- **NFR-I2:** **Connector** behaviour is **swappable** between **mock** and **live** per **MOCK_MODE** (or equivalent) without changing **workflow** semantics beyond **documented** differences.

### Observability & operability

- **NFR-O1:** Operators can **correlate** a **run** with **logs** using a **request or run identifier** in supported components.
- **NFR-O2:** **Local** deployment (Docker or scripts) is **reproducible**: a new engineer can reach a **healthy** stack following docs in **one working session** barring environment-specific blockers.

### Scalability (MVP posture)

- **NFR-SC1:** The **architecture** does not **preclude** horizontal scaling of **stateless** tiers later; **explicit** multi-tenant scale targets are **out of scope** for this PRD phase.

### Accessibility (web UI)

- **NFR-A1:** **Core** authoring and run-monitoring flows use **semantic HTML** and **keyboard-navigable** controls where feasible; a **full WCAG 2.2 AA** audit is **post-MVP** unless a customer mandates earlier.

### Documentation

- **NFR-D1:** **OpenAPI** (or equivalent) for **documented** HTTP surfaces is **kept in sync** with behaviour for each **MVP release milestone** agreed with stakeholders.
