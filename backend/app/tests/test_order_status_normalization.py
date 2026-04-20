from __future__ import annotations

from datetime import datetime, timezone
import os
from tempfile import mkstemp
from types import SimpleNamespace

from sqlmodel import Session, SQLModel, create_engine

from app.db import models  # noqa: F401  # ensure metadata registration
from app.services.order_status import normalize_order_status, normalize_order_status_or_default
from app.services.orders.offramp_service import create_offramp_order
from app.services.orders.onramp_service import create_onramp_order


class _FakeBanxa:
    def __init__(self, *, status: str):
        self._status = status

    def create_onramp_order(self, **_kwargs):
        return SimpleNamespace(
            order_id="banxa_1",
            checkout_url="https://checkout.example/order/banxa_1",
            status=self._status,
            created_at=datetime.now(timezone.utc),
        )

    def create_offramp_order(self, **_kwargs):
        return SimpleNamespace(
            order_id="banxa_2",
            checkout_url="https://checkout.example/order/banxa_2",
            status=self._status,
            created_at=datetime.now(timezone.utc),
        )


def _session() -> tuple[Session, str]:
    fd, db_path = mkstemp(suffix=".sqlite3")
    os.close(fd)
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    return Session(engine), db_path


def test_normalize_order_status_mapping() -> None:
    assert normalize_order_status("SUCCESS") == "completed"
    assert normalize_order_status("in_progress") == "processing"
    assert normalize_order_status("canceled") == "cancelled"
    assert normalize_order_status("weird_vendor_state") is None
    assert normalize_order_status_or_default("weird_vendor_state") == "pending"


def test_onramp_persists_only_canonical_status() -> None:
    db, db_path = _session()
    try:
        order = create_onramp_order(
            db=db,
            banxa=_FakeBanxa(status="SUCCESS"),  # type: ignore[arg-type]
            fiat_amount=1000,
            fiat_currency="GBP",
            crypto_currency="USDC",
            wallet_address="0xDEMO",
            blockchain="ethereum",
            user_email="demo@example.com",
        )
        assert order.order_status == "completed"
    finally:
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_offramp_unknown_status_falls_back_to_pending() -> None:
    db, db_path = _session()
    try:
        order = create_offramp_order(
            db=db,
            banxa=_FakeBanxa(status="vendor_unknown_state"),  # type: ignore[arg-type]
            crypto_amount=100,
            crypto_currency="USDC",
            fiat_currency="GBP",
            destination_reference="demo-bank-001",
            user_email="demo@example.com",
        )
        assert order.order_status == "pending"
    finally:
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)
