from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.db.models import ActivityEvent, PayoutWorkflowDefinition, TreasuryTransfer, WorkflowRun
from app.services.workspace_service import get_current_workspace

ACTIVITY_EVENT_TYPES = {
    "payout.completed": "Payout completed",
    "payout.failed": "Payout failed",
    "treasury.deposit": "Treasury funded",
    "treasury.payout": "Treasury payout sent",
    "workflow.run_completed": "Workflow run completed",
    "workflow.run_failed": "Workflow run failed",
}


class ActivityNotFoundError(LookupError):
    pass


def serialize_activity(row: ActivityEvent) -> dict[str, Any]:
    return {
        "id": row.id,
        "workspace_id": row.workspace_id,
        "event_type": row.event_type,
        "event_label": ACTIVITY_EVENT_TYPES.get(row.event_type, row.event_type),
        "status": row.status,
        "title": row.title,
        "summary": row.summary,
        "source_kind": row.source_kind,
        "source_id": row.source_id,
        "links": row.links or {},
        "payload": row.payload or {},
        "created_at": row.created_at.isoformat(),
    }


def _upsert_activity(
    db: Session,
    *,
    workspace_id: int,
    event_type: str,
    status: str,
    title: str,
    summary: str,
    source_kind: str,
    source_id: int,
    links: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> ActivityEvent:
    existing = db.exec(
        select(ActivityEvent).where(
            ActivityEvent.source_kind == source_kind,
            ActivityEvent.source_id == source_id,
            ActivityEvent.event_type == event_type,
        )
    ).first()
    if existing:
        return existing

    row = ActivityEvent(
        workspace_id=workspace_id,
        event_type=event_type,
        status=status,
        title=title,
        summary=summary,
        source_kind=source_kind,
        source_id=source_id,
        links=links or {},
        payload=payload or {},
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def ingest_workflow_run_activity(db: Session, *, run: WorkflowRun, workspace_id: int) -> ActivityEvent | None:
    if run.template_name != "contractor_payout":
        event_type = "workflow.run_completed" if run.status == "completed" else "workflow.run_failed"
        title = f"{run.template_name} run {run.status}"
        summary = f"Workflow run #{run.id} finished with status {run.status}."
    elif run.status == "completed":
        event_type = "payout.completed"
        recipient_name = str((run.input or {}).get("recipient_name", "contractor"))
        amount = (run.input or {}).get("amount")
        asset = (run.input or {}).get("asset", "USDC")
        title = f"Payout to {recipient_name} completed"
        summary = f"Sent {amount} {asset} from treasury to {recipient_name}."
    else:
        event_type = "payout.failed"
        recipient_name = str((run.input or {}).get("recipient_name", "contractor"))
        title = f"Payout to {recipient_name} failed"
        summary = run.error or "The payout workflow could not be completed."

    run_input = run.input or {}
    payout_workflow_id = run_input.get("payout_workflow_id")
    recipient_id = run_input.get("recipient_id")
    if recipient_id is not None:
        recipient_id = int(recipient_id)
    elif isinstance(run.output, dict):
        recipient_id = (run.output.get("result") or {}).get("recipient_id")
        if recipient_id is not None:
            recipient_id = int(recipient_id)
    if recipient_id is None and payout_workflow_id is not None:
        workflow = db.get(PayoutWorkflowDefinition, int(payout_workflow_id))
        if workflow and workflow.workspace_id == workspace_id:
            recipient_id = workflow.recipient_id

    links = {
        "run_id": run.id,
        "nav": {
            "workflows": "workflows",
            "treasury": "treasury",
            "activity": "activity",
        },
    }
    if payout_workflow_id:
        links["payout_workflow_id"] = payout_workflow_id
    if recipient_id:
        links["recipient_id"] = recipient_id

    return _upsert_activity(
        db,
        workspace_id=workspace_id,
        event_type=event_type,
        status="completed" if run.status == "completed" else "failed",
        title=title,
        summary=summary,
        source_kind="workflow_run",
        source_id=run.id,
        links=links,
        payload={
            "template_name": run.template_name,
            "run_status": run.status,
            "error": run.error,
        },
    )


def ingest_transfer_activity(db: Session, *, transfer: TreasuryTransfer) -> ActivityEvent:
    if transfer.direction == "inbound":
        event_type = "treasury.deposit"
        title = "Treasury funded"
        summary = f"Received {transfer.amount} {transfer.asset} into treasury."
    else:
        event_type = "treasury.payout"
        title = "Treasury payout sent"
        counterparty = transfer.counterparty_label or "recipient"
        summary = f"Sent {transfer.amount} {transfer.asset} to {counterparty}."

    return _upsert_activity(
        db,
        workspace_id=transfer.workspace_id,
        event_type=event_type,
        status=transfer.status,
        title=title,
        summary=summary,
        source_kind="treasury_transfer",
        source_id=transfer.id,
        links={
            "treasury_transfer_id": transfer.id,
            "nav": {"treasury": "treasury", "activity": "activity"},
        },
        payload={
            "direction": transfer.direction,
            "amount": transfer.amount,
            "asset": transfer.asset,
            "counterparty_label": transfer.counterparty_label,
            "transaction_hash": transfer.transaction_hash,
        },
    )


def list_activity_events(
    db: Session,
    *,
    event_type: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    workspace = get_current_workspace(db)
    query = select(ActivityEvent).where(ActivityEvent.workspace_id == workspace.id)
    if event_type:
        query = query.where(ActivityEvent.event_type == event_type)
    if status:
        query = query.where(ActivityEvent.status == status)
    rows = db.exec(query.order_by(ActivityEvent.created_at.desc()).limit(limit)).all()
    return [serialize_activity(row) for row in rows]


def get_activity_event(db: Session, *, activity_id: int) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    row = db.get(ActivityEvent, activity_id)
    if not row or row.workspace_id != workspace.id:
        raise ActivityNotFoundError("Activity event not found.")
    return serialize_activity(row)
