from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.services.assistant_proposals import create_proposal, get_proposal


router = APIRouter(prefix="/assistant", tags=["assistant"])


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
    workflow: dict[str, Any]
    validation: AssistantProposalValidation


@router.post(
    "/proposals",
    response_model=AssistantProposalResponse,
    summary="Create assistant workflow proposal",
    response_description="Structured workflow proposal from a chat prompt",
)
def create_assistant_proposal(req: AssistantProposalRequest):
    try:
        proposal = create_proposal(message=req.message, session_id=req.session_id)
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
def get_assistant_proposal(proposal_id: str):
    proposal = get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Assistant proposal not found")
    return AssistantProposalResponse.model_validate(proposal)
