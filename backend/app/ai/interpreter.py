from __future__ import annotations

from typing import Dict, Any


def interpret_request(message: str) -> Dict[str, Any]:
    text = message.lower().strip()

    # --------
    # Wallet-only intent
    # --------
    wallet_keywords = [
        "create wallet",
        "wallet only",
        "set up wallet",
        "setup wallet",
        "new wallet",
    ]
    if any(k in text for k in wallet_keywords):
        return {
            "workflow_name": "generated_wallet_flow",
            "business_summary": "Create a self-custodial wallet.",
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

    # --------
    # Stablecoin / treasury intent
    # --------
    stablecoin_keywords = [
        "usdc",
        "stablecoin",
        "treasury",
        "onramp",
        "fund wallet",
    ]
    if any(k in text for k in stablecoin_keywords):
        return {
            "workflow_name": "generated_stablecoin_flow",
            "business_summary": "Create a wallet and fund it with stablecoins through an onramp.",
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
                    "type": "banxa.onramp.create",
                    "params": {
                        "fiat_amount": 1000,
                        "fiat_currency": "GBP",
                        "crypto_currency": "USDC",
                        "wallet_address": "0xDEMOADDRESS",
                        "blockchain": "ethereum",
                        "user_email": "demo@example.com",
                    },
                },
            ],
        }

    # --------
    # BTC / trading intent
    # --------
    btc_keywords = [
        "buy btc",
        "btc",
        "bitcoin",
        "buy crypto",
        "trade crypto",
        "withdraw to wallet",
    ]
    if any(k in text for k in btc_keywords):
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

    # --------
    # Default fallback
    # --------
    return {
        "workflow_name": "generated_wallet_flow",
        "business_summary": "Create a self-custodial wallet.",
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