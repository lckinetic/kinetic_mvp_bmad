from __future__ import annotations

from dataclasses import dataclass
import hashlib
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
        self._mock_seq = 0

    def _next_mock_seq(self) -> int:
        self._mock_seq += 1
        return self._mock_seq

    def place_trade(self, *, symbol: str, side: Side, amount: float) -> CoinbaseTrade:
        seq = self._next_mock_seq()
        fp = hashlib.sha256(f"trade|{symbol}|{side}|{amount}|{seq}".encode("utf-8")).hexdigest()[:12]
        trade_id = f"cb_trade_{fp}"
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
        seq = self._next_mock_seq()
        fp = hashlib.sha256(
            f"withdraw|{amount}|{currency}|{crypto_address}|{seq}".encode("utf-8")
        ).hexdigest()[:12]
        withdrawal_id = f"cb_withdraw_{fp}"
        return {
            "withdrawal_id": withdrawal_id,
            "asset": currency,
            "amount": float(amount),
            "address": crypto_address,
            "status": "completed",
        }