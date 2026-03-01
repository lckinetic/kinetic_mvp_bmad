from __future__ import annotations

from sqlmodel import Session, select

from app.db.models import Order, utcnow



ALLOWED_STATUSES = {"pending", "processing", "completed", "failed", "cancelled"}
TERMINAL_STATES = {"completed", "failed", "cancelled"}


def normalise_status(raw: str | None) -> str | None:
    if not raw:
        return None
    s = str(raw).strip().lower()
    mapping = {
        "success": "completed",
        "succeeded": "completed",
        "complete": "completed",
        "completed": "completed",
        "processing": "processing",
        "in_progress": "processing",
        "in progress": "processing",
        "pending": "pending",
        "failed": "failed",
        "error": "failed",
        "cancelled": "cancelled",
        "canceled": "cancelled",
    }
    s = mapping.get(s, s)
    return s if s in ALLOWED_STATUSES else None


def apply_order_status_update(
    *,
    db: Session,
    provider: str,
    direction: str,
    order_id: str,
    raw_status: str,
) -> Order | None:
    """
    Internal lifecycle updater used by workflow templates (no HTTP).
    Enforces terminal-state protection and normalisation.
    """
    direction = (direction or "onramp").strip().lower()
    if direction not in {"onramp", "offramp"}:
        direction = "onramp"

    stmt = select(Order).where(
        Order.provider == provider,
        Order.direction == direction,
        Order.order_id == str(order_id),
    )
    order = db.exec(stmt).first()
    if not order:
        return None

    new_status = normalise_status(raw_status)
    if not new_status:
        return order

    current = (order.order_status or "").strip().lower()
    if current in TERMINAL_STATES:
        return order

    order.order_status = new_status
    order.updated_at = utcnow()
    if new_status in TERMINAL_STATES:
        order.completed_at = utcnow()

    db.add(order)
    db.commit()
    db.refresh(order)
    return order
