# Contributing Guide -- Kinetic MVP Backend

This document explains how developers should extend the Kinetic backend
while preserving the existing architecture.

The backend follows a **Modular Monolith with Layered + Adapter
architecture**.\
New code should respect the existing separation of concerns.

------------------------------------------------------------------------

# Adding a New Workflow

Location:

    app/workflows/templates/

Steps:

1.  Create a new template file.

Example:

    app/workflows/templates/my_new_workflow.py

2.  Register the workflow using the registry decorator.

Example:

``` python
@register(
    name="my_workflow",
    version="1.0",
    display_name="My Workflow",
)
```

3.  Define:

-   input_schema
-   business_steps
-   step_outline

4.  Implement the workflow function.

Workflows should:

-   orchestrate business steps
-   call services
-   call adapters
-   record steps using workflow step helpers

Workflows should **NOT call external APIs directly**.

------------------------------------------------------------------------

# Adding a New Integration (External Provider)

Location:

    app/adapters/

Create a new adapter folder:

    app/adapters/<provider_name>/

Example:

    app/adapters/kraken/

Inside the folder:

    client.py

The client should:

-   wrap the external API
-   provide a stable interface for workflows
-   support mock mode for development

Example structure:

    app/adapters/kraken/client.py

Workflows should only interact with **adapter clients**, not external
APIs directly.

------------------------------------------------------------------------

# Adding Business Logic

Location:

    app/services/

Services contain reusable business logic shared by workflows.

Examples:

-   order lifecycle logic
-   step management helpers
-   shared processing logic

Services should:

-   be stateless when possible
-   avoid calling external APIs
-   avoid direct UI logic

------------------------------------------------------------------------

# Adding Domain Definitions

Location:

    app/domain/

Domain modules define:

-   currencies
-   blockchains
-   product constants
-   supported assets

Examples:

    SUPPORTED_CRYPTO_CURRENCIES
    SUPPORTED_FIAT_CURRENCIES
    SUPPORTED_BLOCKCHAINS

Domain modules should not depend on other layers.

------------------------------------------------------------------------

# Adding API Endpoints

Location:

    app/api/

Rules:

API routes should:

-   remain thin
-   call engine or services
-   never contain workflow logic

Example pattern:

    API → Engine → Workflow → Services → Adapters

------------------------------------------------------------------------

# Database Changes

Location:

    app/db/

Steps:

1.  Add new models
2.  Update schema
3.  Ensure models remain independent of API and UI layers

Database models should represent **domain entities**, not UI concepts.

------------------------------------------------------------------------

# UI Changes

Location:

    app/ui/

UI should:

-   call backend APIs
-   display workflows
-   visualise workflow progress
-   render results

UI must not contain business logic.

------------------------------------------------------------------------

# Code Principles

Follow these rules:

1.  **Adapters isolate external systems**
2.  **Workflows orchestrate business flows**
3.  **Services contain reusable logic**
4.  **API remains thin**
5.  **Domain contains business definitions**
6.  **Engine controls execution**

------------------------------------------------------------------------

# Testing

Location:

    app/tests/

Tests should cover:

-   workflow execution
-   adapter mock responses
-   step tracking
-   workflow validation

------------------------------------------------------------------------

# Architecture Reminder

System flow:

    UI
    ↓
    API
    ↓
    Engine
    ↓
    Workflows
    ↓
    Services
    ↓
    Adapters
    ↓
    External Providers

Maintaining this separation keeps the system:

-   maintainable
-   extensible
-   easy to scale

------------------------------------------------------------------------

# Questions

If you are unsure where new logic belongs:

-   Workflow orchestration → **workflows**
-   Reusable logic → **services**
-   External APIs → **adapters**
-   Business constants → **domain**
-   HTTP routes → **api**
