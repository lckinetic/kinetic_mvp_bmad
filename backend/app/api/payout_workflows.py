from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.workspaces import get_db
from app.core.config import Settings, get_settings
from app.services.payout_workflow_service import (
    PayoutWorkflowDisabledError,
    PayoutWorkflowGuardrailError,
    PayoutWorkflowNotFoundError,
    PayoutWorkflowValidationError,
    RecipientInactiveError,
    create_payout_workflow,
    get_payout_workflow,
    list_payout_workflows,
    run_payout_workflow,
    set_payout_workflow_enabled,
    update_payout_workflow,
)
from app.services.recipient_service import RecipientNotFoundError
from app.services.treasury_service import InsufficientBalanceError, TreasuryNotFoundError
from app.services.workspace_service import WorkspaceNotFoundError, get_current_workspace

router = APIRouter(prefix="/payout-workflows", tags=["payout-workflows"])


class PayoutWorkflowCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    recipient_id: int
    amount: float = Field(gt=0)
    asset: str = Field(default="USDC", max_length=12)
    schedule_cadence: str = Field(default="manual", max_length=20)
    schedule_day: str | None = Field(default=None, max_length=20)


class PayoutWorkflowUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    recipient_id: int | None = None
    amount: float | None = Field(default=None, gt=0)
    schedule_cadence: str | None = Field(default=None, max_length=20)
    schedule_day: str | None = Field(default=None, max_length=20)


def _workspace_missing(exc: WorkspaceNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)})


@router.get("", response_model=dict)
def list_payout_workflows_route(db: Session = Depends(get_db)):
    try:
        return {"items": list_payout_workflows(db)}
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc


@router.post("", response_model=dict)
def create_payout_workflow_route(body: PayoutWorkflowCreateRequest, db: Session = Depends(get_db)):
    try:
        return create_payout_workflow(
            db,
            name=body.name,
            recipient_id=body.recipient_id,
            amount=body.amount,
            asset=body.asset,
            schedule_cadence=body.schedule_cadence,
            schedule_day=body.schedule_day,
        )
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except RecipientNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "RECIPIENT_NOT_FOUND", "message": str(exc)}) from exc
    except PayoutWorkflowGuardrailError as exc:
        raise HTTPException(status_code=409, detail={"code": "PAYOUT_WORKFLOW_GUARD", "message": str(exc)}) from exc
    except PayoutWorkflowValidationError as exc:
        raise HTTPException(status_code=400, detail={"code": "PAYOUT_WORKFLOW_INVALID", "message": str(exc)}) from exc


@router.get("/{workflow_id}", response_model=dict)
def get_payout_workflow_route(workflow_id: int, db: Session = Depends(get_db)):
    try:
        return get_payout_workflow(db, workflow_id=workflow_id)
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except PayoutWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "PAYOUT_WORKFLOW_NOT_FOUND", "message": str(exc)}) from exc


@router.patch("/{workflow_id}", response_model=dict)
def update_payout_workflow_route(
    workflow_id: int,
    body: PayoutWorkflowUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        return update_payout_workflow(
            db,
            workflow_id=workflow_id,
            name=body.name,
            recipient_id=body.recipient_id,
            amount=body.amount,
            schedule_cadence=body.schedule_cadence,
            schedule_day=body.schedule_day,
        )
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except PayoutWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "PAYOUT_WORKFLOW_NOT_FOUND", "message": str(exc)}) from exc
    except RecipientNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "RECIPIENT_NOT_FOUND", "message": str(exc)}) from exc
    except PayoutWorkflowGuardrailError as exc:
        raise HTTPException(status_code=409, detail={"code": "PAYOUT_WORKFLOW_GUARD", "message": str(exc)}) from exc
    except PayoutWorkflowValidationError as exc:
        raise HTTPException(status_code=400, detail={"code": "PAYOUT_WORKFLOW_INVALID", "message": str(exc)}) from exc


@router.post("/{workflow_id}/enable", response_model=dict)
def enable_payout_workflow_route(workflow_id: int, db: Session = Depends(get_db)):
    try:
        return set_payout_workflow_enabled(db, workflow_id=workflow_id, enabled=True)
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except PayoutWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "PAYOUT_WORKFLOW_NOT_FOUND", "message": str(exc)}) from exc


@router.post("/{workflow_id}/disable", response_model=dict)
def disable_payout_workflow_route(workflow_id: int, db: Session = Depends(get_db)):
    try:
        return set_payout_workflow_enabled(db, workflow_id=workflow_id, enabled=False)
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except PayoutWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "PAYOUT_WORKFLOW_NOT_FOUND", "message": str(exc)}) from exc


@router.post("/{workflow_id}/run", response_model=dict)
def run_payout_workflow_route(
    workflow_id: int,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    try:
        return run_payout_workflow(db, settings=settings, workflow_id=workflow_id)
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except PayoutWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "PAYOUT_WORKFLOW_NOT_FOUND", "message": str(exc)}) from exc
    except PayoutWorkflowDisabledError as exc:
        workspace = get_current_workspace(db)
        from app.services.activity_service import ingest_blocked_payout_activity
        from app.services.alert_service import create_workflow_disabled_alert

        create_workflow_disabled_alert(db, workspace_id=workspace.id, workflow_id=workflow_id)
        ingest_blocked_payout_activity(
            db,
            workspace_id=workspace.id,
            workflow_id=workflow_id,
            block_reason="workflow_disabled",
            title="Payout workflow is paused",
            summary=str(exc),
        )
        raise HTTPException(status_code=409, detail={"code": "PAYOUT_WORKFLOW_DISABLED", "message": str(exc)}) from exc
    except RecipientInactiveError as exc:
        workspace = get_current_workspace(db)
        from app.services.activity_service import ingest_blocked_payout_activity
        from app.services.alert_service import create_recipient_invalid_alert

        create_recipient_invalid_alert(
            db,
            workspace_id=workspace.id,
            workflow_id=workflow_id,
            recipient_id=exc.recipient_id,
        )
        ingest_blocked_payout_activity(
            db,
            workspace_id=workspace.id,
            workflow_id=workflow_id,
            block_reason="recipient_inactive",
            title="Payout blocked — recipient inactive",
            summary=str(exc),
            recipient_id=exc.recipient_id,
        )
        raise HTTPException(
            status_code=409,
            detail={"code": "RECIPIENT_INACTIVE", "message": str(exc), "details": {"recipient_id": exc.recipient_id}},
        ) from exc
    except PayoutWorkflowGuardrailError as exc:
        raise HTTPException(status_code=409, detail={"code": "PAYOUT_WORKFLOW_GUARD", "message": str(exc)}) from exc
    except RecipientNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "RECIPIENT_NOT_FOUND", "message": str(exc)}) from exc
    except TreasuryNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "TREASURY_NOT_FOUND", "message": str(exc)}) from exc
    except InsufficientBalanceError as exc:
        workspace = get_current_workspace(db)
        from app.services.activity_service import ingest_blocked_payout_activity
        from app.services.alert_service import create_insufficient_balance_alert

        create_insufficient_balance_alert(
            db,
            workspace_id=workspace.id,
            workflow_id=workflow_id,
            balance=exc.balance,
            required=exc.required,
            shortfall=exc.shortfall,
        )
        ingest_blocked_payout_activity(
            db,
            workspace_id=workspace.id,
            workflow_id=workflow_id,
            block_reason="insufficient_balance",
            title="Payout blocked — insufficient treasury balance",
            summary=str(exc),
        )
        raise HTTPException(
            status_code=409,
            detail={
                "code": "INSUFFICIENT_BALANCE",
                "message": str(exc),
                "details": {
                    "balance": exc.balance,
                    "required": exc.required,
                    "shortfall": exc.shortfall,
                    "asset": "USDC",
                },
            },
        ) from exc
