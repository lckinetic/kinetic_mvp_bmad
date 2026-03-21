from __future__ import annotations

from typing import Dict, Any


SUPPORTED_COMPONENTS: Dict[str, Dict[str, Any]] = {
    "banxa.onramp.create": {
        "label": "Banxa Onramp",
        "provider": "banxa",
        "category": "onramp",
        "required_params": [
            "fiat_amount",
            "fiat_currency",
            "crypto_currency",
            "wallet_address",
            "blockchain",
            "user_email",
        ],
    },
    "privy.wallet.create": {
        "label": "Privy Wallet Create",
        "provider": "privy",
        "category": "wallet",
        "required_params": ["user_email"],
    },
    "coinbase.trade.execute": {
        "label": "Coinbase Trade",
        "provider": "coinbase",
        "category": "trade",
        "required_params": ["symbol", "side", "amount"],
    },
    "coinbase.balance.check": {
        "label": "Coinbase Balance Check",
        "provider": "coinbase",
        "category": "balance",
        "required_params": [],
    },
    "coinbase.withdraw.to_wallet": {
        "label": "Coinbase Withdraw",
        "provider": "coinbase",
        "category": "withdraw",
        "required_params": ["asset", "amount", "address"],
    },
}


def get_component(name: str) -> Dict[str, Any]:
    if name not in SUPPORTED_COMPONENTS:
        raise KeyError(f"Unsupported component: {name}")
    return SUPPORTED_COMPONENTS[name]


def list_components() -> list[Dict[str, Any]]:
    return [
        {"name": name, **meta}
        for name, meta in SUPPORTED_COMPONENTS.items()
    ]