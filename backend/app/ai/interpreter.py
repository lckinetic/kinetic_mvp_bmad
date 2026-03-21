from __future__ import annotations

from typing import Dict, Any


def interpret_request(message: str) -> Dict[str, Any]:
    text = message.lower()

    # MVP heuristic version
    if "buy btc" in text or "btc" in text:
        return {
            "workflow_name": "generated_btc_flow",
            "business_summary": "Create wallet, buy BTC, check balance, withdraw to wallet.",
            "steps": [
                {
                    "id": "step_1",
                    "type": "privy.wallet.create",
                    "params": {
                        "user_email": "demo@example.com",
                    },
                },
                {
                    "id": "step_2",
                    "type": "coinbase.trade.execute",
                    "params": {
                        "symbol": "BTC-USD",
                        "side": "buy",
                        "amount": 100,
                    },
                },
                {
                    "id": "step_3",
                    "type": "coinbase.balance.check",
                    "params": {},
                },
                {
                    "id": "step_4",
                    "type": "coinbase.withdraw.to_wallet",
                    "params": {
                        "asset": "BTC",
                        "amount": 0.001,
                        "address": "0xDEMOADDRESS",
                    },
                },
            ],
        }

    return {
        "workflow_name": "generated_wallet_flow",
        "business_summary": "Create a wallet only.",
        "steps": [
            {
                "id": "step_1",
                "type": "privy.wallet.create",
                "params": {
                    "user_email": "demo@example.com",
                },
            }
        ],
    }