from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.workspaces import get_db
from app.services.activity_service import (
    ACTIVITY_EVENT_TYPES,
    ActivityNotFoundError,
    get_activity_event,
    list_activity_events,
)
from app.services.workspace_service import WorkspaceNotFoundError

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/event-types", response_model=dict)
def list_event_types_route():
    return {
        "items": [
            {"id": event_id, "label": label}
            for event_id, label in ACTIVITY_EVENT_TYPES.items()
        ]
    }


@router.get("", response_model=dict)
def list_activity_route(
    db: Session = Depends(get_db),
    event_type: str | None = Query(default=None, max_length=80),
    status: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=50, ge=1, le=200),
):
    try:
        return {
            "items": list_activity_events(
                db,
                event_type=event_type,
                status=status,
                limit=limit,
            )
        }
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc


@router.get("/{activity_id}", response_model=dict)
def get_activity_route(activity_id: int, db: Session = Depends(get_db)):
    try:
        return get_activity_event(db, activity_id=activity_id)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except ActivityNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "ACTIVITY_NOT_FOUND", "message": str(exc)},
        ) from exc
