from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import re
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.ai.interpreter import interpret_request
from app.db.models import AssistantProposal


@dataclass(frozen=True)
class ProposalValidation:
    is_valid: bool
    errors: list[str]


class ProposalNotFoundError(KeyError):
    pass


class ProposalNotConfirmedError(RuntimeError):
    pass


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _iso_to_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _fingerprint(value: str, size: int = 12) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:size]


def _make_session_id(prompt: str) -> str:
    return f"chat_{_fingerprint(prompt.strip().lower(), size=10)}"


def _is_actionable_prompt(prompt: str) -> bool:
    text = prompt.strip()
    if len(text) < 3:
        return False
    return bool(re.search(r"[a-zA-Z]", text))


def validate_workflow_proposal(workflow: dict[str, Any]) -> ProposalValidation:
    errors: list[str] = []
    if not isinstance(workflow, dict):
        return ProposalValidation(is_valid=False, errors=["Workflow payload must be an object."])

    if not workflow.get("workflow_name"):
        errors.append("workflow_name is required.")

    steps = workflow.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("steps must contain at least one step.")
    else:
        for i, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                errors.append(f"step {i} must be an object.")
                continue
            if not step.get("id"):
                errors.append(f"step {i} is missing id.")
            if not step.get("type"):
                errors.append(f"step {i} is missing type.")

    return ProposalValidation(is_valid=(len(errors) == 0), errors=errors)


def _to_payload(row: AssistantProposal) -> dict[str, Any]:
    return {
        "proposal_id": row.proposal_id,
        "session_id": row.session_id,
        "message": row.message,
        "status": row.status,
        "created_at": row.created_at.isoformat(),
        "confirmed": row.confirmed,
        "confirmed_at": row.confirmed_at.isoformat() if row.confirmed_at else None,
        "executed_at": row.executed_at.isoformat() if row.executed_at else None,
        "workflow": row.workflow or {},
        "validation": row.validation or {"is_valid": True, "errors": []},
        "execution": row.execution,
    }


def create_proposal(*, db: Session, message: str, session_id: str | None = None) -> dict[str, Any]:
    prompt = message.strip()
    if not _is_actionable_prompt(prompt):
        raise ValueError("Prompt is not actionable. Provide a task-oriented request.")

    resolved_session_id = session_id or _make_session_id(prompt)
    workflow = interpret_request(prompt)
    validation = validate_workflow_proposal(workflow)
    if not validation.is_valid:
        raise RuntimeError("; ".join(validation.errors))

    proposal_id = f"prop_{_fingerprint(f'{resolved_session_id}:{prompt}')}"
    proposal = {
        "proposal_id": proposal_id,
        "session_id": resolved_session_id,
        "message": prompt,
        "status": "proposed",
        "created_at": _now_iso(),
        "confirmed": False,
        "confirmed_at": None,
        "executed_at": None,
        "workflow": workflow,
        "validation": {
            "is_valid": True,
            "errors": [],
        },
    }
    row = AssistantProposal(
        proposal_id=proposal_id,
        session_id=resolved_session_id,
        message=prompt,
        status="proposed",
        created_at=_iso_to_dt(proposal["created_at"]) or datetime.now(UTC),
        confirmed=False,
        confirmed_at=None,
        executed_at=None,
        workflow=workflow,
        validation=proposal["validation"],
        execution=None,
    )
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
        return _to_payload(row)
    except IntegrityError:
        db.rollback()
        existing = db.exec(select(AssistantProposal).where(AssistantProposal.proposal_id == proposal_id)).first()
        if existing:
            return _to_payload(existing)
        raise


def get_proposal(db: Session, proposal_id: str) -> dict[str, Any] | None:
    row = db.exec(select(AssistantProposal).where(AssistantProposal.proposal_id == proposal_id)).first()
    return _to_payload(row) if row else None


def confirm_proposal(db: Session, proposal_id: str) -> dict[str, Any]:
    row = db.exec(select(AssistantProposal).where(AssistantProposal.proposal_id == proposal_id)).first()
    if not row:
        raise ProposalNotFoundError(proposal_id)
    if row.confirmed:
        return _to_payload(row)

    row.confirmed = True
    row.confirmed_at = datetime.now(UTC)
    if row.status != "executed":
        row.status = "confirmed"
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_payload(row)


def execute_proposal(db: Session, proposal_id: str) -> dict[str, Any]:
    row = db.exec(select(AssistantProposal).where(AssistantProposal.proposal_id == proposal_id)).first()
    if not row:
        raise ProposalNotFoundError(proposal_id)
    if not row.confirmed:
        raise ProposalNotConfirmedError("Proposal must be confirmed before execution.")
    if row.status == "executed":
        return _to_payload(row)

    execution = {
        "run_id": f"run_{_fingerprint(proposal_id, size=10)}",
        "status": "accepted",
        "steps_count": len((row.workflow or {}).get("steps") or []),
        "accepted_at": _now_iso(),
    }
    row.executed_at = _iso_to_dt(execution["accepted_at"])
    row.status = "executed"
    row.execution = execution
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_payload(row)
