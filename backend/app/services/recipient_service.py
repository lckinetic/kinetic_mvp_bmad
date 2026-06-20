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

SUPPORTED_PAYOUT_CADENCES = {"manual", "weekly", "monthly"}
WEEKLY_DAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


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


def _format_default_schedule(cadence: str | None, day: str | None) -> str | None:
    if not cadence or cadence == "manual":
        return "Manual / per workflow"
    if cadence == "weekly" and day:
        return f"Every {day.capitalize()}"
    if cadence == "monthly" and day:
        return f"Monthly on day {day}"
    return cadence.capitalize()


def _validate_payout_defaults(
    *,
    default_payout_asset: str | None = None,
    default_payout_amount: float | None = None,
    default_schedule_cadence: str | None = None,
    default_schedule_day: str | None = None,
) -> dict[str, str | float | None]:
    asset: str | None = None
    amount: float | None = None
    cadence: str | None = None
    day: str | None = None

    if default_payout_amount is not None:
        amount_value = float(default_payout_amount)
        if amount_value <= 0:
            raise RecipientValidationError("Default payout amount must be greater than zero.")
        amount = round(amount_value, 2)
        asset = (default_payout_asset or "USDC").strip().upper()
        if asset != "USDC":
            raise RecipientValidationError("Only USDC default payouts are supported in this MVP.")

    if default_schedule_cadence:
        cadence = default_schedule_cadence.strip().lower()
        if cadence not in SUPPORTED_PAYOUT_CADENCES:
            raise RecipientValidationError("Default schedule must be manual, weekly, or monthly.")
        day_raw = (default_schedule_day or "").strip().lower() or None
        if cadence == "weekly":
            if not day_raw or day_raw not in WEEKLY_DAYS:
                raise RecipientValidationError("Weekly default schedule requires a valid weekday.")
            day = day_raw
        elif cadence == "monthly":
            if not day_raw or not day_raw.isdigit() or not (1 <= int(day_raw) <= 28):
                raise RecipientValidationError("Monthly default schedule requires a day between 1 and 28.")
            day = day_raw
        else:
            day = None

    return {
        "default_payout_asset": asset,
        "default_payout_amount": amount,
        "default_schedule_cadence": cadence,
        "default_schedule_day": day,
    }


def serialize_recipient(row: Recipient) -> dict[str, Any]:
    schedule_label = _format_default_schedule(row.default_schedule_cadence, row.default_schedule_day)
    return {
        "id": row.id,
        "workspace_id": row.workspace_id,
        "name": row.name,
        "wallet_address": row.wallet_address,
        "wallet_address_short": _short_address(row.wallet_address),
        "network": row.network,
        "network_label": SUPPORTED_NETWORKS.get(row.network, row.network),
        "notes": row.notes,
        "default_payout_asset": row.default_payout_asset,
        "default_payout_amount": row.default_payout_amount,
        "default_schedule_cadence": row.default_schedule_cadence,
        "default_schedule_day": row.default_schedule_day,
        "default_schedule_label": schedule_label,
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
    default_payout_asset: str | None = None,
    default_payout_amount: float | None = None,
    default_schedule_cadence: str | None = None,
    default_schedule_day: str | None = None,
) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    fields = validate_recipient_fields(
        name=name,
        wallet_address=wallet_address,
        network=network,
        notes=notes,
    )
    payout_defaults = _validate_payout_defaults(
        default_payout_asset=default_payout_asset,
        default_payout_amount=default_payout_amount,
        default_schedule_cadence=default_schedule_cadence,
        default_schedule_day=default_schedule_day,
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
        default_payout_asset=payout_defaults["default_payout_asset"],
        default_payout_amount=payout_defaults["default_payout_amount"],
        default_schedule_cadence=payout_defaults["default_schedule_cadence"],
        default_schedule_day=payout_defaults["default_schedule_day"],
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
    default_payout_asset: str | None = None,
    default_payout_amount: float | None = None,
    default_schedule_cadence: str | None = None,
    default_schedule_day: str | None = None,
    clear_payout_defaults: bool = False,
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

    if clear_payout_defaults:
        payout_defaults = {
            "default_payout_asset": None,
            "default_payout_amount": None,
            "default_schedule_cadence": None,
            "default_schedule_day": None,
        }
    else:
        payout_defaults = _validate_payout_defaults(
            default_payout_asset=default_payout_asset if default_payout_asset is not None else row.default_payout_asset,
            default_payout_amount=default_payout_amount if default_payout_amount is not None else row.default_payout_amount,
            default_schedule_cadence=default_schedule_cadence if default_schedule_cadence is not None else row.default_schedule_cadence,
            default_schedule_day=default_schedule_day if default_schedule_day is not None else row.default_schedule_day,
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
    row.default_payout_asset = payout_defaults["default_payout_asset"]
    row.default_payout_amount = payout_defaults["default_payout_amount"]
    row.default_schedule_cadence = payout_defaults["default_schedule_cadence"]
    row.default_schedule_day = payout_defaults["default_schedule_day"]
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
    from app.services.payout_workflow_service import recipient_has_active_workflow_links as _has_links

    return _has_links(db, recipient_id=recipient_id)
