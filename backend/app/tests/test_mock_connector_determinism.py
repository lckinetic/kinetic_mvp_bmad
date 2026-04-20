from __future__ import annotations

from app.adapters.banxa.client import BanxaClient
from app.adapters.coinbase.client import CoinbaseClient
from app.adapters.privy.client import PrivyClient


def test_banxa_mock_is_deterministic_for_call_sequence() -> None:
    a = BanxaClient(mock_mode=True)
    b = BanxaClient(mock_mode=True)

    args = dict(
        fiat_amount=1000,
        fiat_currency="GBP",
        crypto_currency="USDC",
        wallet_address="0xDEMO",
        blockchain="ethereum",
        user_email="demo@example.com",
    )

    r1a = a.create_onramp_order(**args)
    r1b = b.create_onramp_order(**args)
    r2a = a.create_onramp_order(**args)
    r2b = b.create_onramp_order(**args)

    assert r1a.order_id == r1b.order_id
    assert r2a.order_id == r2b.order_id
    assert r1a.order_id != r2a.order_id


def test_privy_and_coinbase_mock_outputs_are_deterministic() -> None:
    p1, p2 = PrivyClient(mock_mode=True), PrivyClient(mock_mode=True)
    c1, c2 = CoinbaseClient(mock_mode=True), CoinbaseClient(mock_mode=True)

    w1a = p1.create_wallet(user_email="demo@example.com")
    w1b = p2.create_wallet(user_email="demo@example.com")
    assert w1a.wallet_id == w1b.wallet_id
    assert w1a.address == w1b.address

    t1a = c1.place_trade(symbol="BTC-USD", side="buy", amount=100.0)
    t1b = c2.place_trade(symbol="BTC-USD", side="buy", amount=100.0)
    assert t1a.trade_id == t1b.trade_id

    wd1a = c1.withdraw_crypto(amount=50.0, currency="USDC", crypto_address="0xabc")
    wd1b = c2.withdraw_crypto(amount=50.0, currency="USDC", crypto_address="0xabc")
    assert wd1a["withdrawal_id"] == wd1b["withdrawal_id"]


def test_banxa_mock_timestamp_is_monotonic_beyond_sixty_calls() -> None:
    client = BanxaClient(mock_mode=True)
    args = dict(
        fiat_amount=1000,
        fiat_currency="GBP",
        crypto_currency="USDC",
        wallet_address="0xDEMO",
        blockchain="ethereum",
        user_email="demo@example.com",
    )

    stamps = [client.create_onramp_order(**args).created_at for _ in range(65)]
    assert stamps[0] < stamps[-1]
    assert len(set(stamps)) == len(stamps)
