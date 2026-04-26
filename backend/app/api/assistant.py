from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.db.engine import get_engine
from app.services.assistant_proposals import (
    ProposalNotConfirmedError,
    ProposalNotFoundError,
    confirm_proposal,
    create_proposal,
    execute_proposal,
    get_proposal,
)


router = APIRouter(prefix="/assistant", tags=["assistant"])


def get_db(settings: Settings = Depends(get_settings)):
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session


class AssistantProposalRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Natural-language request from the user.")
    session_id: str | None = Field(
        default=None,
        description="Optional stable chat session id. If omitted, one is derived from the prompt.",
    )


class AssistantProposalValidation(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)


class AssistantProposalResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"title": "AssistantProposal"})

    proposal_id: str
    session_id: str
    message: str
    status: str
    created_at: str
    confirmed: bool = False
    confirmed_at: str | None = None
    executed_at: str | None = None
    workflow: dict[str, Any]
    validation: AssistantProposalValidation
    execution: dict[str, Any] | None = None


@router.post(
    "/proposals",
    response_model=AssistantProposalResponse,
    summary="Create assistant workflow proposal",
    response_description="Structured workflow proposal from a chat prompt",
)
def create_assistant_proposal(req: AssistantProposalRequest, db: Session = Depends(get_db)):
    try:
        proposal = create_proposal(db=db, message=req.message, session_id=req.session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PROMPT",
                "message": "Prompt could not be converted into a workflow proposal",
                "details": {"reason": str(exc)},
            },
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PROPOSAL",
                "message": "Generated proposal failed validation",
                "details": {"reason": str(exc)},
            },
        )
    return AssistantProposalResponse.model_validate(proposal)


@router.get(
    "/proposals/{proposal_id}",
    response_model=AssistantProposalResponse,
    summary="Get assistant proposal by id",
    response_description="Previously generated workflow proposal",
)
def get_assistant_proposal(proposal_id: str, db: Session = Depends(get_db)):
    proposal = get_proposal(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Assistant proposal not found")
    return AssistantProposalResponse.model_validate(proposal)


@router.post(
    "/proposals/{proposal_id}/confirm",
    response_model=AssistantProposalResponse,
    summary="Confirm assistant proposal before execution",
    response_description="Proposal updated to confirmed state",
)
def confirm_assistant_proposal(proposal_id: str, db: Session = Depends(get_db)):
    try:
        proposal = confirm_proposal(db, proposal_id)
    except ProposalNotFoundError:
        raise HTTPException(status_code=404, detail="Assistant proposal not found")
    return AssistantProposalResponse.model_validate(proposal)


@router.post(
    "/proposals/{proposal_id}/execute",
    response_model=AssistantProposalResponse,
    summary="Execute assistant proposal after confirmation",
    response_description="Accepted execution artifact for confirmed proposal",
)
def execute_assistant_proposal(proposal_id: str, db: Session = Depends(get_db)):
    try:
        proposal = execute_proposal(db, proposal_id)
    except ProposalNotFoundError:
        raise HTTPException(status_code=404, detail="Assistant proposal not found")
    except ProposalNotConfirmedError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFIRMATION_REQUIRED",
                "message": "Proposal must be confirmed before execution",
                "details": {"reason": str(exc)},
            },
        )
    return AssistantProposalResponse.model_validate(proposal)
