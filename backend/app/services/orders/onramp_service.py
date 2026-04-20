from __future__ import annotations

from sqlmodel import Session, select

from app.db.models import Order, utcnow
from app.services.banxa_client import BanxaClient
from app.services.order_status import normalize_order_status_or_default

from sqlmodel import select
from sqlalchemy.exc import IntegrityError


def create_onramp_order(
    *,
    db: Session,
    banxa: BanxaClient,
    fiat_amount: float,
    fiat_currency: str,
    crypto_currency: str,
    wallet_address: str,
    blockchain: str,
    user_email: str,
    client_reference: str | None = None,
) -> Order:
    if client_reference:
        client_reference = client_reference.strip()

        stmt = select(Order).where(
            Order.provider == "banxa",
            Order.direction == "onramp",
            Order.client_reference == client_reference,
        )
        existing = db.exec(stmt).first()
        if existing:
            return existing

    result = banxa.create_onramp_order(
        fiat_amount=fiat_amount,
        fiat_currency=fiat_currency,
        crypto_currency=crypto_currency,
        wallet_address=wallet_address,
        blockchain=blockchain,
        user_email=user_email,
    )

    order = Order(
        provider="banxa",
        direction="onramp",
        order_id=result.order_id,
        client_reference=client_reference,
        order_status=normalize_order_status_or_default(result.status),
        user_email=user_email,
        fiat_amount=fiat_amount,
        fiat_currency=fiat_currency,
        crypto_currency=crypto_currency,
        wallet_address=wallet_address,
        blockchain=blockchain,
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
            # Another request inserted the same client_reference first — return that row
            stmt = select(Order).where(
                Order.provider == "banxa",
                Order.direction == "onramp",
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


def get_onramp_order_by_order_id(db: Session, order_id: str) -> Order | None:
    stmt = select(Order).where(Order.direction == "onramp", Order.order_id == order_id)
    return db.exec(stmt).first()
