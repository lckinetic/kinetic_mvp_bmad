# Local Onboarding (Canonical Path)

This is the single recommended onboarding path for running Kinetic MVP locally in backend-first mode.

## Prerequisites

- Python 3.11+
- Docker Desktop (or equivalent Docker runtime)

## 1) Start Postgres

From repo root:

```bash
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml ps
```

Expected: `postgres` is running and healthy.

## Optional: run API in Docker too (after step 4)

If you want the backend app containerized (instead of running it from `.venv`), run this **after completing step 4** (`backend/.env` must exist):

```bash
docker compose -f infra/docker-compose.yml --profile app up -d --build
docker compose -f infra/docker-compose.yml ps
```

Notes:
- `app` service reads `backend/.env`.
- In compose mode, `DATABASE_URL` is automatically pointed to `postgres` service host.
- App is exposed on `http://127.0.0.1:8000`.

## 2) Create and activate virtual environment

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Install backend + dev dependencies

From repo root:

```bash
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"
```

## 4) Configure environment

Create `backend/.env` with:

```dotenv
DATABASE_URL=postgresql+psycopg2://kinetic:kinetic@localhost:5432/kinetic
MOCK_MODE=true
BANXA_API_KEY=replace_me
BANXA_API_SECRET=replace_me
BANXA_ENV=sandbox
BANXA_WEBHOOK_SECRET=replace_me
LOG_LEVEL=INFO
```

Notes:
- Keep `MOCK_MODE=true` for safe local demos.
- Never use production secrets in local files.
- For quick mode switching:
  - `cp backend/.env.mock.example backend/.env` (deterministic demo mode)
  - `cp backend/.env.live.example backend/.env` (real AI mode; requires valid `OPENAI_API_KEY`)
- Or use helper scripts from repo root:
  - `./scripts/use-mock.sh`
  - `./scripts/use-live.sh`
- In live mode (`MOCK_MODE=false`), backend enforces `AI_PROVIDER=openai`, `AI_MODEL`, and `OPENAI_API_KEY`.

## 5) Start API

From repo root:

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --reload --app-dir backend
```

If you started the `app` compose profile, skip this step.

## 6) Verify health and docs

In another terminal:

```bash
curl http://127.0.0.1:8000/health
```

Open:
- `http://127.0.0.1:8000/docs`

Optional AI mode diagnostics (no secret values returned):

```bash
curl http://127.0.0.1:8000/ai/config-status
```

Expected health response:

```json
{"status":"ok"}
```

## 7) MOCK_MODE demo path

### Prebuilt workflow flow

```bash
curl http://127.0.0.1:8000/workflows/templates
curl -X POST "http://127.0.0.1:8000/workflows/run/managed_treasury" -H "Content-Type: application/json" -d '{"input":{"user_email":"demo@example.com","trade_symbol":"BTC-USD","trade_amount":100}}'
curl http://127.0.0.1:8000/workflows/runs
```

### Assistant flow

```bash
curl -X POST "http://127.0.0.1:8000/assistant/proposals" -H "Content-Type: application/json" -d '{"message":"Fund wallet with USDC","session_id":"onboarding-demo"}'
curl -X POST "http://127.0.0.1:8000/assistant/proposals/<proposal_id>/confirm"
curl -X POST "http://127.0.0.1:8000/assistant/proposals/<proposal_id>/execute"
curl "http://127.0.0.1:8000/assistant/proposals/<proposal_id>/ui-handoff"
```

## 8) Verify tests

From repo root:

```bash
source .venv/bin/activate
python -m pytest backend/app/tests/test_workflows_openapi.py backend/app/tests/test_assistant_openapi.py -q
```

## 9) CI smoke parity command

The GitHub Actions smoke workflow runs this command:

```bash
source .venv/bin/activate
python -m pytest backend/app/tests/test_workflows_headless_lifecycle.py backend/app/tests/test_workflows_openapi.py -q
```

This keeps CI focused on prebuilt workflow list/start/status coverage in MOCK_MODE.

## Troubleshooting

- **`ModuleNotFoundError: sqlmodel`**
  - Activate venv and reinstall editable backend package:
  - `source .venv/bin/activate && python -m pip install -e "backend[dev]"`

- **DB connection errors on startup**
  - Confirm Postgres container is healthy:
  - `docker compose -f infra/docker-compose.yml ps`
  - Verify `DATABASE_URL` in `backend/.env`.

- **App container exits immediately**
  - Check logs:
  - `docker compose -f infra/docker-compose.yml logs app`
  - Make sure `backend/.env` exists and has required keys.

- **Port 8000 already in use**
  - Stop previous server process or run with a different port:
  - `python -m uvicorn app.main:app --reload --app-dir backend --port 8001`

- **`/health` fails but server appears started**
  - Check logs for DB init failures.
  - Ensure Docker postgres is reachable on `localhost:5432`.
