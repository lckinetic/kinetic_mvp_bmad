from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field as PydField
from sqlmodel import Session, select

from app.core.config import get_settings, Settings
from app.db.engine import get_engine
from app.db.models import Order
from app.services.banxa_client import BanxaClient
from app.services.offramp_service import create_offramp_order, get_offramp_order_by_order_id


router = APIRouter(prefix="/offramp", tags=["offramp"])


def get_db(settings: Settings = Depends(get_settings)):
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session


def get_banxa(settings: Settings = Depends(get_settings)) -> BanxaClient:
    return BanxaClient(mock_mode=settings.mock_mode)


class CreateOfframpOrderRequest(BaseModel):
    crypto_amount: float = PydField(gt=0)
    crypto_currency: str = PydField(min_length=2, max_length=10)
    fiat_currency: str = PydField(min_length=3, max_length=10)
    destination_reference: str = PydField(min_length=2, max_length=200)
    user_email: EmailStr
    client_reference: Optional[str] = PydField(default=None, max_length=100)


class OfframpOrderResponse(BaseModel):
    order_id: str
    checkout_url: Optional[str] = None
    order_status: str

    user_email: str
    client_reference: Optional[str] = None

    crypto_amount: Optional[float] = None
    crypto_currency: Optional[str] = None
    fiat_currency: Optional[str] = None
    destination_reference: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None


def _to_response(o: Order) -> OfframpOrderResponse:
    return OfframpOrderResponse(
        order_id=o.order_id,
        checkout_url=o.checkout_url,
        order_status=o.order_status,
        user_email=o.user_email,
        client_reference=o.client_reference,
        crypto_amount=o.crypto_amount,
        crypto_currency=o.crypto_currency,
        fiat_currency=o.fiat_currency,
        destination_reference=o.destination_reference,
        created_at=o.created_at.isoformat() if o.created_at else None,
        updated_at=o.updated_at.isoformat() if o.updated_at else None,
        completed_at=o.completed_at.isoformat() if o.completed_at else None,
    )


@router.post("/orders", response_model=OfframpOrderResponse)
def create_order(
    req: CreateOfframpOrderRequest,
    db: Session = Depends(get_db),
    banxa: BanxaClient = Depends(get_banxa),
):
    order = create_offramp_order(
        db=db,
        banxa=banxa,
        crypto_amount=req.crypto_amount,
        crypto_currency=req.crypto_currency,
        fiat_currency=req.fiat_currency,
        destination_reference=req.destination_reference,
        user_email=str(req.user_email),
        client_reference=req.client_reference,
    )
    return _to_response(order)


@router.get("/orders/{order_id}", response_model=OfframpOrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    order = get_offramp_order_by_order_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _to_response(order)


@router.get("/orders", response_model=List[OfframpOrderResponse])
def find_orders(
    client_reference: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if not client_reference:
        raise HTTPException(status_code=400, detail="client_reference is required for MVP search")

    stmt = (
        select(Order)
        .where(Order.provider == "banxa")
        .where(Order.direction == "offramp")
        .where(Order.client_reference == client_reference)
        .order_by(Order.id.desc())
        .limit(20)
    )
    rows = db.exec(stmt).all()
    return [_to_response(o) for o in rows]
