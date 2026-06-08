from __future__ import annotations

import re
from typing import Any

from sqlmodel import Session, select

from app.db.models import Recipient, utcnow
from app.services.workspace_service import get_current_workspace

EVM_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")

SUPPORTED_NETWORKS: dict[str, str] = {
    "base": "Base",
    "ethereum": "Ethereum",
    "polygon": "Polygon",
}


class RecipientNotFoundError(LookupError):
    pass


class RecipientAlreadyExistsError(ValueError):
    pass


class RecipientValidationError(ValueError):
    pass


def _normalize_name(name: str) -> str:
    return (name or "").strip()


def _normalize_address(address: str) -> str:
    return (address or "").strip()


def _normalize_notes(notes: str | None) -> str | None:
    if notes is None:
        return None
    trimmed = notes.strip()
    return trimmed or None


def validate_recipient_fields(
    *,
    name: str,
    wallet_address: str,
    network: str,
    notes: str | None = None,
) -> dict[str, str | None]:
    normalized_name = _normalize_name(name)
    if not normalized_name:
        raise RecipientValidationError("Recipient name is required.")
    if len(normalized_name) > 120:
        raise RecipientValidationError("Recipient name must be 120 characters or fewer.")

    normalized_network = (network or "").strip().lower()
    if normalized_network not in SUPPORTED_NETWORKS:
        supported = ", ".join(SUPPORTED_NETWORKS[network_key] for network_key in SUPPORTED_NETWORKS)
        raise RecipientValidationError(f"Network must be one of: {supported}.")

    normalized_address = _normalize_address(wallet_address).lower()
    if not EVM_ADDRESS_RE.fullmatch(normalized_address):
        raise RecipientValidationError(
            "Wallet address must be a valid EVM address (0x followed by 40 hexadecimal characters)."
        )

    normalized_notes = _normalize_notes(notes)
    if normalized_notes and len(normalized_notes) > 500:
        raise RecipientValidationError("Notes must be 500 characters or fewer.")

    return {
        "name": normalized_name,
        "wallet_address": normalized_address,
        "network": normalized_network,
        "notes": normalized_notes,
    }


def serialize_recipient(row: Recipient) -> dict[str, Any]:
    return {
        "id": row.id,
        "workspace_id": row.workspace_id,
        "name": row.name,
        "wallet_address": row.wallet_address,
        "wallet_address_short": _short_address(row.wallet_address),
        "network": row.network,
        "network_label": SUPPORTED_NETWORKS.get(row.network, row.network),
        "notes": row.notes,
        "status": row.status,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
    }


def _short_address(address: str) -> str:
    if len(address) < 12:
        return address
    return f"{address[:6]}…{address[-4:]}"


def list_recipients(
    db: Session,
    *,
    search: str | None = None,
    include_inactive: bool = False,
    status: str | None = None,
) -> list[dict[str, Any]]:
    workspace = get_current_workspace(db)
    query = select(Recipient).where(Recipient.workspace_id == workspace.id)

    if status:
        query = query.where(Recipient.status == status)
    elif not include_inactive:
        query = query.where(Recipient.status == "active")

    rows = db.exec(query.order_by(Recipient.name.asc())).all()
    items = [serialize_recipient(row) for row in rows]

    if search:
        needle = search.strip().lower()
        if needle:
            items = [
                item
                for item in items
                if needle in item["name"].lower()
                or needle in item["wallet_address"].lower()
            ]

    return items


def get_recipient(db: Session, *, recipient_id: int) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(Recipient, recipient_id)
    if not row or row.workspace_id != workspace.id:
        raise RecipientNotFoundError("Recipient not found.")
    return serialize_recipient(row)


def create_recipient(
    db: Session,
    *,
    name: str,
    wallet_address: str,
    network: str,
    notes: str | None = None,
) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    fields = validate_recipient_fields(
        name=name,
        wallet_address=wallet_address,
        network=network,
        notes=notes,
    )

    existing = db.exec(
        select(Recipient).where(
            Recipient.workspace_id == workspace.id,
            Recipient.wallet_address == fields["wallet_address"],
            Recipient.network == fields["network"],
        )
    ).first()
    if existing:
        raise RecipientAlreadyExistsError("A recipient with this wallet address already exists on this network.")

    row = Recipient(
        workspace_id=workspace.id,
        name=fields["name"],
        wallet_address=fields["wallet_address"],
        network=fields["network"],
        notes=fields["notes"],
        status="active",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_recipient(row)


def update_recipient(
    db: Session,
    *,
    recipient_id: int,
    name: str | None = None,
    wallet_address: str | None = None,
    network: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(Recipient, recipient_id)
    if not row or row.workspace_id != workspace.id:
        raise RecipientNotFoundError("Recipient not found.")

    next_name = row.name if name is None else name
    next_address = row.wallet_address if wallet_address is None else wallet_address
    next_network = row.network if network is None else network
    next_notes = row.notes if notes is None else notes

    fields = validate_recipient_fields(
        name=next_name,
        wallet_address=next_address,
        network=next_network,
        notes=next_notes,
    )

    duplicate = db.exec(
        select(Recipient).where(
            Recipient.workspace_id == workspace.id,
            Recipient.wallet_address == fields["wallet_address"],
            Recipient.network == fields["network"],
            Recipient.id != row.id,
        )
    ).first()
    if duplicate:
        raise RecipientAlreadyExistsError("A recipient with this wallet address already exists on this network.")

    row.name = fields["name"]
    row.wallet_address = fields["wallet_address"]
    row.network = fields["network"]
    row.notes = fields["notes"]
    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_recipient(row)


def deactivate_recipient(db: Session, *, recipient_id: int) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(Recipient, recipient_id)
    if not row or row.workspace_id != workspace.id:
        raise RecipientNotFoundError("Recipient not found.")

    row.status = "inactive"
    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    payload = serialize_recipient(row)
    payload["workflow_warning"] = None
    return payload


def recipient_has_active_workflow_links(db: Session, *, recipient_id: int) -> bool:
    """Placeholder until WorkflowDefinition links recipients in Epic 13."""
    _ = (db, recipient_id)
    return False
