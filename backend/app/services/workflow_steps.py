from __future__ import annotations

from typing import Any, Dict, Optional
from sqlmodel import Session, select

from app.db.models import WorkflowStep, utcnow


def step_start(
    *,
    db: Session,
    run_id: int,
    seq: int,
    step_name: str,
    data: Optional[Dict[str, Any]] = None,
) -> WorkflowStep:
    step = WorkflowStep(
        run_id=run_id,
        seq=seq,
        step_name=step_name,
        status="running",
        data=data or {},
        started_at=utcnow(),
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def step_complete(
    *,
    db: Session,
    step_id: int,
    data: Optional[Dict[str, Any]] = None,
) -> WorkflowStep:
    step = db.get(WorkflowStep, step_id)
    if not step:
        raise ValueError("WorkflowStep not found")
    step.status = "completed"
    if data:
        step.data = {**(step.data or {}), **data}
    step.ended_at = utcnow()
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def step_fail(
    *,
    db: Session,
    step_id: int,
    error: str,
    data: Optional[Dict[str, Any]] = None,
) -> WorkflowStep:
    step = db.get(WorkflowStep, step_id)
    if not step:
        raise ValueError("WorkflowStep not found")
    step.status = "failed"
    step.error = error
    if data:
        step.data = {**(step.data or {}), **data}
    step.ended_at = utcnow()
    db.add(step)
    db.commit()
    db.refresh(step)
    return step
