from __future__ import annotations

from typing import Any, Dict, Optional
import inspect

from fastapi import HTTPException
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.db.models import WorkflowRun, utcnow

# Keep Banxa import for now (MVP), but runner is structured to support more adapters later
from app.services.banxa_client import BanxaClient

from app.workflows.registry import get_template
from app.workflows.validation import validate_template_input


def _call_template_function(fn, *, db: Session, settings: Settings, input_data: Dict[str, Any]):
    """
    Call a template function safely, supporting both:
      - old signature: fn(db=..., settings=..., banxa=..., input=...)
      - future signature: fn(db=..., settings=..., adapters={...}, input=...)
    """
    adapters = {
        "banxa": BanxaClient(mock_mode=settings.mock_mode),
        # future: "privy": PrivyClient(...),
        # future: "coinbase": CoinbaseClient(...),
    }

    sig = inspect.signature(fn)
    kwargs: Dict[str, Any] = {
        "db": db,
        "settings": settings,
        "input": input_data,
    }

    # Backwards compatible: if template expects banxa, provide it
    if "banxa" in sig.parameters:
        kwargs["banxa"] = adapters["banxa"]

    # Forward compatible: if template expects adapters, provide full dict
    if "adapters" in sig.parameters:
        kwargs["adapters"] = adapters

    return fn(**kwargs)


def run_template(
    *,
    db: Session,
    template_name: str,
    input_data: Dict[str, Any],
    settings: Optional[Settings] = None,
) -> WorkflowRun:
    """
    Execute a registered workflow template.

    Responsibilities:
      - Validate template exists (404 if unknown)
      - Create WorkflowRun row
      - Inject run_id into input + persist it
      - Validate input against template schema (400 on validation errors)
      - Execute template function directly (no HTTP calls)
      - Update run status/output/error
    """
    # 0) Validate template exists (unknown template => 404, do not create a run)
    try:
        t = get_template(template_name)
    except KeyError:
        raise HTTPException(status_code=404, detail="Template not found")

    settings = settings or get_settings()

    # 1) Create run (persist immediately so we have an ID for logging)
    run = WorkflowRun(
        template_name=template_name,
        status="running",
        input=input_data or {},
        output={},
        updated_at=utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)  # run.id now exists

    # 2) Inject run_id into input and persist it (needed for step logging + idempotency)
    run_input = dict(run.input or {})
    run_input["run_id"] = run.id
    run.input = run_input
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        schema = t.get("input_schema", [])
        validated_input = validate_template_input(run_input, schema)

        # ensure run_id always survives validation
        validated_input["run_id"] = run.id

        fn = t["function"]
        output = _call_template_function(
            fn,
            db=db,
            settings=settings,
            input_data=validated_input,
        )

        run.status = "completed"
        run.output = output or {}
        run.updated_at = utcnow()

    except HTTPException as e:
        # Validation or template-thrown HTTPException should propagate properly (400/404 etc)
        run.status = "failed"
        run.error = str(e.detail)
        run.updated_at = utcnow()

        db.add(run)
        db.commit()
        db.refresh(run)
        raise

    except Exception as e:
        run.status = "failed"
        run.error = f"{type(e).__name__}: {e}"
        run.updated_at = utcnow()

        db.add(run)
        db.commit()
        db.refresh(run)

    else:
        db.add(run)
        db.commit()
        db.refresh(run)

    return run