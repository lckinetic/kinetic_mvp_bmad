from __future__ import annotations

from sqlmodel import Session, select

from app.db.models import Workspace


class WorkspaceNotFoundError(LookupError):
    pass


def _normalize_name(name: str) -> str:
    return (name or "").strip()


def create_workspace(db: Session, *, name: str) -> Workspace:
    normalized = _normalize_name(name)
    if not normalized:
        raise ValueError("Workspace name is required.")
    if len(normalized) > 120:
        raise ValueError("Workspace name must be 120 characters or fewer.")

    row = Workspace(name=normalized)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_current_workspace(db: Session) -> Workspace:
    row = db.exec(select(Workspace).order_by(Workspace.id.desc())).first()
    if not row:
        raise WorkspaceNotFoundError("No workspace exists yet.")
    return row
