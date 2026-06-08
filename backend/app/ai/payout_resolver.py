from __future__ import annotations

from typing import Any

from sqlmodel import Session

from app.services.recipient_service import RecipientNotFoundError, get_recipient, list_recipients


def resolve_recipient_for_draft(
    db: Session,
    *,
    recipient_name: str | None,
    recipient_id: int | None = None,
) -> dict[str, Any]:
    warnings: list[str] = []

    if recipient_id is not None:
        try:
            recipient = get_recipient(db, recipient_id=recipient_id)
        except RecipientNotFoundError:
            warnings.append("Selected recipient was not found. Pick a recipient before saving.")
            return {
                "recipient_id": None,
                "recipient": None,
                "recipient_resolved": False,
                "warnings": warnings,
            }
        warnings.append(f"Recipient selected: {recipient['name']}")
        return {
            "recipient_id": recipient["id"],
            "recipient": recipient,
            "recipient_resolved": True,
            "warnings": warnings,
        }

    if not recipient_name:
        warnings.append("No recipient name found in prompt. Select a recipient before saving.")
        return {
            "recipient_id": None,
            "recipient": None,
            "recipient_resolved": False,
            "warnings": warnings,
        }

    items = list_recipients(db)
    needle = recipient_name.strip().lower()
    if not needle:
        warnings.append("No recipient name found in prompt. Select a recipient before saving.")
        return {
            "recipient_id": None,
            "recipient": None,
            "recipient_resolved": False,
            "warnings": warnings,
        }

    exact = [row for row in items if row["name"].lower() == needle]
    if len(exact) == 1:
        recipient = exact[0]
        warnings.append(f"Matched recipient: {recipient['name']}")
        return {
            "recipient_id": recipient["id"],
            "recipient": recipient,
            "recipient_resolved": True,
            "warnings": warnings,
        }

    partial = [
        row
        for row in items
        if needle in row["name"].lower() or row["name"].lower().startswith(needle)
    ]
    if len(partial) == 1:
        recipient = partial[0]
        warnings.append(f"Matched recipient: {recipient['name']}")
        return {
            "recipient_id": recipient["id"],
            "recipient": recipient,
            "recipient_resolved": True,
            "warnings": warnings,
        }
    if len(partial) > 1:
        warnings.append(f"Multiple recipients match '{recipient_name}'. Select one manually.")
        return {
            "recipient_id": None,
            "recipient": None,
            "recipient_resolved": False,
            "warnings": warnings,
        }

    first_token = needle.split()[0]
    first_matches = [row for row in items if row["name"].lower().split()[0] == first_token]
    if len(first_matches) == 1:
        recipient = first_matches[0]
        warnings.append(f"Matched recipient by first name: {recipient['name']}")
        return {
            "recipient_id": recipient["id"],
            "recipient": recipient,
            "recipient_resolved": True,
            "warnings": warnings,
        }
    if len(first_matches) > 1:
        warnings.append(f"Multiple recipients match first name '{first_token}'. Select one manually.")
        return {
            "recipient_id": None,
            "recipient": None,
            "recipient_resolved": False,
            "warnings": warnings,
        }

    warnings.append(f"No recipient found for '{recipient_name}'. Add them or pick manually.")
    return {
        "recipient_id": None,
        "recipient": None,
        "recipient_resolved": False,
        "warnings": warnings,
    }
