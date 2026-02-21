from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field as PydField
from sqlmodel import Session

from app.core.config import get_settings, Settings
from app.db.engine import get_engine
from app.db.models import Order
from app.services.banxa_client import BanxaClient
from app.services.onramp_service import create_onramp_order, get_onramp_order_by_order_id
from typing import Optional
from sqlmodel import select

router = APIRouter(prefix="/onramp", tags=["onramp"])


def get_db(settings: Settings = Depends(get_settings)):
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session


class CreateOnrampOrderRequest(BaseModel):
    fiat_amount: float = PydField(gt=0)
    fiat_currency: str = PydField(min_length=3, max_length=10)
    crypto_currency: str = PydField(min_length=2, max_length=10)
    wallet_address: str = PydField(min_length=4, max_length=200)
    blockchain: str = PydField(min_length=2, max_length=50)
    user_email: EmailStr
    client_reference: str | None = PydField(default=None, max_length=100)


class OnrampOrderResponse(BaseModel):
    order_id: str
    checkout_url: str | None
    order_status: str
    fiat_amount: float
    fiat_currency: str
    crypto_currency: str
    wallet_address: str
    blockchain: str
    created_at: datetime


@router.post("/orders", response_model=OnrampOrderResponse)
def create_order(
    req: CreateOnrampOrderRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    banxa = BanxaClient(mock_mode=settings.mock_mode)

    order = create_onramp_order(
        db=db,
        banxa=banxa,
        fiat_amount=req.fiat_amount,
        fiat_currency=req.fiat_currency.upper(),
        crypto_currency=req.crypto_currency.upper(),
        wallet_address=req.wallet_address,
        blockchain=req.blockchain.lower(),
        user_email=str(req.user_email).lower(),
        client_reference=req.client_reference,
    )

    return OnrampOrderResponse(
        order_id=order.order_id,
        checkout_url=order.checkout_url,
        order_status=order.order_status,
        fiat_amount=order.fiat_amount,
        fiat_currency=order.fiat_currency,
        crypto_currency=order.crypto_currency,
        wallet_address=order.wallet_address,
        blockchain=order.blockchain,
        created_at=order.created_at,
    )


@router.get("/orders/{order_id}", response_model=OnrampOrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = get_onramp_order_by_order_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OnrampOrderResponse(
        order_id=order.order_id,
        checkout_url=order.checkout_url,
        order_status=order.order_status,
        fiat_amount=order.fiat_amount,
        fiat_currency=order.fiat_currency,
        crypto_currency=order.crypto_currency,
        wallet_address=order.wallet_address,
        blockchain=order.blockchain,
        created_at=order.created_at,
    )

from typing import Optional
from sqlmodel import select

@router.get("/orders")
def find_orders(
    client_reference: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if not client_reference:
        raise HTTPException(status_code=400, detail="client_reference is required for MVP search")

    stmt = (
        select(Order)
        .where(Order.direction == "onramp")
        .where(Order.client_reference == client_reference)
        .order_by(Order.id.desc())
        .limit(20)
    )
    rows = db.exec(stmt).all()

    return [
        OnrampOrderResponse(
            order_id=o.order_id,
            checkout_url=o.checkout_url,
            order_status=o.order_status,
            fiat_amount=o.fiat_amount,
            fiat_currency=o.fiat_currency,
            crypto_currency=o.crypto_currency,
            wallet_address=o.wallet_address,
            blockchain=o.blockchain,
            created_at=o.created_at,
        )
        for o in rows
    ]