from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib


@dataclass(frozen=True)
class BanxaCreateOrderResult:
    order_id: str
    checkout_url: str
    status: str
    created_at: datetime


class BanxaClient:
    """
    MVP client. In MOCK_MODE it returns fake order IDs and a sandbox-like checkout URL.
    Later we swap the NotImplementedError for real Banxa API calls.
    """
    def __init__(self, mock_mode: bool):
        self.mock_mode = mock_mode
        self._mock_seq = 0

    def _next_mock_seq(self) -> int:
        self._mock_seq += 1
        return self._mock_seq

    @staticmethod
    def _mock_stamp(seq: int) -> datetime:
        # Deterministic and monotonic timestamp for CI-safe snapshots.
        base = datetime(2025, 1, 1, tzinfo=timezone.utc)
        return base + timedelta(seconds=max(seq, 0))

    @staticmethod
    def _digest(value: str, n: int = 12) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:n]

    def create_onramp_order(
        self,
        *,
        fiat_amount: float,
        fiat_currency: str,
        crypto_currency: str,
        wallet_address: str,
        blockchain: str,
        user_email: str,
    ) -> BanxaCreateOrderResult:
        if self.mock_mode:
            seq = self._next_mock_seq()
            fp = self._digest(
                f"onramp|{fiat_amount}|{fiat_currency}|{crypto_currency}|{wallet_address}|{blockchain}|{user_email}|{seq}"
            )
            oid = f"banxa_mock_{fp}"
            url = f"https://checkout.sandbox.banxa.com/?order_id={oid}"
            return BanxaCreateOrderResult(
                order_id=oid,
                checkout_url=url,
                status="pending",
                created_at=self._mock_stamp(seq),
            )

        raise NotImplementedError("Real Banxa calls not implemented yet. Set MOCK_MODE=true.")

    def create_offramp_order(
        self,
        *,
        crypto_amount: float,
        crypto_currency: str,
        fiat_currency: str,
        destination_reference: str,
        user_email: str,
    ) -> BanxaCreateOrderResult:
        if self.mock_mode:
            seq = self._next_mock_seq()
            fp = self._digest(
                f"offramp|{crypto_amount}|{crypto_currency}|{fiat_currency}|{destination_reference}|{user_email}|{seq}"
            )
            oid = f"banxa_mock_off_{fp}"
            url = f"https://checkout.sandbox.banxa.com/?order_id={oid}"
            return BanxaCreateOrderResult(
                order_id=oid,
                checkout_url=url,
                status="pending",
                created_at=self._mock_stamp(seq),
            )

        raise NotImplementedError("Real Banxa offramp calls not implemented yet. Set MOCK_MODE=true.")