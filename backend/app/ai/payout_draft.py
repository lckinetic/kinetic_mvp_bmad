from __future__ import annotations

import re
from typing import Any

WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
SUPPORTED_ASSETS = ("USDC", "USDT")
SUPPORTED_CADENCES = ("manual", "weekly", "monthly")
RECIPIENT_STOPWORDS = {"my", "the", "a", "every", "all", "contractor", "team", "roster", "usdc", "usdt"}


def _extract_monthly_day(text: str) -> str:
    patterns = (
        r"\b(\d{1,2})(?:st|nd|rd|th)\s+of\s+(?:each|the)\s+month",
        r"(?:on\s+the\s+|on\s+day\s+|day\s+)(\d{1,2})(?:st|nd|rd|th)?(?:\s+of\s+(?:each|the)\s+month|\s+monthly)?",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            day = int(match.group(1))
            if 1 <= day <= 28:
                return str(day)
    return "1"


def _extract_recipient_name(original: str, text: str) -> str | None:
    cap_match = re.search(
        r"\b(?:pay|send)\s+(?:my\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
        original,
    )
    if cap_match:
        return cap_match.group(1).strip()

    low_match = re.search(r"\b(?:pay|send)\s+(?:my\s+)?([a-z]+)\b", text)
    if low_match:
        token = low_match.group(1)
        if token not in RECIPIENT_STOPWORDS and token not in WEEKDAYS:
            return token.capitalize()

    to_cap = re.search(r"\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", original)
    if to_cap:
        return to_cap.group(1).strip()

    to_low = re.search(r"\bto\s+([a-z]+)\b", text)
    if to_low:
        token = to_low.group(1)
        if token not in RECIPIENT_STOPWORDS and token not in WEEKDAYS:
            return token.capitalize()

    return None


def normalize_payout_draft(payload: dict[str, Any]) -> dict[str, Any]:
    cadence = str(payload.get("schedule_cadence") or "manual").strip().lower()
    if cadence not in SUPPORTED_CADENCES:
        cadence = "manual"

    schedule_day = payload.get("schedule_day")
    normalized_day: str | None = None
    if cadence == "weekly":
        day = str(schedule_day or "friday").strip().lower()
        normalized_day = day if day in WEEKDAYS else "friday"
    elif cadence == "monthly":
        day_text = str(schedule_day or "1").strip().lower()
        normalized_day = day_text if day_text.isdigit() and 1 <= int(day_text) <= 28 else "1"
    else:
        cadence = "manual"
        normalized_day = None

    asset = str(payload.get("asset") or "USDC").strip().upper()
    if asset not in SUPPORTED_ASSETS:
        asset = "USDC"

    amount_raw = payload.get("amount", 50)
    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        amount = 50.0
    if amount <= 0:
        amount = 50.0

    recipient_name = payload.get("recipient_name")
    if recipient_name is not None:
        recipient_name = str(recipient_name).strip() or None

    name = str(payload.get("name") or "Contractor payout").strip() or "Contractor payout"
    summary = str(payload.get("summary") or "Generated contractor payout workflow draft.").strip()

    return {
        "draft_type": "contractor_payout",
        "name": name[:120],
        "summary": summary,
        "recipient_name": recipient_name,
        "recipient_id": None,
        "recipient": None,
        "recipient_resolved": False,
        "amount": amount,
        "asset": asset,
        "schedule_cadence": cadence,
        "schedule_day": normalized_day,
        "warnings": [],
        "source_message": str(payload.get("source_message") or "").strip(),
    }


def parse_payout_draft_mock(message: str) -> dict[str, Any]:
    """Deterministic NL → hero payout draft for demo prompts."""
    original = (message or "").strip()
    text = original.lower()

    amount = 50.0
    amount_match = re.search(r"(\d+(?:\.\d+)?)", original)
    if amount_match:
        amount = float(amount_match.group(1))

    asset = "USDT" if "usdt" in text else "USDC"

    cadence = "manual"
    schedule_day: str | None = None
    for day in WEEKDAYS:
        if day in text:
            cadence = "weekly"
            schedule_day = day
            break
    if "monthly" in text or "each month" in text or "every month" in text:
        cadence = "monthly"
        schedule_day = _extract_monthly_day(text)
    elif "every week" in text or " weekly" in text:
        cadence = "weekly"
        schedule_day = schedule_day or "friday"

    recipient_name = _extract_recipient_name(original, text)

    if "roster" in text or "contractors" in text:
        recipient_name = None

    if recipient_name and schedule_day and cadence == "weekly":
        name = f"{recipient_name} {asset} {schedule_day} payout"
    elif recipient_name and cadence == "monthly":
        name = f"{recipient_name} {asset} monthly payout"
    elif schedule_day and cadence == "weekly":
        name = f"Contractor {asset} {schedule_day} payout"
    else:
        name = f"{asset} contractor payout"

    summary_subject = recipient_name or "contractors"
    summary = f"Pay {summary_subject} {amount:g} {asset}"
    if cadence == "weekly" and schedule_day:
        summary += f" every {schedule_day}"
    elif cadence == "monthly" and schedule_day:
        summary += f" monthly on day {schedule_day}"
    summary += "."

    return normalize_payout_draft(
        {
            "name": name,
            "summary": summary,
            "recipient_name": recipient_name,
            "amount": amount,
            "asset": asset,
            "schedule_cadence": cadence,
            "schedule_day": schedule_day,
            "source_message": original,
        }
    )
