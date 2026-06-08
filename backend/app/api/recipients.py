from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.workspaces import get_db
from app.services.recipient_service import (
    RecipientAlreadyExistsError,
    RecipientNotFoundError,
    RecipientValidationError,
    SUPPORTED_NETWORKS,
    create_recipient,
    deactivate_recipient,
    get_recipient,
    list_recipients,
    recipient_has_active_workflow_links,
    update_recipient,
)
from app.services.workspace_service import WorkspaceNotFoundError

router = APIRouter(prefix="/recipients", tags=["recipients"])


class RecipientCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    wallet_address: str = Field(min_length=4, max_length=200)
    network: str = Field(min_length=2, max_length=40)
    notes: str | None = Field(default=None, max_length=500)


class RecipientUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    wallet_address: str | None = Field(default=None, max_length=200)
    network: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=500)


def _workspace_missing(exc: WorkspaceNotFoundError) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
    )


@router.get("/networks", response_model=dict)
def list_networks_route():
    return {
        "items": [
            {"id": network_id, "label": label}
            for network_id, label in SUPPORTED_NETWORKS.items()
        ]
    }


@router.get("", response_model=dict)
def list_recipients_route(
    db: Session = Depends(get_db),
    search: str | None = Query(default=None, max_length=120),
    include_inactive: bool = Query(default=False),
):
    try:
        items = list_recipients(db, search=search, include_inactive=include_inactive)
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    return {"items": items}


@router.post("", response_model=dict)
def create_recipient_route(body: RecipientCreateRequest, db: Session = Depends(get_db)):
    try:
        return create_recipient(
            db,
            name=body.name,
            wallet_address=body.wallet_address,
            network=body.network,
            notes=body.notes,
        )
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except RecipientAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "RECIPIENT_ALREADY_EXISTS", "message": str(exc)},
        ) from exc
    except RecipientValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "RECIPIENT_INVALID", "message": str(exc)},
        ) from exc


@router.get("/{recipient_id}", response_model=dict)
def get_recipient_route(recipient_id: int, db: Session = Depends(get_db)):
    try:
        return get_recipient(db, recipient_id=recipient_id)
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except RecipientNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "RECIPIENT_NOT_FOUND", "message": str(exc)},
        ) from exc


@router.patch("/{recipient_id}", response_model=dict)
def update_recipient_route(
    recipient_id: int,
    body: RecipientUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        return update_recipient(
            db,
            recipient_id=recipient_id,
            name=body.name,
            wallet_address=body.wallet_address,
            network=body.network,
            notes=body.notes,
        )
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except RecipientNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "RECIPIENT_NOT_FOUND", "message": str(exc)},
        ) from exc
    except RecipientAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "RECIPIENT_ALREADY_EXISTS", "message": str(exc)},
        ) from exc
    except RecipientValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "RECIPIENT_INVALID", "message": str(exc)},
        ) from exc


@router.post("/{recipient_id}/deactivate", response_model=dict)
def deactivate_recipient_route(recipient_id: int, db: Session = Depends(get_db)):
    try:
        payload = deactivate_recipient(db, recipient_id=recipient_id)
        if recipient_has_active_workflow_links(db, recipient_id=recipient_id):
            payload["workflow_warning"] = (
                "This recipient is linked to an active payout workflow. "
                "Deactivate or update the workflow before removing this destination."
            )
        return payload
    except WorkspaceNotFoundError as exc:
        raise _workspace_missing(exc) from exc
    except RecipientNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "RECIPIENT_NOT_FOUND", "message": str(exc)},
        ) from exc
