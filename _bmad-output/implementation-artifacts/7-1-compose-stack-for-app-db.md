---
story_key: 7-1-compose-stack-for-app-db
epic: 7
status: done
sprint: 1
story_prepared_on: '2026-04-26'
---

# Story 7.1: Compose stack for app + DB

Status: **done** - compose stack wiring accepted after code review completion.

## Story

As a **developer**,  
I can **`docker compose up`** the dependencies (and optionally app),  
So that **my environment matches team defaults**.

## Acceptance criteria

1. **Given** compose files, **when** I run them per docs, **then** Postgres (and app if included) start with documented ports and env wiring.

## Tasks / subtasks

- [x] Review current compose setup and align it with documented onboarding/runtime expectations.
- [x] Ensure compose includes reliable Postgres service wiring and health checks.
- [x] Add optional app service wiring (if included) with clear env and port mapping.
- [x] Document compose startup, teardown, and verification commands.
- [x] Add validation steps showing services are reachable using documented defaults.
- [x] Confirm compatibility with existing local `.venv` backend run path (no conflicting assumptions).

## Dev notes

### Implementation summary

- Updated `infra/docker-compose.yml`:
  - Kept hardened Postgres service with health checks and restart policy.
  - Added optional `app` service under `profiles: ["app"]` with:
    - build from `backend/Dockerfile`
    - `env_file` from `backend/.env`
    - compose-safe `DATABASE_URL` override pointing to `postgres` host
    - dependency on healthy Postgres
    - published `8000:8000` port
- Added `backend/Dockerfile` for containerized backend runtime.
- Updated `docs/onboarding-local.md` with optional compose app flow and troubleshooting for container startup.

### Expected implementation touchpoints

- `infra/docker-compose.yml`
- `docs/onboarding-local.md` and related docs
- Optional backend docker runtime files if needed for app service inclusion

## Dev agent record

### Agent model used

Codex 5.3

### Completion notes list

- Implemented optional app container profile without disrupting existing `.venv` workflow.
- Validated compose syntax and profile config:
  - `docker compose -f infra/docker-compose.yml config`
  - `docker compose -f infra/docker-compose.yml --profile app config`
- Kept docs synchronized with compose behavior and expected runtime wiring.

### File list

- `_bmad-output/implementation-artifacts/7-1-compose-stack-for-app-db.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `infra/docker-compose.yml`
- `backend/Dockerfile`
- `docs/onboarding-local.md`

## Change Log

- **2026-04-26** - Story 7.1 created and kicked off; status -> in-progress.
- **2026-04-26** - Story 7.1 implemented; status -> review.
- **2026-04-26** - Story 7.1 code review completed; status -> done.
