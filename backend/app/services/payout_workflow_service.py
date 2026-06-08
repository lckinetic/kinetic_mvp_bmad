from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.core.config import Settings
from app.db.models import PayoutWorkflowDefinition, Recipient, utcnow
from app.engine.runner import run_template
from app.services.recipient_service import RecipientNotFoundError, serialize_recipient
from app.services.treasury_service import (
    InsufficientBalanceError,
    TreasuryNotFoundError,
    check_sufficient_balance,
    get_current_treasury,
    get_treasury_for_workspace,
)
from app.services.workspace_service import get_current_workspace

SUPPORTED_CADENCES = {"manual", "weekly", "monthly"}
WEEKLY_DAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


class PayoutWorkflowNotFoundError(LookupError):
    pass


class PayoutWorkflowValidationError(ValueError):
    pass


class PayoutWorkflowDisabledError(PermissionError):
    pass


class PayoutWorkflowGuardrailError(ValueError):
    pass


def _format_schedule(cadence: str, day: str | None) -> str:
    if cadence == "manual":
        return "Manual run only"
    if cadence == "weekly" and day:
        return f"Every {day.capitalize()}"
    if cadence == "monthly" and day:
        return f"Monthly on day {day}"
    return cadence.capitalize()


def _validate_schedule(cadence: str, day: str | None) -> tuple[str, str | None]:
    normalized = (cadence or "manual").strip().lower()
    if normalized not in SUPPORTED_CADENCES:
        raise PayoutWorkflowValidationError("Schedule cadence must be manual, weekly, or monthly.")

    normalized_day = (day or "").strip().lower() or None
    if normalized == "weekly":
        if not normalized_day or normalized_day not in WEEKLY_DAYS:
            raise PayoutWorkflowValidationError("Weekly schedules require a valid weekday.")
    elif normalized == "monthly":
        if not normalized_day or not normalized_day.isdigit() or not (1 <= int(normalized_day) <= 28):
            raise PayoutWorkflowValidationError("Monthly schedules require a day between 1 and 28.")
    else:
        normalized_day = None

    return normalized, normalized_day


def _get_recipient_for_workspace(db: Session, *, workspace_id: int, recipient_id: int) -> Recipient:
    row = db.get(Recipient, recipient_id)
    if not row or row.workspace_id != workspace_id:
        raise RecipientNotFoundError("Recipient not found.")
    return row


def serialize_payout_workflow(
    db: Session,
    row: PayoutWorkflowDefinition,
    *,
    recipient: Recipient | None = None,
) -> dict[str, Any]:
    if recipient is None:
        recipient = db.get(Recipient, row.recipient_id)
    recipient_payload = serialize_recipient(recipient) if recipient else None
    return {
        "id": row.id,
        "workspace_id": row.workspace_id,
        "name": row.name,
        "template_name": row.template_name,
        "recipient_id": row.recipient_id,
        "recipient": recipient_payload,
        "amount": row.amount,
        "asset": row.asset,
        "schedule_cadence": row.schedule_cadence,
        "schedule_day": row.schedule_day,
        "schedule_label": _format_schedule(row.schedule_cadence, row.schedule_day),
        "enabled": row.enabled,
        "last_run_id": row.last_run_id,
        "last_run_at": row.last_run_at.isoformat() if row.last_run_at else None,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
    }


def list_payout_workflows(db: Session) -> list[dict[str, Any]]:
    workspace = get_current_workspace(db)
    rows = db.exec(
        select(PayoutWorkflowDefinition)
        .where(PayoutWorkflowDefinition.workspace_id == workspace.id)
        .order_by(PayoutWorkflowDefinition.created_at.desc())
    ).all()
    return [serialize_payout_workflow(db, row) for row in rows]


def get_payout_workflow(db: Session, *, workflow_id: int) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(PayoutWorkflowDefinition, workflow_id)
    if not row or row.workspace_id != workspace.id:
        raise PayoutWorkflowNotFoundError("Payout workflow not found.")
    return serialize_payout_workflow(db, row)


def create_payout_workflow(
    db: Session,
    *,
    name: str,
    recipient_id: int,
    amount: float,
    asset: str = "USDC",
    schedule_cadence: str = "manual",
    schedule_day: str | None = None,
) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    normalized_name = (name or "").strip()
    if not normalized_name:
        raise PayoutWorkflowValidationError("Workflow name is required.")
    if amount <= 0:
        raise PayoutWorkflowValidationError("Payout amount must be greater than zero.")

    recipient = _get_recipient_for_workspace(db, workspace_id=workspace.id, recipient_id=recipient_id)
    if recipient.status != "active":
        raise PayoutWorkflowGuardrailError("Recipient must be active to configure a payout workflow.")

    treasury = get_treasury_for_workspace(db, workspace_id=workspace.id)
    if not treasury:
        raise PayoutWorkflowGuardrailError("Create a treasury wallet before configuring payout workflows.")

    cadence, day = _validate_schedule(schedule_cadence, schedule_day)
    asset_norm = (asset or "USDC").strip().upper()
    if asset_norm != "USDC":
        raise PayoutWorkflowValidationError("Only USDC payouts are supported in this MVP.")

    row = PayoutWorkflowDefinition(
        workspace_id=workspace.id,
        name=normalized_name,
        template_name="contractor_payout",
        recipient_id=recipient.id,
        amount=round(amount, 2),
        asset=asset_norm,
        schedule_cadence=cadence,
        schedule_day=day,
        enabled=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_payout_workflow(db, row, recipient=recipient)


def update_payout_workflow(
    db: Session,
    *,
    workflow_id: int,
    name: str | None = None,
    recipient_id: int | None = None,
    amount: float | None = None,
    schedule_cadence: str | None = None,
    schedule_day: str | None = None,
) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(PayoutWorkflowDefinition, workflow_id)
    if not row or row.workspace_id != workspace.id:
        raise PayoutWorkflowNotFoundError("Payout workflow not found.")

    recipient = _get_recipient_for_workspace(db, workspace_id=workspace.id, recipient_id=row.recipient_id)
    if name is not None:
        normalized_name = name.strip()
        if not normalized_name:
            raise PayoutWorkflowValidationError("Workflow name is required.")
        row.name = normalized_name
    if recipient_id is not None:
        recipient = _get_recipient_for_workspace(db, workspace_id=workspace.id, recipient_id=recipient_id)
        if recipient.status != "active":
            raise PayoutWorkflowGuardrailError("Recipient must be active to configure a payout workflow.")
        row.recipient_id = recipient.id
    if amount is not None:
        if amount <= 0:
            raise PayoutWorkflowValidationError("Payout amount must be greater than zero.")
        row.amount = round(amount, 2)
    if schedule_cadence is not None or schedule_day is not None:
        cadence, day = _validate_schedule(
            schedule_cadence if schedule_cadence is not None else row.schedule_cadence,
            schedule_day if schedule_day is not None else row.schedule_day,
        )
        row.schedule_cadence = cadence
        row.schedule_day = day

    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_payout_workflow(db, row, recipient=recipient)


def set_payout_workflow_enabled(db: Session, *, workflow_id: int, enabled: bool) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(PayoutWorkflowDefinition, workflow_id)
    if not row or row.workspace_id != workspace.id:
        raise PayoutWorkflowNotFoundError("Payout workflow not found.")
    row.enabled = enabled
    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_payout_workflow(db, row)


def validate_run_guardrails(db: Session, *, settings: Settings, workflow: PayoutWorkflowDefinition) -> Recipient:
    if not workflow.enabled:
        raise PayoutWorkflowDisabledError("This payout workflow is disabled.")

    workspace = get_current_workspace(db)
    recipient = _get_recipient_for_workspace(db, workspace_id=workspace.id, recipient_id=workflow.recipient_id)
    if recipient.status != "active":
        raise PayoutWorkflowGuardrailError("Recipient is inactive. Update the workflow before running.")

    treasury_view = get_current_treasury(db, settings=settings)
    check_sufficient_balance(db, treasury_id=treasury_view["id"], amount=workflow.amount)
    return recipient


def run_payout_workflow(db: Session, *, settings: Settings, workflow_id: int) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(PayoutWorkflowDefinition, workflow_id)
    if not row or row.workspace_id != workspace.id:
        raise PayoutWorkflowNotFoundError("Payout workflow not found.")

    recipient = validate_run_guardrails(db, settings=settings, workflow=row)

    run = run_template(
        db=db,
        template_name=row.template_name,
        input_data={
            "workspace_id": workspace.id,
            "recipient_name": recipient.name,
            "recipient_address": recipient.wallet_address,
            "recipient_network": recipient.network,
            "amount": row.amount,
            "asset": row.asset,
            "payout_workflow_id": row.id,
        },
        settings=settings,
    )

    row.last_run_id = run.id
    row.last_run_at = utcnow()
    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "workflow": serialize_payout_workflow(db, row, recipient=recipient),
        "run": {
            "id": run.id,
            "template_name": run.template_name,
            "status": run.status,
            "input": run.input,
            "output": run.output,
            "error": run.error,
            "created_at": run.created_at.isoformat(),
            "updated_at": run.updated_at.isoformat(),
        },
    }


def recipient_has_active_workflow_links(db: Session, *, recipient_id: int) -> bool:
    row = db.exec(
        select(PayoutWorkflowDefinition).where(
            PayoutWorkflowDefinition.recipient_id == recipient_id,
            PayoutWorkflowDefinition.enabled == True,  # noqa: E712
        )
    ).first()
    return row is not None
