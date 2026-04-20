from __future__ import annotations

from typing import Optional

CANONICAL_ORDER_STATUSES = {
    "pending",
    "processing",
    "completed",
    "failed",
    "cancelled",
}

_STATUS_MAPPING = {
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


def normalize_order_status(raw: object) -> Optional[str]:
    """Return canonical order status, or None when raw value is unusable."""
    if raw is None:
        return None
    value = str(raw).strip().lower()
    if not value:
        return None
    normalized = _STATUS_MAPPING.get(value, value)
    return normalized if normalized in CANONICAL_ORDER_STATUSES else None


def normalize_order_status_or_default(raw: object, default: str = "pending") -> str:
    """Normalize status, falling back to a canonical default."""
    normalized = normalize_order_status(raw)
    if normalized:
        return normalized
    return default if default in CANONICAL_ORDER_STATUSES else "pending"
