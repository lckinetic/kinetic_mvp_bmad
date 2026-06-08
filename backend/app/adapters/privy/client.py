from __future__ import annotations

from dataclasses import dataclass
import hashlib


@dataclass
class PrivyWallet:
    wallet_id: str
    address: str
    network: str = "base"


@dataclass
class PrivyBalance:
    asset: str
    amount: float
    network: str


class PrivyClient:
    """
    Privy adapter with deterministic mock behaviour for demo-safe treasury flows.
    Live Privy API integration is deferred to a later sprint.
    """

    def __init__(self, *, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self._mock_seq = 0

    def _next_mock_seq(self) -> int:
        self._mock_seq += 1
        return self._mock_seq

    def create_wallet(self, *, user_email: str) -> PrivyWallet:
        """Create a mock self-custodial wallet for a user (legacy workflow path)."""
        seq = self._next_mock_seq()
        fp = hashlib.sha256(f"{user_email}|{seq}".encode("utf-8")).hexdigest()
        wallet_id = f"privy_wallet_{fp[:12]}"
        address = f"0x{fp[:40]}"
        return PrivyWallet(wallet_id=wallet_id, address=address)

    def create_treasury_wallet(
        self,
        *,
        workspace_id: int,
        label: str,
        network: str = "base",
    ) -> PrivyWallet:
        """Create a treasury wallet scoped to a workspace."""
        if not self.mock_mode:
            raise NotImplementedError("Live Privy treasury wallet creation is not configured yet.")

        fp = hashlib.sha256(f"treasury|{workspace_id}|{label}|{network}".encode("utf-8")).hexdigest()
        wallet_id = f"privy_treasury_{fp[:12]}"
        address = f"0x{fp[:40]}"
        return PrivyWallet(wallet_id=wallet_id, address=address, network=network)

    def get_balance(self, *, address: str, asset: str = "USDC", network: str = "base") -> PrivyBalance:
        """Read wallet balance. Mock mode returns zero unless caller supplies ledger balance."""
        if not self.mock_mode:
            raise NotImplementedError("Live Privy balance reads are not configured yet.")
        return PrivyBalance(asset=asset, amount=0.0, network=network)
