from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.db.models import Alert, TreasuryTransfer, WorkflowRun, utcnow
from app.services.workspace_service import get_current_workspace

ALERT_CATALOG: dict[str, dict[str, str]] = {
    "payout.failed": {
        "title": "Payout could not be completed",
        "message": "The payout workflow ended in a failed state. Review the run details and retry when ready.",
        "severity": "critical",
        "recovery_action": "retry_payout",
        "recovery_label": "Retry payout",
        "nav_route": "workflows",
    },
    "insufficient_balance": {
        "title": "Treasury balance is too low for this payout",
        "message": "Fund treasury before retrying this payout workflow.",
        "severity": "critical",
        "recovery_action": "fund_treasury",
        "recovery_label": "Fund treasury",
        "nav_route": "treasury",
    },
    "transfer.failed": {
        "title": "Payout could not be completed",
        "message": "A treasury transfer failed. Review activity details and retry when balance and recipient details are correct.",
        "severity": "critical",
        "recovery_action": "view_activity",
        "recovery_label": "View details",
        "nav_route": "activity",
    },
    "workflow.disabled": {
        "title": "This workflow is paused",
        "message": "Enable the payout workflow before running it again.",
        "severity": "warning",
        "recovery_action": "enable_workflow",
        "recovery_label": "Enable workflow",
        "nav_route": "workflows",
    },
    "recipient.invalid": {
        "title": "Recipient wallet address isn't valid for this network",
        "message": "Update the contractor recipient details before retrying the payout.",
        "severity": "warning",
        "recovery_action": "edit_recipient",
        "recovery_label": "Edit recipient",
        "nav_route": "recipients",
    },
    "provider.unavailable": {
        "title": "Treasury provider isn't available",
        "message": "Treasury wallet creation requires a configured provider. Use mock mode for demo or configure Privy credentials.",
        "severity": "critical",
        "recovery_action": "view_settings",
        "recovery_label": "Open settings",
        "nav_route": "settings",
    },
}


class AlertNotFoundError(LookupError):
    pass


def serialize_alert(row: Alert) -> dict[str, Any]:
    catalog = ALERT_CATALOG.get(row.alert_type, {})
    return {
        "id": row.id,
        "workspace_id": row.workspace_id,
        "alert_type": row.alert_type,
        "severity": row.severity,
        "status": row.status,
        "title": row.title,
        "message": row.message,
        "recovery_action": row.recovery_action,
        "recovery_label": row.recovery_label,
        "source_kind": row.source_kind,
        "source_id": row.source_id,
        "links": row.links or {},
        "payload": row.payload or {},
        "acknowledged_at": row.acknowledged_at.isoformat() if row.acknowledged_at else None,
        "resolved_at": row.resolved_at.isoformat() if row.resolved_at else None,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
        "nav_route": (row.links or {}).get("nav_route") or catalog.get("nav_route", "activity"),
        "is_prominent": row.status == "open",
    }


def _upsert_alert(
    db: Session,
    *,
    workspace_id: int,
    alert_type: str,
    source_kind: str,
    source_id: int,
    title: str | None = None,
    message: str | None = None,
    links: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> Alert:
    catalog = ALERT_CATALOG.get(alert_type, {})
    existing = db.exec(
        select(Alert).where(
            Alert.source_kind == source_kind,
            Alert.source_id == source_id,
            Alert.alert_type == alert_type,
        )
    ).first()
    if existing and existing.status != "resolved":
        existing.message = message or catalog.get("message", existing.message)
        existing.payload = {**(existing.payload or {}), **(payload or {})}
        existing.links = {**(existing.links or {}), **(links or {})}
        existing.updated_at = utcnow()
        if existing.status == "acknowledged":
            existing.status = "open"
            existing.acknowledged_at = None
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    row = Alert(
        workspace_id=workspace_id,
        alert_type=alert_type,
        severity=catalog.get("severity", "warning"),
        status="open",
        title=title or catalog.get("title", alert_type),
        message=message or catalog.get("message", "An operational issue needs attention."),
        recovery_action=catalog.get("recovery_action", "view_activity"),
        recovery_label=catalog.get("recovery_label", "View details"),
        source_kind=source_kind,
        source_id=source_id,
        links={
            **(links or {}),
            "nav_route": catalog.get("nav_route", "activity"),
        },
        payload=payload or {},
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_alert_from_failed_run(db: Session, *, run: WorkflowRun, workspace_id: int) -> Alert | None:
    if run.status != "failed":
        return None

    alert_type = "payout.failed"

    payout_workflow_id = (run.input or {}).get("payout_workflow_id")
    links = {
        "run_id": run.id,
        "nav": {"workflows": "workflows", "activity": "activity", "treasury": "treasury"},
    }
    if payout_workflow_id:
        links["payout_workflow_id"] = payout_workflow_id

    return _upsert_alert(
        db,
        workspace_id=workspace_id,
        alert_type=alert_type,
        source_kind="workflow_run",
        source_id=run.id,
        message=run.error or ALERT_CATALOG[alert_type]["message"],
        links=links,
        payload={"template_name": run.template_name, "error": run.error},
    )


def create_insufficient_balance_alert(
    db: Session,
    *,
    workspace_id: int,
    workflow_id: int,
    balance: float,
    required: float,
    shortfall: float,
) -> Alert:
    catalog = ALERT_CATALOG["insufficient_balance"]
    return _upsert_alert(
        db,
        workspace_id=workspace_id,
        alert_type="insufficient_balance",
        source_kind="payout_workflow",
        source_id=workflow_id,
        message=f"{catalog['message']} Available {balance:.2f} USDC, required {required:.2f} USDC.",
        links={
            "payout_workflow_id": workflow_id,
            "nav": {"treasury": "treasury", "workflows": "workflows", "activity": "activity"},
        },
        payload={"balance": balance, "required": required, "shortfall": shortfall, "asset": "USDC"},
    )


def create_alert_from_failed_transfer(db: Session, *, transfer: TreasuryTransfer) -> Alert | None:
    if transfer.status != "failed":
        return None
    return _upsert_alert(
        db,
        workspace_id=transfer.workspace_id,
        alert_type="transfer.failed",
        source_kind="treasury_transfer",
        source_id=transfer.id,
        message=transfer.error_message or ALERT_CATALOG["transfer.failed"]["message"],
        links={
            "treasury_transfer_id": transfer.id,
            "nav": {"activity": "activity", "treasury": "treasury", "workflows": "workflows"},
        },
        payload={
            "amount": transfer.amount,
            "asset": transfer.asset,
            "counterparty_label": transfer.counterparty_label,
        },
    )


def create_recipient_invalid_alert(
    db: Session,
    *,
    workspace_id: int,
    workflow_id: int,
    recipient_id: int,
) -> Alert:
    catalog = ALERT_CATALOG["recipient.invalid"]
    return _upsert_alert(
        db,
        workspace_id=workspace_id,
        alert_type="recipient.invalid",
        source_kind="payout_workflow",
        source_id=workflow_id,
        message=catalog["message"],
        links={
            "payout_workflow_id": workflow_id,
            "recipient_id": recipient_id,
            "nav": {"recipients": "recipients", "workflows": "workflows", "activity": "activity"},
        },
        payload={"recipient_id": recipient_id},
    )


def create_provider_unavailable_alert(db: Session, *, workspace_id: int, message: str | None = None) -> Alert:
    catalog = ALERT_CATALOG["provider.unavailable"]
    return _upsert_alert(
        db,
        workspace_id=workspace_id,
        alert_type="provider.unavailable",
        source_kind="workspace",
        source_id=workspace_id,
        message=message or catalog["message"],
        links={"nav": {"settings": "settings", "treasury": "treasury"}},
    )


def create_workflow_disabled_alert(db: Session, *, workspace_id: int, workflow_id: int) -> Alert:
    return _upsert_alert(
        db,
        workspace_id=workspace_id,
        alert_type="workflow.disabled",
        source_kind="payout_workflow",
        source_id=workflow_id,
        links={"payout_workflow_id": workflow_id, "nav": {"workflows": "workflows"}},
    )


def resolve_alerts_for_workflow(db: Session, *, workspace_id: int, workflow_id: int) -> None:
    rows = db.exec(
        select(Alert).where(
            Alert.workspace_id == workspace_id,
            Alert.source_kind == "payout_workflow",
            Alert.source_id == workflow_id,
            Alert.status.in_(["open", "acknowledged"]),
        )
    ).all()
    for row in rows:
        row.status = "resolved"
        row.resolved_at = utcnow()
        row.updated_at = utcnow()
        db.add(row)
    db.commit()


def list_alerts(
    db: Session,
    *,
    status: str | None = None,
    include_acknowledged: bool = True,
    limit: int = 50,
) -> list[dict[str, Any]]:
    workspace = get_current_workspace(db)
    query = select(Alert).where(Alert.workspace_id == workspace.id)
    if status:
        query = query.where(Alert.status == status)
    elif not include_acknowledged:
        query = query.where(Alert.status == "open")
    rows = db.exec(query.order_by(Alert.created_at.desc()).limit(limit)).all()
    return [serialize_alert(row) for row in rows]


def get_alert(db: Session, *, alert_id: int) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(Alert, alert_id)
    if not row or row.workspace_id != workspace.id:
        raise AlertNotFoundError("Alert not found.")
    return serialize_alert(row)


def acknowledge_alert(db: Session, *, alert_id: int) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(Alert, alert_id)
    if not row or row.workspace_id != workspace.id:
        raise AlertNotFoundError("Alert not found.")
    row.status = "acknowledged"
    row.acknowledged_at = utcnow()
    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_alert(row)


def resolve_alert(db: Session, *, alert_id: int) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(Alert, alert_id)
    if not row or row.workspace_id != workspace.id:
        raise AlertNotFoundError("Alert not found.")
    row.status = "resolved"
    row.resolved_at = utcnow()
    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_alert(row)
