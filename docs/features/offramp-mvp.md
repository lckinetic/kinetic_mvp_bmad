# Feature: Offramp (MVP)

## Feature name
Offramp - Create Order (mock) + Retrieve + Webhook lifecycle updates

## Problem / user goal
Enable a corporate user to cash out crypto to fiat (offramp) as part of an end-to-end corporate crypto operations workflow.

## MVP impact (1–2 sentences)
Adds bidirectional capability (onramp + offramp) to demonstrate Kinetic as a pre-built crypto operations workflow engine, not a single-purpose onramp API.

## Scope (in)
- POST /offramp/orders (MOCK_MODE): create an offramp order and persist to DB
- GET /offramp/orders/{order_id}: fetch persisted offramp order
- Webhook updates: existing /webhooks/banxa updates offramp orders too (direction-aware)
- client_reference support + uniqueness rule reused

## Scope (out)
- Real Banxa offramp API calls (can come later behind same interface)
- KYC flows, bank account verification, payout rails
- Multi-currency FX conversion logic
- Authentication / RBAC

## APIhanges
- Add:
  - POST /offramp/orders
  - GET /offramp/orders/{order_id}
  - (Optional) GET /offramp/orders?client_reference=...
- Webhook: update to detect direction and apply status update to offramp order as well

## Data model changes
- Prefer NO new tables
- Reuse Order table with:
  - direction = "offramp"
  - provider = "banxa"
- Optional: add offramp-specific fields later (bank details), but keep out of scope for MVP

## Business logic changes
- Add Offramp service layer:
  - services/offramp_service.py mirrors onramp_service.py
- Extend BanxaClient with create_offramp_order mock
- Extend webhooks handler to update order by order_id + direction (or infer direction from payload)

## Idempotency & retries
- Offramp order creation: same behaviour as onramp
  - client_reference is idempotency handle (unique per provider+direction+client_reference)
- Webhooks: existing idempotency key logic remains

## Error handling
- 400 validation for request
- 404 for unknown order_id
- For duplicate client_reference: return existing order (idempotent behaviour)

## Security & secrets
- No new secrets required for MVP mock mode

## Tests (minimum)
- POST /offramp/orders returns order_id + checkout_url + pending
- GET returns same order after restart
- Webhook updates offramp status to completed
- Terminal protection works (completed can’t revert)
- Duplicate client_reference returns same order

## Docs & Postman updates
- docs/api/offramp.md (new)
- docs/architecture.md add offramp endpoints
- postman: add Offramp folder + requests

## Done definition
- Offramp endpoints appear in /docs
- Postman tests pass for create/get/webhook update
- DB contains offramp rows and uniqueness works
- Webhook event log shows processed events for offramp too
