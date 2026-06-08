from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.workspaces import get_db
from app.core.config import Settings, get_settings
from app.services.treasury_service import (
    InsufficientBalanceError,
    MockOnlyOperationError,
    TreasuryAlreadyExistsError,
    TreasuryNotFoundError,
    TreasuryProviderNotConfiguredError,
    check_sufficient_balance,
    create_treasury,
    get_current_treasury,
    list_transfers,
    serialize_transfer,
    simulate_deposit,
    simulate_failed_outbound_transfer,
)
from app.services.workspace_service import WorkspaceNotFoundError, get_current_workspace

router = APIRouter(prefix="/treasury", tags=["treasury"])


class TreasuryCreateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=120)


class BalanceCheckRequest(BaseModel):
    amount: float = Field(gt=0)


class SimulateDepositRequest(BaseModel):
    amount: float = Field(default=1000.0, gt=0)
    counterparty_label: str | None = Field(default=None, max_length=120)


class SimulateFailedPayoutRequest(BaseModel):
    amount: float = Field(default=50.0, gt=0)
    counterparty_label: str | None = Field(default=None, max_length=120)


@router.post("", response_model=dict)
def create_treasury_route(
    body: TreasuryCreateRequest | None = None,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    try:
        get_current_workspace(db)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc

    try:
        return create_treasury(db, settings=settings, name=body.name if body else None)
    except TreasuryAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "TREASURY_ALREADY_EXISTS", "message": str(exc)},
        ) from exc
    except TreasuryProviderNotConfiguredError as exc:
        workspace = get_current_workspace(db)
        from app.services.alert_service import create_provider_unavailable_alert

        create_provider_unavailable_alert(db, workspace_id=workspace.id, message=str(exc))
        raise HTTPException(
            status_code=501,
            detail={"code": "TREASURY_PROVIDER_NOT_CONFIGURED", "message": str(exc)},
        ) from exc


@router.get("", response_model=dict)
def get_treasury_route(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    try:
        return get_current_treasury(db, settings=settings)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except TreasuryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "TREASURY_NOT_FOUND", "message": str(exc)},
        ) from exc


@router.get("/transfers", response_model=dict)
def list_transfers_route(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    try:
        view = get_current_treasury(db, settings=settings)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except TreasuryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "TREASURY_NOT_FOUND", "message": str(exc)},
        ) from exc

    rows = list_transfers(db, treasury_id=view["id"])
    return {"items": [serialize_transfer(row) for row in rows]}


@router.post("/balance/check", response_model=dict)
def balance_check_route(
    body: BalanceCheckRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    try:
        view = get_current_treasury(db, settings=settings)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except TreasuryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "TREASURY_NOT_FOUND", "message": str(exc)},
        ) from exc

    try:
        return check_sufficient_balance(db, treasury_id=view["id"], amount=body.amount)
    except InsufficientBalanceError as exc:
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
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "TREASURY_INVALID", "message": str(exc)},
        ) from exc


@router.post("/transfers/simulate-deposit", response_model=dict)
def simulate_deposit_route(
    body: SimulateDepositRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    try:
        return simulate_deposit(
            db,
            settings=settings,
            amount=body.amount,
            counterparty_label=body.counterparty_label or "Demo deposit",
        )
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except TreasuryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "TREASURY_NOT_FOUND", "message": str(exc)},
        ) from exc
    except MockOnlyOperationError as exc:
        raise HTTPException(
            status_code=403,
            detail={"code": "MOCK_ONLY", "message": str(exc)},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "TREASURY_INVALID", "message": str(exc)},
        ) from exc


@router.post("/transfers/simulate-failed-payout", response_model=dict)
def simulate_failed_payout_route(
    body: SimulateFailedPayoutRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    try:
        return simulate_failed_outbound_transfer(
            db,
            settings=settings,
            amount=body.amount,
            counterparty_label=body.counterparty_label or "Demo failed payout",
        )
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except TreasuryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "TREASURY_NOT_FOUND", "message": str(exc)},
        ) from exc
    except MockOnlyOperationError as exc:
        raise HTTPException(
            status_code=403,
            detail={"code": "MOCK_ONLY", "message": str(exc)},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "TREASURY_INVALID", "message": str(exc)},
        ) from exc
