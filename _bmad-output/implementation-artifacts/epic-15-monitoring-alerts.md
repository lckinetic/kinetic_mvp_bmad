# Epic 15: Monitoring & alerts

## Status
done

## Epic goal
Failure visibility, alerts, and exception resolution for operational control — Dashboard prominence, acknowledge flow, recovery CTAs, Activity Centre history for blocked payouts.

## Stories implemented

### 15.1 — Alert domain model
- `Alert` in `backend/app/db/models.py` with workspace scope, severity/status, recovery fields
- Unique constraint on `(source_kind, source_id, alert_type)`

### 15.2 — Alerts on workflow failure
- `create_alert_from_failed_run()` via `ingest_workflow_run_activity()` when run status is `failed`
- `payout.failed` catalog entry with retry recovery CTA

### 15.3 — Alerts on transfer failure
- `create_alert_from_failed_transfer()` on failed outbound `TreasuryTransfer`
- Mock demo path: `POST /treasury/transfers/simulate-failed-payout`

### 15.4 — Alerts API
- `GET /alerts`, `GET /alerts/{id}`, `POST /alerts/{id}/acknowledge`, `POST /alerts/{id}/resolve`
- `GET /alerts/catalog` — UX-04 aligned copy

### 15.5 — Dashboard alerts widget
- Prominent open-alert banners with recovery + acknowledge in `ui_kits/app/Dashboard.jsx`
- Alerts widget with de-emphasized acknowledged rows

### 15.6 — Error state UX patterns
- Insufficient balance, workflow disabled, recipient inactive, transfer failed, provider unavailable catalog entries
- OpsShell inline recovery CTAs (Fund treasury, Enable workflow, Edit recipient)

### 15.7 — Exception resolution flow
- Auto-resolve workflow alerts on successful payout run
- Blocked payout activity events (`payout.blocked`) for insufficient balance, disabled workflow, inactive recipient
- Recovery deep-links via `nav_route` and `recovery_label`

## Alert catalog (wired)

| Type | Trigger |
|------|---------|
| `insufficient_balance` | Payout run guardrail |
| `workflow.disabled` | Run on disabled workflow |
| `recipient.invalid` | Run with inactive recipient |
| `transfer.failed` | Failed treasury transfer ingest |
| `payout.failed` | Failed workflow run ingest |
| `provider.unavailable` | Live-mode treasury create without provider |

## Tests
- `backend/app/tests/test_alerts_api.py` — insufficient balance, acknowledge, resolve, disabled workflow, inactive recipient, blocked activity, transfer failed, main.py mount
- `backend/app/tests/test_activity_api.py` — `payout.blocked` event type
- `backend/app/tests/test_payout_workflows_api.py` — `RECIPIENT_INACTIVE` response code

## Demo alignment
- `docs/demo-mvp-flow.md` hero steps 14–15 (blocked payout alert + acknowledge + Activity Centre blocked event)

## Review findings (resolved)

### Medium (fixed)
- [x] `recipient.invalid` catalog never emitted → alert on inactive recipient run
- [x] `transfer.failed` unreachable in mock → `simulate-failed-payout` endpoint
- [x] `workflow.disabled` alert API-only → OpsShell allows run attempt + Enable workflow CTA
- [x] Provider unavailable missing → `provider.unavailable` alert on treasury create 501
- [x] Blocked runs missing from Activity Centre → `payout.blocked` ingest on guardrail failures

### Low (fixed)
- [x] No `main.py` mount smoke → `test_main_app_mounts_alerts_router`
- [x] Thin test coverage → five additional alert/activity tests
- [x] Unused import in `alert_service.py` → removed
- [x] No epic artifact → this file

### Deferred
- [ ] Dedicated Alerts management page (Dashboard widget sufficient for MVP)
- [ ] Manual resolve in UI (`POST /resolve` API exists; auto-resolve covers primary path)
- [ ] Workspace session scoping (Epic 10)
