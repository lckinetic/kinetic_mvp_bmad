# kinetic-mvp-bmad — Source Tree Analysis

**Date:** 2026-04-12  
**Scan:** BMad alignment (deep-style pass on critical paths; not an exhaustive file-by-file read)

## Overview

The repository centers on **`backend/app`**: FastAPI entrypoint, API routers, services, provider adapters, workflow engine, and SQLModel models. **`docs/`** holds product and engineering documentation, Postman assets, and BMad-generated indexes. **`_bmad/`** stores BMad module configuration; **`_bmad-output/`** holds BMad artifacts such as **`project-context.md`**.

## Directory Structure (high level)

```
kinetic-mvp-bmad/
├── _bmad/                      # BMad module config (bmm, core)
├── _bmad-output/               # BMad outputs (e.g. project-context.md)
├── .cursor/skills/             # Cursor BMad skills (workflows)
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app factory, router includes, lifespan
│   │   ├── api/                # HTTP routers (health, onramp, offramp, webhooks, workflows, ai)
│   │   ├── core/               # config, logging
│   │   ├── db/                 # engine, SQLModel models
│   │   ├── services/           # domain services, provider clients
│   │   ├── adapters/           # Banxa, Privy, Coinbase clients
│   │   ├── engine/             # graph runner, metrics, registry
│   │   ├── workflows/          # templates, validation, registry
│   │   ├── ai/                 # interpreter, schemas
│   │   └── ui/                 # minimal UI router
│   └── pyproject.toml
├── docs/                       # PRD-style docs, architecture, Postman
├── infra/
│   └── docker-compose.yml      # Local Postgres
└── (project root metadata, git, etc.)
```

## Critical Directories

### `backend/app/api/`

**Purpose:** HTTP surface area — route definitions, request/response models, dependency injection.  
**Entry:** Routers included from `main.py`.  
**Rule:** Keep provider-specific logic out; delegate to services.

### `backend/app/services/`

**Purpose:** Business logic, orchestration, Banxa and order lifecycle behavior.  
**Contains:** Service modules and `orders/` subpackage.  
**Integration:** Called by API layer; uses DB and adapters.

### `backend/app/adapters/`

**Purpose:** Provider-specific HTTP/SDK boundaries (Banxa, Privy, Coinbase).  
**Integration:** Used by services; must respect `MOCK_MODE` when implemented at call sites.

### `backend/app/db/`

**Purpose:** SQLModel models (`Order`, `WebhookEvent`, `WorkflowRun`, …), engine helpers.  
**Entry:** Models imported in `main.py` before table creation.

### `backend/app/engine/` and `backend/app/workflows/`

**Purpose:** Workflow execution, graph runner, templates (`managed_treasury`, `treasury_demo`), validation.  
**Note:** Extending this area requires preserving registry and validation patterns.

### `docs/`

**Purpose:** Source-of-truth documentation, AI principles, Postman collections.  
**See:** `docs/ai/architecture-principles.md` for non-negotiable MVP rules.

### `_bmad-output/`

**Purpose:** BMad-generated artifacts for agents (e.g. **`project-context.md`**).

## Tests

`pyproject.toml` declares **`app/tests`** as test root; add new tests there when introducing coverage.
