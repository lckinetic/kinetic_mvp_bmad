# Hero Flow Feedback — Round 1 (2026-06-20)

Source: product walkthrough notes (`Kinetic hero flow feedback round 1.docx`).

## Priority overview

| Priority | Theme | Stories | Rationale |
|----------|-------|---------|-----------|
| **P0** | Treasury clarity & funding narrative | 17.1–17.5 | Blocks demo comprehension; quick UX wins |
| **P1** | Readability & iconography | 17.6–17.7 | Site-wide polish; low risk |
| **P2** | Recipient payout profile | 17.8–17.10 | Aligns contractor table with real ops mental model |
| **P3** | Dashboard schedule visibility | 17.11 | Closes loop on recurring workflow value |

---

## Epic 17 — Hero flow feedback (round 1)

### P0 — Treasury

| ID | Story | Acceptance |
|----|-------|------------|
| 17.1 | **Privy wallet labeling** | Treasury wallet explicitly labeled as Privy custodial wallet; room for future providers |
| 17.2 | **Wallet source selector (UI-only)** | UI offers Privy (active) + MetaMask / Trust Wallet preview options; no backend connect required |
| 17.3 | **Funding path narrative** | Fund panel explains fiat treasury → on-ramp → USDC transfer; demo simulate labeled as shortcut |
| 17.4 | **Meaningful deposit counterparty** | Simulated deposits show business-meaningful counterparty (not "Demo deposit") |
| 17.5 | **Refresh balance feedback** | Refresh shows in-progress state and confirmation when complete |

### P1 — UX polish

| ID | Story | Acceptance |
|----|-------|------------|
| 17.6 | **Operational typography** | Non-home pages use larger base text (14px+) for body/table content |
| 17.7 | **Copy icon actions** | Address copy uses icon button with accessible label instead of text-only buttons |

### P2 — Recipients & workflows

| ID | Story | Acceptance |
|----|-------|------------|
| 17.8 | **Recipient payout defaults** | Recipient stores optional default asset, amount, cadence, schedule day |
| 17.9 | **Expanded recipients table** | Table shows payout currency, amount, frequency columns |
| 17.10 | **Workflow pre-fill** | Creating workflow pre-fills from selected recipient defaults |

### P3 — Dashboard

| ID | Story | Acceptance |
|----|-------|------------|
| 17.11 | **Upcoming scheduled payouts** | Enabled weekly/monthly workflows appear in Dashboard widget |

---

## Out of scope (this round)

- Live MetaMask / Trust Wallet connection backend
- Live fiat on-ramp integration (Banxa hero path)
- Multi-treasury wallet backend (UI may preview future state only)
- Automated scheduler execution (display-only schedule on Dashboard)

## Demo doc alignment

Update `docs/demo-mvp-flow.md` funding step to reference fiat → on-ramp → Privy treasury narrative.
