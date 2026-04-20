from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import get_settings, Settings
from app.db.engine import get_engine
from app.db.models import WebhookEvent, Order
from app.services.order_status import CANONICAL_ORDER_STATUSES, normalize_order_status


# internal status
ALLOWED_STATUSES = CANONICAL_ORDER_STATUSES
TERMINAL_STATES = {"completed", "failed", "cancelled"}


# internal and external status mapping
def normalise_status(payload: dict) -> str | None:
    """
    Extract a status from webhook payload and normalise it to our MVP status set.
    Returns None if no usable status found.
    """
    raw = payload.get("status") or payload.get("order_status") or payload.get("orderStatus")
    return normalize_order_status(raw)


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def get_db(settings: Settings = Depends(get_settings)):
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session


def _canonical_json(payload: Dict[str, Any]) -> str:
    # stable representation for idempotency key and signing
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def _compute_signature(secret: str, body: str) -> str:
    return hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()


def _parse_json_body(body: bytes) -> Dict[str, Any]:
    """Parse JSON from raw body, handling BOM and common encoding issues."""
    text = body.decode("utf-8", errors="replace")
    text = text.strip()
    if text.startswith("\ufeff"):
        text = text[1:]
    # Replace smart/curly quotes that break JSON
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    return json.loads(text)


@router.post("/banxa")
async def banxa_webhook(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    x_banxa_signature: Optional[str] = Header(default=None),
    x_idempotency_key: Optional[str] = Header(default=None),
):
    body = await request.body()
    try:
        payload = _parse_json_body(body) if body else {}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {e!s}")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON body must be an object")

    canonical = _canonical_json(payload)

    # 1) Basic signature check (skip in MOCK_MODE unless you want to test it)
    if not settings.mock_mode:
        if not settings.banxa_webhook_secret:
            raise HTTPException(status_code=500, detail="BANXA_WEBHOOK_SECRET not configured")
        if not x_banxa_signature:
            raise HTTPException(status_code=400, detail="Missing X-BANXA-SIGNATURE header")

        expected = _compute_signature(settings.banxa_webhook_secret, canonical)
        if not hmac.compare_digest(expected, x_banxa_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # 2) Idempotency key
    # Prefer header; otherwise derive from payload (MVP-safe)
    idem = x_idempotency_key or hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # 3) Extract minimal fields (Banxa payload shapes vary; keep it defensive)
    event_type = str(payload.get("event") or payload.get("type") or "unknown")
    order_id = payload.get("order_id") or payload.get("orderId") or payload.get("id")

    # Option 2: Use payload.direction if present, default to onramp (demo-friendly)
    direction = str(payload.get("direction") or "onramp").strip().lower()
    if direction not in {"onramp", "offramp"}:
        direction = "onramp"

    # 4) Store webhook event (unique constraint enforces idempotency)
    event = WebhookEvent(
        provider="banxa",
        direction=direction,
        event_type=event_type,
        order_id=str(order_id) if order_id else None,
        payload=payload,
        idempotency_key=idem,
        processed=False,
    )

    try:
        db.add(event)
        db.commit()
        db.refresh(event)
    except IntegrityError:
        # likely unique constraint hit (duplicate webhook)
        db.rollback()
        return {"status": "duplicate_ignored", "idempotency_key": idem}

    # 5) Update order status if order exists
    order = None
    if order_id:
        stmt = select(Order).where(
            Order.order_id == str(order_id),
            Order.direction == direction,
        )
        order = db.exec(stmt).first()

    if order:
        new_status = normalise_status(payload)

        # Don't overwrite terminal states
        if new_status:
            if (order.order_status or "").lower() in TERMINAL_STATES:
                # already terminal; keep it stable
                pass
            else:
                order.order_status = new_status
                order.updated_at = event.received_at

                if new_status in TERMINAL_STATES:
                    order.completed_at = event.received_at

                db.add(order)
                db.commit()

    event.processed = True
    db.add(event)
    db.commit()

    return {"status": "received", "idempotency_key": idem}


@router.get("/banxa/events")
def list_banxa_events(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 200))  # keep it bounded
    stmt = select(WebhookEvent).where(WebhookEvent.provider == "banxa").order_by(WebhookEvent.id.desc()).limit(limit)
    return db.exec(stmt).all()