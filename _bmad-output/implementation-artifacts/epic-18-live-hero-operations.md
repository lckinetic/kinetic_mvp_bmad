# Epic 18 — Live hero operations (non-mock mode)

**Status:** backlog  
**Plan:** `_bmad-output/planning-artifacts/phase-3-live-operations/epic-plan.md`

## Goal

Run the hero journey against **Privy** (treasury + payouts) when `MOCK_MODE=false`, while preserving the existing mock demo path. **Banxa on-ramp is optional** — fund treasury by sending sandbox USDC to the live address.

## Sprint map

| Sprint | Stories | Required? | Milestone |
|--------|---------|-----------|-----------|
| A | 18.1–18.5, 18.9 | **Yes** | Live Privy treasury + inbound deposit detection |
| B | 18.6–18.8 | **No** | Banxa on-ramp (when credentials available) |
| C | 18.10–18.13 | **Yes** | Live contractor payout transfer |
| D | 18.14–18.17 | **Yes** | Docs, env templates, diagnostics |

**Required build order:** A → C → D. Sprint B anytime after A if desired.

## Stories

### Required

- [ ] 18.1 Privy settings & startup validation
- [ ] 18.2 Live Privy treasury wallet create
- [ ] 18.3 Live balance read & reconciliation
- [ ] 18.4 Treasury config-status & UI live indicators
- [ ] 18.5 Live mode guardrails (mock-only endpoints; manual deposit path)
- [ ] 18.9 Inbound deposit detection (webhook/poll)
- [ ] 18.10 Privy outbound USDC transfer
- [ ] 18.11 contractor_payout live execution path
- [ ] 18.12 Real tx metadata on transfers
- [ ] 18.13 Sandbox payout integration tests
- [ ] 18.14 Live onboarding docs
- [ ] 18.15 .env.live.example template
- [ ] 18.16 Live hero demo script (manual deposit default)
- [ ] 18.17 Provider diagnostics in Settings

### Optional (Sprint B — Banxa)

- [ ] 18.6 Banxa sandbox on-ramp adapter
- [ ] 18.7 On-ramp → treasury deposit reconciliation
- [ ] 18.8 Live funding wizard Banxa integration

## Prerequisites

- Privy sandbox app credentials **(required)**
- PostgreSQL recommended for live dev
- Banxa sandbox keys **(optional — Sprint B only)**
