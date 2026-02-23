from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.models import Order, utcnow
from app.services.banxa_client import BanxaClient


def create_offramp_order(
    *,
    db: Session,
    banxa: BanxaClient,
    crypto_amount: float,
    crypto_currency: str,
    fiat_currency: str,
    destination_reference: str,
    user_email: str,
    client_reference: str | None = None,
) -> Order:
    """
    MVP Offramp order creation.
    - MOCK_MODE: creates a mock Banxa offramp order and persists it.
    - Idempotent when client_reference is provided (unique per provider+direction+client_reference).
    """
    if client_reference:
        client_reference = client_reference.strip()

        stmt = select(Order).where(
            Order.provider == "banxa",
            Order.direction == "offramp",
            Order.client_reference == client_reference,
        )
        existing = db.exec(stmt).first()
        if existing:
            return existing

    result = banxa.create_offramp_order(
        crypto_amount=crypto_amount,
        crypto_currency=crypto_currency,
        fiat_currency=fiat_currency,
        destination_reference=destination_reference,
        user_email=user_email,
    )

    order = Order(
        provider="banxa",
        direction="offramp",
        order_id=result.order_id,
        client_reference=client_reference,
        order_status=result.status,
        user_email=user_email,
        crypto_amount=crypto_amount,
        crypto_currency=crypto_currency,
        fiat_currency=fiat_currency,
        destination_reference=destination_reference,
        checkout_url=result.checkout_url,
        created_at=result.created_at,
        updated_at=utcnow(),
    )

    db.add(order)

    if client_reference:
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            stmt = select(Order).where(
                Order.provider == "banxa",
                Order.direction == "offramp",
                Order.client_reference == client_reference,
            )
            existing = db.exec(stmt).first()
            if existing:
                return existing
            raise
    else:
        db.commit()

    db.refresh(order)
    return order


def get_offramp_order_by_order_id(*, db: Session, order_id: str) -> Order | None:
    stmt = select(Order).where(
        Order.provider == "banxa",
        Order.direction == "offramp",
        Order.order_id == order_id,
    )
    return db.exec(stmt).first()
