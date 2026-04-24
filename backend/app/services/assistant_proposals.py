from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import re
from threading import Lock
from typing import Any

from app.ai.interpreter import interpret_request


_PROPOSALS: dict[str, dict[str, Any]] = {}
_STORE_LOCK = Lock()


@dataclass(frozen=True)
class ProposalValidation:
    is_valid: bool
    errors: list[str]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


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


def create_proposal(*, message: str, session_id: str | None = None) -> dict[str, Any]:
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
        "workflow": workflow,
        "validation": {
            "is_valid": True,
            "errors": [],
        },
    }

    with _STORE_LOCK:
        _PROPOSALS[proposal_id] = proposal
    return proposal


def get_proposal(proposal_id: str) -> dict[str, Any] | None:
    with _STORE_LOCK:
        proposal = _PROPOSALS.get(proposal_id)
    return proposal
