from __future__ import annotations

from typing import Any, Dict, Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.config import get_settings, Settings
from app.db.engine import get_engine

from app.workflows.registry import list_templates, get_template
from app.db.models import WorkflowRun, WorkflowStep
import app.workflows  # noqa: F401  (ensures templates register)

from app.engine.metrics import compute_run_metrics
from app.engine.runner import run_template

router = APIRouter(prefix="/workflows", tags=["workflows"])


def get_db(settings: Settings = Depends(get_settings)):
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session


class RunWorkflowRequest(BaseModel):
    input: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{
            "fiat_amount": 1000,
            "fiat_currency": "GBP",
            "crypto_currency": "USDC",
            "wallet_address": "0xDEMO",
            "blockchain": "ethereum",
            "user_email": "demo@example.com",
            "crypto_amount": 100,
            "destination_reference": "demo-bank-001",
            "onramp_client_reference": "treasury-demo-on-001",
            "offramp_client_reference": "treasury-demo-off-001"
        }]
    )


class WorkflowRunResponse(BaseModel):
    id: int
    template_name: str
    status: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


def _to_response(db: Session, r: WorkflowRun) -> WorkflowRunResponse:
    metrics = compute_run_metrics(db, r)
    return WorkflowRunResponse(
        id=r.id,
        template_name=r.template_name,
        status=r.status,
        input=r.input or {},
        output=r.output or {},
        error=r.error,
        created_at=r.created_at.isoformat() if r.created_at else None,
        updated_at=r.updated_at.isoformat() if r.updated_at else None,
        metrics=metrics,
    )

@router.post("/run/{template_name}", response_model=WorkflowRunResponse)
def run_workflow(
    template_name: str,
    req: RunWorkflowRequest,
    db: Session = Depends(get_db),
):
    run = run_template(
        db=db,
        template_name=template_name,
        input_data=req.input or {},
    )
    return _to_response(db, run)


@router.get("/runs", response_model=List[WorkflowRunResponse])
def list_runs(
    limit: int = 20,
    template_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 200))
    stmt = select(WorkflowRun).order_by(WorkflowRun.id.desc()).limit(limit)
    if template_name:
        stmt = select(WorkflowRun).where(WorkflowRun.template_name == template_name).order_by(WorkflowRun.id.desc()).limit(limit)

    rows = db.exec(stmt).all()
    return [_to_response(db, r) for r in rows]


@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    run = db.get(WorkflowRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return _to_response(db, run)



@router.get("/templates")
def get_templates():
    templates = list_templates()
    return [
        {
            "name": t["name"],
            "version": t.get("version", "1.0"),
            "display_name": t["display_name"],
            "description": t["description"],
            "category": t["category"],
            "input_schema": t.get("input_schema", []),
            "business_summary": t.get("business_summary", ""),
            "business_steps": t.get("business_steps", []),
            "step_outline": t.get("step_outline", []),
        }
        for t in templates
    ]
    
@router.get("/templates/{template_name}")
def get_template_details(template_name: str):
    try:
        t = get_template(template_name)
    except KeyError:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "name": t["name"],
        "version": t.get("version", "1.0"),
        "display_name": t["display_name"],
        "description": t["description"],
        "category": t["category"],
        "input_schema": t.get("input_schema", []),
        "business_summary": t.get("business_summary", ""),
        "business_steps": t.get("business_steps", []),
        "step_outline": t.get("step_outline", []),
        "step_labels": t.get("step_labels", {}),
    }

@router.get("/runs/{run_id}/steps")
def list_run_steps(run_id: int, db: Session = Depends(get_db)):
    steps = db.exec(
        select(WorkflowStep)
        .where(WorkflowStep.run_id == run_id)
        .order_by(WorkflowStep.seq.asc(), WorkflowStep.id.asc())
    ).all()

    out = []
    for s in steps:
        duration_ms = None
        if s.started_at and s.ended_at:
            duration_ms = int((s.ended_at - s.started_at).total_seconds() * 1000)

        out.append(
            {
                "id": s.id,
                "run_id": s.run_id,
                "seq": s.seq,
                "step_name": s.step_name,
                "status": s.status,
                "data": s.data or {},
                "error": s.error,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "duration_ms": duration_ms,
            }
        )
    return out