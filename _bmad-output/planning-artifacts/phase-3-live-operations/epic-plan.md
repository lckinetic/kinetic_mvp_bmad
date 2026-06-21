---
phase: phase-3-live-operations
status: draft
project_name: kinetic-mvp-bmad
brownfieldBaseline: Epics 10–17 complete (hero journey mock-first)
---

# Epic Plan — Live Hero Operations (Non-Mock Mode)

## Transformation Goal

Enable the **same hero journey** completed in mock mode to run against **real provider sandboxes** when `MOCK_MODE=false`:

**Create Workspace → Privy Treasury Wallet → Fund (manual deposit or optional on-ramp) → Recipients → Payout Workflow → Live Payout → Monitor**

**Positioning unchanged:** Kinetic orchestrates and monitors treasury + payout operations; **Privy** (custody/transfers) is required for live mode. **Banxa** (on-ramp) is an **optional** funding path — the epic is completable by sending sandbox USDC directly to the treasury address.

**Not in scope for Epic 18:** auth/RBAC, multi-tenant SaaS hardening, automated schedule cron, mainnet production launch, MetaMask/Trust self-custody connect.

---

## Current Baseline (Post Epic 17)

| Capability | Mock (`MOCK_MODE=true`) | Live (`MOCK_MODE=false`) today |
|------------|-------------------------|--------------------------------|
| Treasury wallet create | Deterministic Privy mock | **`NotImplementedError`** |
| Fund treasury wizard | UI-simulated fiat → on-ramp → deposit | Simulate endpoints **blocked** |
| Treasury balance | Internal ledger from transfers | Privy balance read **not implemented** |
| Payout run | Ledger debit only (no chain tx) | Same — **no live transfer** |
| Banxa on-ramp | Mock order IDs | **`NotImplementedError`** (optional — not required for epic completion) |
| AI payout drafts | Mock + optional live OpenAI (`AI_MOCK_MODE`) | AI already decoupled |

Epic 18 closes the gap for **hero-domain** live paths without rewriting the platform.

---

## Epic Sequencing (within Epic 18)

| Sprint | Theme | Stories | Required? | Unlocks |
|--------|-------|---------|-----------|---------|
| **A** | Live Privy treasury | 18.1–18.5, **18.9** | **Yes** | `MOCK_MODE=false` can create treasury, detect inbound USDC |
| **B** | Banxa on-ramp (optional) | 18.6–18.8 | **No** | Fund wizard step 2 calls live Banxa sandbox |
| **C** | Live payout execution | 18.10–18.13 | **Yes** | Contractor payout sends real sandbox USDC |
| **D** | Ops & demo readiness | 18.14–18.17 | **Yes** | Documented sandbox walkthrough + diagnostics |

**Build order (required):** A (+ 18.9) → C → D.

**Optional:** Sprint B after A if Banxa credentials are available. C can start after A once treasury is funded manually (send USDC to live address + 18.9 detects deposit).

### Funding paths (live mode)

| Path | How | Stories |
|------|-----|---------|
| **Required — manual deposit** | Copy treasury address → send sandbox USDC from faucet/wallet → inbound detected | 18.5, **18.9**, 18.3 |
| **Optional — Banxa on-ramp** | Fund wizard step 2 initiates Banxa sandbox order | 18.6–18.8 (+ 18.7 reconciliation) |

---

## Cross-Cutting Technical Dependencies

| Layer | Reuse | Extend |
|-------|-------|--------|
| Adapters | `PrivyClient`, `BanxaClient` mock pattern | Live HTTP/SDK paths behind `mock_mode` flag |
| Config | `MOCK_MODE`, `AI_MOCK_MODE` decoupling | `PRIVY_*`, validate live env at startup |
| Treasury service | Ledger (`TreasuryTransfer`), guardrails | Reconcile with provider balance; real tx hashes |
| Engine | `contractor_payout` template | Call Privy transfer before ledger commit |
| Activity / Alerts | Existing ingestion (E14/E15) | Live failure + deposit events |
| UI | Live badge pattern (`AI_MOCK_MODE`) | Treasury/Settings show provider + sandbox status |
| API | Error envelope (E2) | `PROVIDER_NOT_CONFIGURED`, `PROVIDER_UNAVAILABLE` |

**Architecture rules (from `project-context.md`):**

- API → services → adapters → DB (no provider calls in routes).
- Keep mock path **deterministic** for demos; live path behind explicit env.
- Never log secrets; use `safe_settings_log` / redaction patterns from E8.

---

# Epic 18 — Live Hero Operations

## Epic Definition

Wire hero treasury, funding, and payout flows to **Privy** (custodial wallet + transfers). **Banxa sandbox on-ramp is optional** — manual USDC deposit to the treasury address is the required live funding path.

## Business Objectives

- Validate product narrative with **real sandbox transactions**, not only simulated ledger entries.
- Prove path from **USDC in treasury → contractor payout** (fiat on-ramp optional).
- Keep mock mode as default for investor/demo safety.

## User Value

- **Treasury manager:** real Privy wallet address, real inbound USDC, balance reflects provider state.
- **Finance ops:** payout run produces a real sandbox transfer with traceable tx reference.
- **Demo operator:** clear Live vs Mock indicators; documented sandbox credentials setup.

## Dependencies

- **E11–E13** treasury, recipients, payout workflows (done).
- **E14–E15** activity + alerts for live failure visibility (done).
- **E17** funding wizard UX (done — Banxa integration in Sprint B is optional; manual deposit path documented in Sprint D).
- External: **Privy app credentials (required)**; Banxa sandbox keys **(optional, Sprint B only)**.

## Technical Dependencies

| Provider | Hero use | Implementation surface |
|----------|----------|------------------------|
| **Privy** | Treasury wallet create, balance read, USDC transfer on Base | `backend/app/adapters/privy/client.py`, `treasury_service.py`, `contractor_payout.py` |
| **Banxa** _(optional)_ | Fiat → USDC on-ramp (funding wizard step 2) | `backend/app/adapters/banxa/client.py` — Sprint B only |
| **OpenAI** | Already live via `AI_MOCK_MODE` | No Epic 18 change required |

---

## Suggested Story Breakdown

### Sprint A — Live Privy treasury foundation

| Story | Title | Acceptance summary |
|-------|-------|-------------------|
| **18.1** | Privy settings & startup validation | `PRIVY_APP_ID`, `PRIVY_APP_SECRET` (or documented equivalent) required when `MOCK_MODE=false`; clear startup error if missing |
| **18.2** | Live Privy treasury wallet create | `POST /treasury` provisions real sandbox wallet on configured network (default Base); persists `provider_wallet_id` + address |
| **18.3** | Live balance read & reconciliation | `GET /treasury` reflects provider USDC balance; optional reconcile job or on-read sync; ledger stays source for payout guardrails |
| **18.4** | Treasury config-status & UI live indicators | `GET /treasury/config-status` (non-secret); UI shell badge **LIVE OPS** when `MOCK_MODE=false`; mock-only controls hidden |
| **18.5** | Live mode guardrails | `simulate-deposit` / `simulate-failed-payout` return `MOCK_ONLY` when not in mock; document **manual sandbox USDC deposit** as required live funding path |
| **18.9** | Inbound deposit detection | Webhook and/or polling marks inbound USDC to treasury address as `TreasuryTransfer` inbound _(required for manual funding)_ |

### Sprint B — Banxa on-ramp _(optional)_

| Story | Title | Acceptance summary |
|-------|-------|-------------------|
| **18.6** | Banxa sandbox on-ramp adapter | Real Banxa API for create order / quote in sandbox; replaces `NotImplementedError` in on-ramp path |
| **18.7** | On-ramp → treasury deposit reconciliation | Completed on-ramp credits treasury ledger + activity event with partner reference |
| **18.8** | Live funding wizard integration | Wizard step 2 calls Banxa when configured; otherwise shows manual deposit instructions only |

### Sprint C — Live payout execution

| Story | Title | Acceptance summary |
|-------|-------|-------------------|
| **18.10** | Privy outbound USDC transfer | Adapter method: treasury wallet → recipient address on network; returns tx hash / transfer id |
| **18.11** | `contractor_payout` live execution | Template calls Privy transfer **before** ledger commit; failed provider call → failed run + alert |
| **18.12** | Real tx metadata on transfers | `TreasuryTransfer.transaction_hash` stores provider reference; activity/alerts show real refs |
| **18.13** | Sandbox payout integration tests | Tests with mocked HTTP or recorded fixtures; no secrets in repo |

### Sprint D — Ops, docs & demo readiness

| Story | Title | Acceptance summary |
|-------|-------|-------------------|
| **18.14** | Live onboarding docs | `docs/onboarding-live-sandbox.md` + update `onboarding-local.md` cross-links |
| **18.15** | `.env.live.example` | Template for `MOCK_MODE=false`, Privy (required), Banxa _(optional)_, optional `AI_MOCK_MODE` |
| **18.16** | Live hero demo script | `docs/demo-live-sandbox-flow.md` — **manual deposit path** as default; Banxa as optional addendum |
| **18.17** | Provider diagnostics in Settings | Settings shows Privy configured (required) and Banxa configured (optional); link to config-status endpoints |

---

## Environment & Prerequisites

```dotenv
# Required when MOCK_MODE=false (Epic 18)
MOCK_MODE=false
DATABASE_URL=postgresql+psycopg2://...   # recommended for live dev

# Privy (Sprint A+)
PRIVY_APP_ID=
PRIVY_APP_SECRET=
PRIVY_API_BASE_URL=          # if non-default
PRIVY_TREASURY_NETWORK=base  # default Base for hero

# Banxa sandbox (optional — Sprint B only)
# BANXA_API_KEY=
# BANXA_API_SECRET=
# BANXA_ENV=sandbox
# BANXA_WEBHOOK_SECRET=

# AI remains independent
AI_MOCK_MODE=true            # can stay mock while testing live treasury
```

**Team prerequisites before Sprint A coding:**

1. Privy developer app with server-side wallet API access for sandbox/testnet.
2. Decision: **Base Sepolia / Base sandbox** as hero network (align with E11 default `base`).
3. _(Optional)_ Banxa sandbox merchant credentials if implementing Sprint B.

---

## FR / Hero Step Coverage

| Hero step | Epic 18 stories |
|-----------|-----------------|
| Create treasury wallet | 18.1, 18.2, 18.4 |
| Fund treasury (required) | 18.5, **18.9**, 18.3 — manual sandbox USDC deposit |
| Fund treasury (optional) | 18.6–18.8 — Banxa on-ramp when configured |
| Add recipient | — (already live-ready; no provider) |
| Create / run payout workflow | 18.10–18.13 |
| Monitor (activity/alerts) | 18.7, 18.9, 18.12 (feeds existing E14/E15) |

---

## Out of Scope (defer to future epics)

| Item | Reason |
|------|--------|
| Mainnet production launch | Sandbox validation first |
| Auth / RBAC / multi-tenant | PRD defer |
| Scheduled payout cron | Display-only schedule exists (E17) |
| Multi-treasury wallets per workspace | Product decision pending |
| MetaMask / Trust wallet connect backend | E17 UI preview only |
| Legacy graph workflows live (Coinbase path) | Focus hero `contractor_payout` |
| Railway/production deployment hardening | Separate infra epic |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Provider API drift | Adapter isolation; contract tests with fixtures |
| Ledger vs chain balance mismatch | Reconciliation story 18.3; show both in UI if diverged |
| Accidental mainnet spend | Network locked to sandbox in config; startup validation |
| Secret leakage in logs | Existing redaction (E8); audit new adapter logs |
| Long webhook latency for funding | Polling fallback (18.9); manual refresh in UI |

---

## Success Metrics

- Hero journey completable in **Privy sandbox** with **manual USDC deposit** (Banxa not required).
- Treasury create succeeds with `MOCK_MODE=false` and valid Privy credentials.
- At least one **end-to-end sandbox payout** with real tx reference in Activity Centre.
- Mock mode regression unchanged (`MOCK_MODE=true` demo path still <5 min).
- Live setup documented in ≤15 minutes for a new developer (Privy-only path).

---

## 4-Sprint Delivery Sequence

| Sprint | Focus | Required? | Demo milestone |
|--------|-------|-----------|----------------|
| 1 (A) | Privy treasury + inbound deposits | **Yes** | “Here is our live sandbox treasury address — fund it manually” |
| 2 (B) | Banxa on-ramp | **No** | “We on-ramped sandbox USDC into treasury” _(optional)_ |
| 3 (C) | Live payout | **Yes** | “We paid a contractor on-chain (sandbox)” |
| 4 (D) | Docs/diagnostics | **Yes** | “New engineer can run live sandbox from docs” |

---

## Related Artifacts

- Baseline hero plan: `_bmad-output/planning-artifacts/phase-2-hero-workflow/epic-plan.md`
- Feedback applied (E17): `_bmad-output/planning-artifacts/phase-2-hero-workflow/hero-flow-feedback-round-1.md`
- Implementation tracking: `_bmad-output/implementation-artifacts/epic-18-live-hero-operations.md` (created when sprint starts)
