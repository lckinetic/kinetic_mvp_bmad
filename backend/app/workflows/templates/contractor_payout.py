from __future__ import annotations

from typing import Any, Dict

from sqlmodel import Session

from app.core.config import Settings
from app.services.treasury_service import (
    InsufficientBalanceError,
    TreasuryNotFoundError,
    check_sufficient_balance,
    compute_balance,
    get_treasury_for_workspace,
    record_outbound_transfer,
)
from app.services.workflow_steps import step_complete, step_fail, step_start
from app.workflows.registry import register


@register(
    name="contractor_payout",
    version="1.0",
    display_name="Contractor Payout",
    description="Check treasury balance, send stablecoin payout to a contractor, and complete.",
    category="payout",
    input_schema=[
        {
            "name": "recipient_name",
            "label": "Recipient name",
            "type": "string",
            "required": True,
            "example": "Alice Chen",
        },
        {
            "name": "recipient_address",
            "label": "Recipient wallet address",
            "type": "string",
            "required": True,
            "example": "0x1111111111111111111111111111111111111111",
        },
        {
            "name": "recipient_network",
            "label": "Recipient network",
            "type": "string",
            "required": True,
            "default": "base",
            "example": "base",
        },
        {
            "name": "amount",
            "label": "Payout amount",
            "type": "number",
            "required": True,
            "default": 50,
            "min": 0.01,
            "step": 0.01,
            "example": 50,
        },
        {
            "name": "asset",
            "label": "Asset",
            "type": "string",
            "required": True,
            "default": "USDC",
            "example": "USDC",
        },
        {
            "name": "workspace_id",
            "label": "Workspace ID",
            "type": "number",
            "required": True,
        },
    ],
    business_summary="Pay a contractor from treasury after confirming sufficient stablecoin balance.",
    business_steps=[
        "Checking treasury balance",
        "Sending payout to contractor",
        "Completing payout run",
    ],
    step_outline=[
        "balance.check",
        "transfer.payout",
        "payout.complete",
    ],
    step_labels={
        "balance.check": "Checking balance",
        "transfer.payout": "Sending payout",
        "payout.complete": "Complete",
    },
)
def contractor_payout(
    *,
    db: Session,
    settings: Settings,
    adapters: Dict[str, Any],
    input: Dict[str, Any],
) -> Dict[str, Any]:
    run_id = int(input.get("run_id", 0))
    workspace_id = int(input["workspace_id"])
    amount = round(float(input["amount"]), 2)
    asset = str(input.get("asset", "USDC"))
    recipient_name = str(input["recipient_name"])
    recipient_address = str(input["recipient_address"])
    recipient_network = str(input.get("recipient_network", "base"))

    treasury = get_treasury_for_workspace(db, workspace_id=workspace_id)
    if not treasury:
        raise TreasuryNotFoundError("Treasury is required before running contractor payouts.")

    seq = 1
    steps_out: list[dict[str, Any]] = []

    s = step_start(db=db, run_id=run_id, seq=seq, step_name="balance.check")
    try:
        balance = compute_balance(db, treasury_id=treasury.id)
        check_sufficient_balance(db, treasury_id=treasury.id, amount=amount)
        step_complete(
            db=db,
            step_id=s.id,
            data={"balance": balance, "required": amount, "asset": asset, "sufficient": True},
        )
        steps_out.append({"step": "balance.check", "balance": balance, "required": amount})
    except InsufficientBalanceError as exc:
        step_fail(
            db=db,
            step_id=s.id,
            error=str(exc),
            data={"balance": exc.balance, "required": exc.required, "shortfall": exc.shortfall},
        )
        raise
    except Exception as exc:
        step_fail(db=db, step_id=s.id, error=str(exc))
        raise
    seq += 1

    s = step_start(db=db, run_id=run_id, seq=seq, step_name="transfer.payout")
    try:
        transfer = record_outbound_transfer(
            db,
            treasury_id=treasury.id,
            workspace_id=workspace_id,
            amount=amount,
            asset=asset,
            counterparty_label=recipient_name,
            reference=f"payout_run_{run_id}",
            recipient_address=recipient_address,
            recipient_network=recipient_network,
        )
        step_complete(
            db=db,
            step_id=s.id,
            data={
                "transfer_id": transfer.id,
                "transaction_hash": transfer.transaction_hash,
                "recipient_address": recipient_address,
                "recipient_network": recipient_network,
                "amount": amount,
                "asset": asset,
            },
        )
        steps_out.append({"step": "transfer.payout", "transfer_id": transfer.id, "status": "completed"})
    except Exception as exc:
        step_fail(db=db, step_id=s.id, error=str(exc))
        raise
    seq += 1

    s = step_start(db=db, run_id=run_id, seq=seq, step_name="payout.complete")
    try:
        step_complete(
            db=db,
            step_id=s.id,
            data={
                "recipient_name": recipient_name,
                "amount": amount,
                "asset": asset,
                "status": "completed",
            },
        )
        steps_out.append({"step": "payout.complete", "status": "completed"})
    except Exception as exc:
        step_fail(db=db, step_id=s.id, error=str(exc))
        raise

    return {
        "template": "contractor_payout",
        "steps": steps_out,
        "result": {
            "run_id": run_id,
            "recipient_name": recipient_name,
            "recipient_address": recipient_address,
            "amount": amount,
            "asset": asset,
            "transfer_id": transfer.id,
        },
    }
