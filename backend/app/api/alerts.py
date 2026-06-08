from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.workspaces import get_db
from app.services.alert_service import (
    ALERT_CATALOG,
    AlertNotFoundError,
    acknowledge_alert,
    get_alert,
    list_alerts,
    resolve_alert,
)
from app.services.workspace_service import WorkspaceNotFoundError

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/catalog", response_model=dict)
def alert_catalog_route():
    return {
        "items": [
            {"alert_type": alert_type, **definition}
            for alert_type, definition in ALERT_CATALOG.items()
        ]
    }


@router.get("", response_model=dict)
def list_alerts_route(
    db: Session = Depends(get_db),
    status: str | None = Query(default=None, max_length=40),
    include_acknowledged: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
):
    try:
        return {
            "items": list_alerts(
                db,
                status=status,
                include_acknowledged=include_acknowledged,
                limit=limit,
            )
        }
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc


@router.get("/{alert_id}", response_model=dict)
def get_alert_route(alert_id: int, db: Session = Depends(get_db)):
    try:
        return get_alert(db, alert_id=alert_id)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except AlertNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "ALERT_NOT_FOUND", "message": str(exc)},
        ) from exc


@router.post("/{alert_id}/acknowledge", response_model=dict)
def acknowledge_alert_route(alert_id: int, db: Session = Depends(get_db)):
    try:
        return acknowledge_alert(db, alert_id=alert_id)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except AlertNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "ALERT_NOT_FOUND", "message": str(exc)},
        ) from exc


@router.post("/{alert_id}/resolve", response_model=dict)
def resolve_alert_route(alert_id: int, db: Session = Depends(get_db)):
    try:
        return resolve_alert(db, alert_id=alert_id)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "WORKSPACE_NOT_FOUND", "message": str(exc)},
        ) from exc
    except AlertNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "ALERT_NOT_FOUND", "message": str(exc)},
        ) from exc
