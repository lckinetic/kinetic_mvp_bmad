# Kinetic MVP – Development & Agent Operating Guide

## 1. Purpose of This Repository

This repository contains the **local-first MVP implementation of Kinetic**.

The goal of this MVP is to:
- Demonstrate a **working end-to-end crypto flow**:
  - Fiat on-ramp → wallet → off-ramp
- Validate third-party integrations (starting with Banxa)
- Support demos for partners and investors
- Be built **without a full-time CTO**, using AI agents + light external dev help

This is **not** the final platform architecture.  
This is a **fast, reliable, demoable MVP**.

---

# Kinetic MVP — AI-Powered Workflow Automation for Crypto Operations

Kinetic is an AI-assisted workflow automation platform that enables fintechs and treasury teams to build and execute crypto workflows across multiple providers.

This MVP demonstrates:
- Prebuilt workflow execution
- AI-generated workflows from natural language
- Unified execution engine with step tracking and metrics
- Modular adapter-based architecture

---

## 🚀 Key Features

### 1. Prebuilt Workflows
Users can select predefined templates such as:
- Treasury Rebalance (Onramp → Offramp)
- Managed Crypto Treasury (Wallet → Trade → Withdraw)

### 2. AI Workflow Generation
Users can describe a workflow in natural language:
> “Buy BTC and withdraw to wallet”

Kinetic will:
- interpret intent
- generate a workflow graph
- allow user to review/edit
- execute it end-to-end

### 3. Editable Workflows
Generated workflows are fully editable before execution, enabling:
- parameter tuning
- flow customisation
- safe execution control

### 4. Step-Level Execution Tracking
Every workflow run includes:
- step-by-step status
- duration metrics
- detailed payload logs

---

## 🧠 Architecture Overview

Kinetic follows a **Modular Monolith with Adapter Pattern**:

- **UI Layer**: HTML + JS pages (`/ui`, `/ui/ai`)
- **API Layer**: FastAPI endpoints (`/workflows`, `/ai`)
- **Engine Layer**:
  - Template runner (prebuilt workflows)
  - Graph runner (AI workflows)
- **Adapter Layer**:
  - Banxa (onramp/offramp)
  - Privy (wallet)
  - Coinbase (trade, balance, withdraw)
- **Persistence Layer**:
  - WorkflowRun
  - WorkflowStep

---

## 🧩 Project Structure

app/
api/              # FastAPI routes
ai/               # Interpreter + schemas
engine/           # Workflow + graph execution
workflows/        # Prebuilt workflow templates
adapters/         # External provider integrations
services/         # Legacy / domain services
db/               # Models and engine
ui/               # HTML UI pages

---

## 🔌 API Endpoints

### Workflows
- `GET /workflows/templates`
- `POST /workflows/run/{template_name}`
- `GET /workflows/runs/{id}`
- `GET /workflows/runs/{id}/steps`

### AI
- `POST /ai/interpret`
- `POST /ai/run-graph`

---

## 🖥 UI Pages

- `/ui` → Prebuilt workflow runner
- `/ui/ai` → AI workflow generator

---

## ⚙️ Running Locally

```bash
uvicorn app.main:app --reload

## 3. MVP Scope (What We Are Building)

### In Scope (MVP)
- Banxa fiat on-ramp (sandbox first)
- Banxa fiat off-ramp
- Basic wallet abstraction (Privy or stub initially)
- Order lifecycle tracking
- Webhook handling with idempotency
- Minimal UI or API-only demo

### Out of Scope (MVP)
- Visual workflow builder
- Multi-provider routing
- Dynamic module registry
- Runtime AI orchestration
- DeFi strategies or complex treasury logic
- Production-grade IAM or compliance tooling

---

## 4. High-Level Architecture (MVP)

Client (UI / CLI / Postman)
        |
        v
FastAPI Endpoints
        |
        v
Service Layer (pure Python)
        |
        v
Integration Clients (Banxa / Wallet)
        |
        v
Mock APIs OR Real APIs

---

## 5. Repository Structure

```
kinetic-mvp/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ services/
│  │  └─ tests/
│  ├─ pyproject.toml
│  ├─ .env.example
│  └─ README.md
├─ infra/
│  └─ docker-compose.yml
└─ README.md
```

---

## 6. Database Strategy

- ORM: **SQLModel**
- Migrations: **None for MVP**
- Tables created on startup via `SQLModel.metadata.create_all(engine)`

---

## 7. AI Agent Team (Internal Dev Team)

Agents act as **build-time helpers**, not runtime logic.

Roles:
- Orchestrator
- Tech Lead (CTO replacement)
- Repo Lead Dev
- Pair Programmer
- QA / Test Engineer
- AppSec-lite

---

## 8. Definition of Done

- Working code
- Local run instructions
- Tests or test steps
- One happy-path example
- No unnecessary abstractions

---

## 9. How to Run Locally

```bash
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
test from another terminal
curl http://localhost:8000/health

---

## 10. Guiding Philosophy

> Proof beats elegance.  
> Working beats perfect.  
> Deterministic beats clever.


## activate environment
source .venv/bin/activate

# start or stop postgresql
brew services stop postgresql@15
brew services start postgresql@15
brew services restart postgresql@15
psql -h 127.0.0.1 -p 5432 -U kinetic -d kinetic

\dt
\q

# Postman Collection

This folder contains the version-controlled Postman collection and environment
for local MVP development.

Rules:
- Any new API endpoint must be reflected here.
- Update collection before merging feature branch.
- Keep examples realistic and aligned with docs/api/.
MD


# validating the full startup chain
env → config → FastAPI → DB engine → tables → API endpoint

# Swagger UI
http://127.0.0.1:8000/docs

# Health check
http://127.0.0.1:8000/health

# Onramp
http://127.0.0.1:8000/onramp/create

# Onramp
http://127.0.0.1:8000/onramp/create

http://127.0.0.1:8000/ui
http://127.0.0.1:8000/ui/ai