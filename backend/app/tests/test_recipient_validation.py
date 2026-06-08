"""Recipient validation unit tests."""

from __future__ import annotations

import pytest

from app.services.recipient_service import (
    RecipientValidationError,
    validate_recipient_fields,
)


def test_validate_recipient_fields_accepts_valid_payload() -> None:
    fields = validate_recipient_fields(
        name="Alice Chen",
        wallet_address="0xAbCdEf0123456789AbCdEf0123456789AbCdEf01",
        network="base",
        notes="Contractor",
    )
    assert fields["network"] == "base"
    assert fields["notes"] == "Contractor"
    assert fields["wallet_address"] == "0xabcdef0123456789abcdef0123456789abcdef01"


def test_validate_recipient_fields_normalizes_address_case() -> None:
    fields = validate_recipient_fields(
        name="Alice Chen",
        wallet_address="0xABCDEF0123456789ABCDEF0123456789ABCDEF01",
        network="base",
    )
    assert fields["wallet_address"] == "0xabcdef0123456789abcdef0123456789abcdef01"


def test_validate_recipient_fields_rejects_bad_network() -> None:
    with pytest.raises(RecipientValidationError, match="Network must be one of"):
        validate_recipient_fields(
            name="Alice",
            wallet_address="0xAbCdEf0123456789AbCdEf0123456789AbCdEf01",
            network="solana",
        )


def test_validate_recipient_fields_rejects_short_address() -> None:
    with pytest.raises(RecipientValidationError, match="valid EVM address"):
        validate_recipient_fields(
            name="Alice",
            wallet_address="0x1234",
            network="base",
        )
