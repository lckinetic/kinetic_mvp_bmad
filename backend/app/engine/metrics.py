from __future__ import annotations

from typing import Any, Dict
from sqlmodel import Session, select

from app.db.models import WorkflowRun, WorkflowStep


def compute_run_metrics(db: Session, run: WorkflowRun) -> Dict[str, Any]:
    steps = db.exec(
        select(WorkflowStep)
        .where(WorkflowStep.run_id == run.id)
        .order_by(WorkflowStep.seq.asc(), WorkflowStep.id.asc())
    ).all()

    total = len(steps)
    completed = sum(1 for s in steps if s.status == "completed")
    failed = sum(1 for s in steps if s.status == "failed")
    running = sum(1 for s in steps if s.status == "running")

    progress_pct = int((completed / total) * 100) if total else 0

    if total:
        started = [s.started_at for s in steps if s.started_at]
        start_ts = min(started) if started else (run.created_at or run.updated_at)
        end_candidates = [s.ended_at for s in steps if s.ended_at] or [run.updated_at or run.created_at]
        end_ts = max(end_candidates)
        duration_ms = int((end_ts - start_ts).total_seconds() * 1000) if (start_ts and end_ts) else 0
    else:
        duration_ms = 0

    return {
        "steps_total": total,
        "steps_completed": completed,
        "steps_failed": failed,
        "steps_running": running,
        "progress_pct": progress_pct,
        "duration_ms": duration_ms,
    }