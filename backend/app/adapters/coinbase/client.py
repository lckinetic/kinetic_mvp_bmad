from __future__ import annotations

from dataclasses import dataclass
import uuid
from typing import Literal, Optional


Side = Literal["buy", "sell"]


@dataclass
class CoinbaseTrade:
    trade_id: str
    symbol: str
    side: Side
    amount: float
    status: str = "filled"
    price: Optional[float] = None


class CoinbaseClient:
    """
    Mock Coinbase adapter (MVP version).
    Later this will wrap real Coinbase APIs.
    """

    def __init__(self, *, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def place_trade(self, *, symbol: str, side: Side, amount: float) -> CoinbaseTrade:
        trade_id = f"cb_trade_{uuid.uuid4().hex[:12]}"
        return CoinbaseTrade(
            trade_id=trade_id,
            symbol=symbol,
            side=side,
            amount=float(amount),
            status="filled",
            price=50000.0 if symbol.startswith("BTC") else None,
        )

    def get_balance(self) -> dict:
        return {
            "USD": 1000.0,
            "BTC": 0.25,
            "ETH": 1.5,
        }

    def withdraw_crypto(self, *, amount: float, currency: str, crypto_address: str) -> dict:
        withdrawal_id = f"cb_withdraw_{uuid.uuid4().hex[:12]}"
        return {
            "withdrawal_id": withdrawal_id,
            "asset": currency,
            "amount": float(amount),
            "address": crypto_address,
            "status": "completed",
        }