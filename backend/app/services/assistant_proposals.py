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


class ProposalInvalidStateError(RuntimeError):
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


def _as_step_links(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
        return out
    return []


def _extract_step_targets(step: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    for key in ("next", "next_step", "on_success", "on_failure"):
        targets.extend(_as_step_links(step.get(key)))
    targets.extend(_as_step_links(step.get("next_steps")))
    branches = step.get("branches")
    if isinstance(branches, dict):
        for value in branches.values():
            targets.extend(_as_step_links(value))
    return targets


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


def build_ui_handoff(db: Session, proposal_id: str) -> dict[str, Any]:
    row = db.exec(select(AssistantProposal).where(AssistantProposal.proposal_id == proposal_id)).first()
    if not row:
        raise ProposalNotFoundError(proposal_id)
    if not row.confirmed:
        raise ProposalInvalidStateError("Proposal must be confirmed before UI handoff.")

    workflow = row.workflow or {}
    steps = workflow.get("steps") or []

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    step_to_node: dict[str, str] = {}
    for idx, step in enumerate(steps, start=1):
        raw_step_id = str(step.get("id") or f"step_{idx}")
        node_id = f"node_{raw_step_id}"
        step_to_node[raw_step_id] = node_id
        step_type = str(step.get("type") or "engine.step")
        nodes.append(
            {
                "id": node_id,
                "type": step_type,
                "label": step_type.split(".")[-1].replace("_", " "),
                "provider": step_type.split(".")[0] if "." in step_type else "engine",
                "params": step.get("params") or {},
                "seq": idx,
            }
        )

    explicit_edges: list[tuple[str, str]] = []
    for idx, step in enumerate(steps, start=1):
        source_step_id = str(step.get("id") or f"step_{idx}")
        source_node_id = step_to_node[source_step_id]
        for target_step_id in _extract_step_targets(step):
            target_node_id = step_to_node.get(target_step_id)
            if target_node_id:
                explicit_edges.append((source_node_id, target_node_id))

    if explicit_edges:
        for idx, (src, dst) in enumerate(explicit_edges, start=1):
            edges.append({"id": f"edge_{idx}", "from": src, "to": dst})
    else:
        for idx in range(2, len(nodes) + 1):
            edges.append({"id": f"edge_{idx-1}", "from": nodes[idx - 2]["id"], "to": nodes[idx - 1]["id"]})

    return {
        "proposal_id": row.proposal_id,
        "session_id": row.session_id,
        "status": row.status,
        "workflow_name": str(workflow.get("workflow_name") or "assistant_workflow"),
        "nodes": nodes,
        "edges": edges,
        "source": "assistant_proposal",
    }
