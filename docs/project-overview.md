# kinetic-mvp-bmad — Project Overview (BMad)

**Date:** 2026-04-12  
**Type:** backend API + workflow engine (Python / FastAPI)  
**Repository layout:** monolith with primary code under `backend/`, knowledge under `docs/`, BMad under `_bmad/` and `_bmad-output/`

## Executive Summary

Kinetic MVP is a **FastAPI** service that supports **on/off-ramp** flows (Banxa and related adapters), **order persistence** in **PostgreSQL** via **SQLModel**, **webhook ingestion** with **idempotent** processing, and a **workflow / graph execution** layer for demos and automation. **`MOCK_MODE`** defaults to enabled so the system stays demo-safe without live provider calls.

## Classification

| Dimension | Value |
|-----------|--------|
| Repository type | Monolith (single deployable backend; docs + BMad collateral at repo root) |
| Primary language | Python 3.11+ |
| Data store | PostgreSQL |
| API style | REST (FastAPI, OpenAPI at `/docs`) |

## Technology Stack

| Layer | Technology |
|-------|------------|
| HTTP | FastAPI, Uvicorn |
| ORM | SQLModel (Pydantic v2, SQLAlchemy) |
| DB driver | psycopg2-binary |
| Config | python-dotenv, frozen `Settings` dataclass |
| Tests (declared) | pytest, httpx (dev) |

## Key Features (current direction)

- Health and discovery routes; onramp/offramp APIs; webhook ingestion.
- Internal **canonical order statuses** and **DB-level idempotency** for webhooks and client references.
- **Workflow runs** stored for debugging and demos (`WorkflowRun` and engine under `app/engine`, `app/workflows`).
- Optional **AI** and **UI** routers for experimentation (`app/api/ai.py`, `app/ui/router.py`).

## Architecture Highlights

- **Layered design**: API → services → adapters/clients → DB (see `docs/ai/architecture-principles.md`).
- **Audit-first webhooks**: store payloads, then process; do not delete events in MVP.
- **Postman as primary UI** until a full client exists — collections live under `docs/postman/`.

## Development Overview

**Prerequisites:** Python 3.11+, Docker (for Postgres), `uv` or `pip` for installing `backend/pyproject.toml`.

**Typical commands** (from `backend/`):

```bash
# Install
pip install -e ".[dev]"

# Run API (ensure DATABASE_URL and optional MOCK_MODE in .env)
uvicorn app.main:app --reload

# Tests (when present)
pytest
```

See also `docs/overview.md` for product scope and `docs/architecture.md` for the concise technical map.
