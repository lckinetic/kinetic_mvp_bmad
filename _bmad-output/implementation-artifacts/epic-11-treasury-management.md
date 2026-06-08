# Epic 11: Treasury management

## Status
done

## Epic goal
Treasury wallet lifecycle — create, balance, funding instructions, transaction history — scoped to workspace, mock-first with Privy adapter extension.

## Stories implemented

### 11.1 — Treasury & wallet domain models
- `Treasury`, `TreasuryWallet`, `TreasuryTransfer` in `backend/app/db/models.py`
- One treasury per workspace (`uq_treasury_workspace`); one wallet per treasury

### 11.2 — Privy adapter — treasury wallet create
- `PrivyClient.create_treasury_wallet()` in `backend/app/adapters/privy/client.py`
- Deterministic mock addresses; live path raises `NotImplementedError` (mapped to 501 at API)

### 11.3 — Treasury create API & service
- `POST /treasury`, `GET /treasury` in `backend/app/api/treasury.py`
- `create_treasury()` in `backend/app/services/treasury_service.py`
- 409 when treasury already exists for workspace

### 11.4 — Treasury balance read
- Ledger balance from completed `TreasuryTransfer` rows via `compute_balance()`
- Exposed on `GET /treasury` response (`balance` field)

### 11.5 — Funding instructions UI
- Fund treasury panel in `ui_kits/app/Treasury.jsx`: asset, network, address, warning
- Copy funding address button (wallet card also has copy)

### 11.6 — Transaction history
- `GET /treasury/transfers` API; table UI on Treasury screen
- Mock inbound deposits via `POST /treasury/transfers/simulate-deposit`

### 11.7 — Treasury screen (UI)
- Full Treasury screen: balance, connected wallet, fund panel, transaction history
- Create wallet empty state; refresh balance action
- Dashboard treasury balance widget in `ui_kits/app/Dashboard.jsx`

### 11.8 — Insufficient balance error state
- `POST /treasury/balance/check` → `INSUFFICIENT_BALANCE` (409) with balance/required/shortfall
- Treasury UI banner with “Fund treasury” scroll CTA

## Tests
- `backend/app/tests/test_treasury_api.py` — create/get, idempotency, deposits, balance check, live-mode 501, main.py mount
- `backend/app/tests/test_privy_adapter.py` — deterministic treasury wallet
- `backend/app/tests/test_ui_shell_navigation_smoke.py` — treasury UI wiring, funding copy, dashboard refresh

## Demo alignment
- `docs/demo-mvp-flow.md` hero steps 5–7 (create wallet, simulate deposit, balance check)

## Review findings (resolved)

### Medium (fixed)
- [x] Live-mode treasury create returned unhandled 500 → `TREASURY_PROVIDER_NOT_CONFIGURED` (501)
- [x] Fund treasury panel missing copy button → “Copy funding address” added
- [x] Non-atomic treasury + wallet create → single transaction with `flush()` + one `commit()`

### Low (fixed)
- [x] Dashboard balance stale after treasury actions → `dashboardRefreshKey` on navigate/hash return
- [x] Treasury router mount not smoke-tested → `test_main_app_mounts_treasury_router`
- [x] No story artifacts for 11.x → this file

### Deferred (out of Epic 11 scope)
- [x] Workspace session scoping via latest workspace ID (Epic 10) — deferred
- [x] Transaction history activity cross-links (Epic 14) — deferred
