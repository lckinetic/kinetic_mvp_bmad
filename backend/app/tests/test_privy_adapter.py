"""Privy adapter mock behaviour tests."""

from __future__ import annotations

from app.adapters.privy.client import PrivyClient


def test_create_treasury_wallet_is_deterministic() -> None:
    client = PrivyClient(mock_mode=True)
    first = client.create_treasury_wallet(workspace_id=7, label="Acme Treasury Ops")
    second = client.create_treasury_wallet(workspace_id=7, label="Acme Treasury Ops")
    assert first.wallet_id == second.wallet_id
    assert first.address == second.address
    assert first.network == "base"


def test_create_wallet_legacy_path_differs_from_treasury() -> None:
    client = PrivyClient(mock_mode=True)
    legacy = client.create_wallet(user_email="ops@acme.test")
    treasury = client.create_treasury_wallet(workspace_id=1, label="Acme")
    assert legacy.address != treasury.address
