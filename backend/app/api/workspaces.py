from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.db.engine import get_engine
from app.services.workspace_service import (
    WorkspaceNotFoundError,
    create_workspace,
    get_current_workspace,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def get_db(settings: Settings = Depends(get_settings)) -> Generator[Session, None, None]:
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    created_at: str


def _to_response(row) -> WorkspaceResponse:
    return WorkspaceResponse(
        id=row.id,
        name=row.name,
        created_at=row.created_at.isoformat(),
    )


@router.post("", response_model=WorkspaceResponse)
def create_workspace_route(body: WorkspaceCreateRequest, db: Session = Depends(get_db)):
    try:
        row = create_workspace(db, name=body.name)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "WORKSPACE_INVALID",
                "message": str(exc),
            },
        ) from exc
    return _to_response(row)


@router.get("/current", response_model=WorkspaceResponse)
def get_current_workspace_route(db: Session = Depends(get_db)):
    try:
        row = get_current_workspace(db)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "WORKSPACE_NOT_FOUND",
                "message": str(exc),
            },
        ) from exc
    return _to_response(row)
