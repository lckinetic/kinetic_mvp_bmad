from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.core.secrets_redact import redact_secrets_in_text
from app.db.engine import get_engine
from app.db.models import WorkflowRun, utcnow

from app.ai.service import get_ai_service
from app.engine.graph_runner import run_graph
from app.engine.metrics import compute_run_metrics

from app.services.banxa_client import BanxaClient
from app.services.coinbase_client import CoinbaseClient
from app.services.privy_client import PrivyClient


router = APIRouter(prefix="/ai", tags=["ai"])


def get_db(settings: Settings = Depends(get_settings)):
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session


class InterpretRequest(BaseModel):
    message: str = Field(..., min_length=1)


class RunGraphRequest(BaseModel):
    workflow: Dict[str, Any]


@router.post("/interpret")
def interpret(req: InterpretRequest, settings: Settings = Depends(get_settings)):
    try:
        ai_service = get_ai_service(settings)
        result = ai_service.generate_workflow(req.message)
    except Exception as exc:
        reason = redact_secrets_in_text(f"{type(exc).__name__}: {exc}", settings)
        raise HTTPException(
            status_code=502,
            detail={
                "code": "AI_INTERPRET_FAILED",
                "message": "AI workflow interpretation failed",
                "details": {"reason": reason},
            },
        )
    return {
        **result.workflow,
        "meta": {
            "source": result.source,
            "provider": result.provider,
            "model": result.model,
            "mock_mode": settings.ai_mock_mode,
        },
    }


@router.get("/capabilities")
def capabilities(settings: Settings = Depends(get_settings)):
    return {
        "mock_mode": settings.ai_mock_mode,
        "provider": "mock" if settings.ai_mock_mode else settings.ai_provider,
        "model": "rule-based" if settings.ai_mock_mode else settings.ai_model,
    }


@router.get("/config-status")
def config_status(settings: Settings = Depends(get_settings)):
    """Non-secret AI runtime diagnostics for pre-demo verification."""
    return {
        "mock_mode": settings.ai_mock_mode,
        "provider": "mock" if settings.ai_mock_mode else settings.ai_provider,
        "model": "rule-based" if settings.ai_mock_mode else settings.ai_model,
        "openai_api_key_configured": bool(settings.openai_api_key),
        "openai_base_url": settings.openai_base_url,
        "ai_timeout_seconds": settings.ai_timeout_seconds,
    }


@router.post("/run-graph")
def run_generated_graph(
    req: RunGraphRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    run = WorkflowRun(
        template_name="generated_workflow",
        status="running",
        input=req.workflow,
        output={},
        updated_at=utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    adapters = {
        "banxa": BanxaClient(mock_mode=settings.mock_mode),
        "privy": PrivyClient(mock_mode=settings.mock_mode),
        "coinbase": CoinbaseClient(mock_mode=settings.mock_mode),
    }

    try:
        output = run_graph(
            db=db,
            settings=settings,
            adapters=adapters,
            run_id=run.id,
            workflow=req.workflow,
        )
        run.status = "completed"
        run.output = output
        run.updated_at = utcnow()

    except Exception as e:
        run.status = "failed"
        run.error = redact_secrets_in_text(f"{type(e).__name__}: {e}", settings)
        run.updated_at = utcnow()

    db.add(run)
    db.commit()
    db.refresh(run)

    return {
        "id": run.id,
        "template_name": run.template_name,
        "status": run.status,
        "input": run.input or {},
        "output": run.output or {},
        "error": run.error,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "updated_at": run.updated_at.isoformat() if run.updated_at else None,
        "metrics": compute_run_metrics(db, run),
    }