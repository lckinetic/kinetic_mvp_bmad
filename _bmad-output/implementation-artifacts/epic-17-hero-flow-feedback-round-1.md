# Epic 17 — Hero flow feedback (round 1)

**Status:** done  
**Source:** `hero-flow-feedback-round-1.md`

## Scope

Address round-1 hero walkthrough feedback: treasury funding clarity, Privy labeling, recipient payout defaults, workflow pre-fill, dashboard schedule visibility, and operational UI readability.

## Implementation notes

- Wallet source selector is **UI-only** for MetaMask / Trust Wallet; MVP create path remains Privy mock.
- Recipient payout defaults are optional nullable fields with SQLite migration helper.
- Dashboard upcoming payouts lists **enabled** workflows with `weekly` or `monthly` cadence (no cron yet).

## Stories

- [x] 17.1 Privy wallet labeling
- [x] 17.2 Wallet source selector (UI-only)
- [x] 17.3 Funding path narrative
- [x] 17.4 Meaningful deposit counterparty
- [x] 17.5 Refresh balance feedback
- [x] 17.6 Operational typography
- [x] 17.7 Copy icon actions
- [x] 17.8 Recipient payout defaults
- [x] 17.9 Expanded recipients table
- [x] 17.10 Workflow pre-fill from recipient
- [x] 17.11 Dashboard upcoming scheduled payouts
