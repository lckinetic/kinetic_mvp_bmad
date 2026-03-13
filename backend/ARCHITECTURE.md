# Kinetic MVP Backend Architecture

## Overview

Kinetic MVP backend follows a **Modular Monolith architecture using a
Layered + Adapter pattern**.

The goal of this architecture is to: - Keep business workflows easy to
implement - Isolate external integrations - Allow the system to evolve
into microservices later if required - Provide a clear separation
between UI, API, workflow logic, and infrastructure

The system executes **workflow templates** that orchestrate integrations
such as fiat onramps, wallets, and trading venues.

------------------------------------------------------------------------

## High Level Flow

UI\
↓\
API (FastAPI)\
↓\
Workflow Engine\
↓\
Workflow Templates\
↓\
Services / Domain\
↓\
Adapters\
↓\
External Providers

Side persistence: Database

------------------------------------------------------------------------

## Folder Structure

backend/app

-   adapters\
-   api\
-   core\
-   db\
-   domain\
-   engine\
-   services\
-   ui\
-   workflows\
-   main.py

Each layer has a specific responsibility.

------------------------------------------------------------------------

## 1. UI Layer

Location: `app/ui`

Responsibilities: - Display available workflow templates - Show business
descriptions and step outlines - Execute workflows - Display progress
bars and results - Visualise step logs

The UI communicates only with the **API layer**.

------------------------------------------------------------------------

## 2. API Layer

Location: `app/api`

Framework: **FastAPI**

Responsibilities: - Expose REST endpoints - Receive UI requests -
Trigger workflow execution - Return workflow results and step logs

Typical endpoints:

GET /workflows/templates\
GET /workflows/templates/{template}\
POST /workflows/run/{template}\
GET /runs/{run_id}/steps

Rules: - No business logic - Delegates execution to the **engine layer**

------------------------------------------------------------------------

## 3. Engine Layer

Location: `app/engine`

Key components: - runner.py - metrics.py

Responsibilities: - Create workflow run records - Validate input data -
Execute workflow templates - Track execution metrics - Record step
execution status

------------------------------------------------------------------------

## 4. Workflow Layer

Location: `app/workflows`

Components: - registry.py - validation.py - templates/

Templates define **business workflows**.

Examples: - treasury_demo - managed_treasury

A workflow template: - Defines input schema - Provides business
descriptions - Defines execution steps - Calls services and adapters

------------------------------------------------------------------------

## 5. Service Layer

Location: `app/services`

Responsibilities: Reusable internal logic such as: - workflow step
tracking - order lifecycle management - shared workflow utilities

Examples: - workflow_steps.py - order_lifecycle.py

------------------------------------------------------------------------

## 6. Adapter Layer

Location: `app/adapters`

Adapters isolate external providers.

Examples: - banxa/client.py - privy/client.py - coinbase/client.py

Responsibilities: - Communicate with external APIs - Provide mock
implementations for MVP - Allow swapping mock APIs for real APIs later

This follows the **Adapter pattern**.

------------------------------------------------------------------------

## 7. Domain Layer

Location: `app/domain`

Contains business constants and domain definitions.

Examples: - SUPPORTED_CRYPTO_CURRENCIES - SUPPORTED_FIAT_CURRENCIES -
SUPPORTED_BLOCKCHAINS

This keeps business rules independent of workflows and APIs.

------------------------------------------------------------------------

## 8. Database Layer

Location: `app/db`

Responsibilities: - Database models - Session management - Persistence

Core entities: - WorkflowRun - WorkflowStep

These track workflow execution and step history.

------------------------------------------------------------------------

## 9. Core Layer

Location: `app/core`

Responsibilities: - System configuration - Environment settings -
Application-level utilities

Examples: - Settings - Config

------------------------------------------------------------------------

## External Integrations

Current mock integrations: - Banxa - Privy - Coinbase

These are implemented via adapters.

Future integrations can be added without changing workflow logic.

------------------------------------------------------------------------

## Architecture Pattern

The backend uses:

**Modular Monolith + Layered Architecture + Adapter Pattern**

Benefits: - Simple deployment - Clear separation of concerns - Easy to
extend - Easy to refactor into microservices later

------------------------------------------------------------------------

## Future Evolution

Possible future extensions: - Workflow builder UI - AI-generated
workflows - Integration marketplace - Additional providers -
Event-driven execution

The current architecture is designed to support these expansions.
