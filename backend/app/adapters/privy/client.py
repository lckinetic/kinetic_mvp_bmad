from __future__ import annotations

from dataclasses import dataclass
import hashlib


@dataclass
class PrivyWallet:
    wallet_id: str
    address: str


class PrivyClient:
    """
    Mock Privy adapter (MVP version).
    Later this will wrap real Privy API calls.
    """

    def __init__(self, *, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self._mock_seq = 0

    def _next_mock_seq(self) -> int:
        self._mock_seq += 1
        return self._mock_seq

    def create_wallet(self, *, user_email: str) -> PrivyWallet:
        """
        Create a mock self-custodial wallet for a user.
        In real implementation this would call Privy API.
        """
        seq = self._next_mock_seq()
        fp = hashlib.sha256(f"{user_email}|{seq}".encode("utf-8")).hexdigest()
        wallet_id = f"privy_wallet_{fp[:12]}"
        address = f"0x{fp[:40]}"

        return PrivyWallet(
            wallet_id=wallet_id,
            address=address,
        )