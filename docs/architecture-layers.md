# Backend layering (`backend/app`)

Operational rules for imports and responsibilities. Aligns with `docs/ai/architecture-principles.md` and `_bmad-output/planning-artifacts/architecture.md` §3.

## Packages and roles

| Layer | Path | Role |
|--------|------|------|
| **API** | `app/api/` | HTTP routes, request/response models, FastAPI dependencies. No provider-specific orchestration. |
| **Services** | `app/services/` | Use-cases, orchestration, workflow steps, **construction of clients** used by routes or engine. |
| **Engine** | `app/engine/` | Graph execution, component dispatch, run metrics. Receives ready-made adapter instances (dict) from callers. |
| **Adapters** | `app/adapters/` | Partner HTTP/SDK details, mock vs live behaviour. |
| **DB** | `app/db/` | SQLModel models, engine, session helpers. |
| **AI** | `app/ai/` | Interpreter / LLM-facing helpers (not money movement). |

## Allowed dependency edges (summary)

- **API →** `app.services`, `app.db`, `app.core`, `app.engine` (orchestration entrypoints only), `app.ai` where appropriate.
- **Services →** `app.adapters`, `app.db`, `app.core`, other `app.services`, `app.engine` if needed for shared helpers.
- **Engine →** `app.services` (e.g. workflow step persistence), `app.db`, `app.core`; **not** HTTP frameworks.
- **Adapters →** `app.core` (settings), standard library + HTTP clients only; avoid importing API or services to prevent cycles.

## Forbidden (enforced by convention + review)

- **API must not** import `app.adapters` directly. Thin re-exports under `app.services` (e.g. `banxa_client.py`, `privy_client.py`) are the way routes obtain client classes.

## Exceptions

| Location | Import | Reason | Remove by |
|----------|--------|--------|-----------|
| _(none)_ | — | — | — |

If a temporary exception is required, add a row here and link a follow-up story or issue.

## Automated check

`backend/app/tests/test_api_layer_no_adapter_imports.py` parses `app/api/**/*.py` and fails on any `app.adapters` import. Run from repo `backend/`:

```bash
pytest app/tests/test_api_layer_no_adapter_imports.py -q
```

## Secrets & logs (NFR-S1)

Operational rules live in **`docs/ai/architecture-principles.md` §9** and helpers in **`app/core/secrets_redact.py`** / **`app/core/logging.safe_settings_log`**. Run:

```bash
pytest app/tests/test_secrets_redact.py -q
```
