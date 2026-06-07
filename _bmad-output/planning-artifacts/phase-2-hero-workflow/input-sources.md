# Input Sources — Phase 2 Hero Workflow

## Product & strategy inputs

| Source | Key contributions |
|--------|-------------------|
| Kinetic Product Vision v2 | Platform positioning, first operational domain, success criteria |
| Founder Alignment Strategy v1 | Hero user, hybrid platform model, competitive positioning |
| Hero Workflow PRD v1 Full | Domain model, screen inventory, FR1–FR10, 4-week plan |
| BMAD PRD v1.0 | JTBD, NFRs, BMAD story guidance |
| UX User Journey Spec v1.0 | Persona, navigation IA, demo flow (<5 min) |

## Brownfield baseline (repository)

| Area | Current state | Gap vs hero workflow |
|------|---------------|----------------------|
| Workflow engine | Template registry, `WorkflowRun`/`WorkflowStep` | Persisted user workflows, hero payout template, scheduling |
| Adapters | Privy/Coinbase/Banxa mock-first | Treasury balance/transfer; wallet persistence |
| AI | `/ai/interpret`, `AI_MOCK_MODE` decoupled | Hero payout NL schema; assistant→engine bridge |
| UI | Home, Workflows, Operations, AI Assistant, Builder (mock) | Dashboard, Treasury, Recipients, Activity Centre, onboarding |
| Domain | Orders, runs, webhooks, proposals | Workspace, Treasury, Recipient, WorkflowDefinition, Activity, Alert |

## Out of scope (this phase)

Trading, yield, fiat banking, enterprise approvals, multi-wallet providers, competing as custody/payment rail.
