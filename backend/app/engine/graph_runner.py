from __future__ import annotations

from typing import Any, Dict

from sqlmodel import Session

from app.core.config import Settings
from app.services.workflow_steps import step_start, step_complete, step_fail
from app.engine.component_registry import get_component


def run_graph(
    *,
    db: Session,
    settings: Settings,
    adapters: Dict[str, Any],
    run_id: int,
    workflow: Dict[str, Any],
) -> Dict[str, Any]:
    steps_out = []
    seq = 1

    for step in workflow.get("steps", []):
        step_id = step["id"]
        step_type = step["type"]
        params = step.get("params", {})

        s = step_start(
            db=db,
            run_id=run_id,
            seq=seq,
            step_name=step_type,
            data={"component_id": step_id, "params": params},
        )

        try:
            result = execute_component(
                adapters=adapters,
                component_type=step_type,
                params=params,
            )
            step_complete(db=db, step_id=s.id, data=result or {})
            steps_out.append(
                {
                    "id": step_id,
                    "type": step_type,
                    "result": result or {},
                }
            )
        except Exception as e:
            step_fail(db=db, step_id=s.id, error=f"{type(e).__name__}: {e}")
            raise

        seq += 1

    return {
        "workflow_name": workflow.get("workflow_name", "generated_workflow"),
        "business_summary": workflow.get("business_summary", ""),
        "steps": steps_out,
    }


def execute_component(*, adapters: Dict[str, Any], component_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    get_component(component_type)  # validates supported component

    if component_type == "privy.wallet.create":
        privy = adapters["privy"]
        wallet = privy.create_wallet(user_email=params["user_email"])
        return {
            "wallet_id": wallet.wallet_id,
            "address": wallet.address,
        }

    if component_type == "banxa.onramp.create":
        # MVP: mock response only for AI-generated graph path
        return {
            "provider": "banxa",
            "status": "created",
            "fiat_amount": params["fiat_amount"],
            "fiat_currency": params["fiat_currency"],
            "crypto_currency": params["crypto_currency"],
        }

    if component_type == "coinbase.trade.execute":
        coinbase = adapters["coinbase"]
        trade = coinbase.place_trade(
            symbol=params["symbol"],
            side=params["side"],
            amount=float(params["amount"]),
        )
        return {
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "side": trade.side,
            "amount": trade.amount,
            "status": trade.status,
        }

    if component_type == "coinbase.balance.check":
        coinbase = adapters["coinbase"]
        balance = coinbase.get_balance()
        return balance

    if component_type == "coinbase.withdraw.to_wallet":
        coinbase = adapters["coinbase"]
        withdrawal = coinbase.withdraw_crypto(
            amount=float(params["amount"]),
            currency=params["asset"],
            crypto_address=params["address"],
        )
        return withdrawal

    raise ValueError(f"Unsupported component_type: {component_type}")