from __future__ import annotations

from app.core.config import Settings
from app.core.logging import safe_settings_log
from app.core.secrets_redact import redact_database_url, redact_secrets_in_text


def test_redact_database_url_masks_password() -> None:
    url = "postgresql+psycopg2://kinetic:supersecret@localhost:5432/kinetic"
    out = redact_database_url(url)
    assert "supersecret" not in out
    assert "kinetic:***" in out or ":***@" in out


def test_safe_settings_log_masks_database_url_and_secrets() -> None:
    row = safe_settings_log(
        {
            "MOCK_MODE": True,
            "DATABASE_URL": "postgresql://u:passw@db:5432/app",
            "BANXA_API_KEY": "key123",
            "BANXA_API_SECRET": "sec456",
            "BANXA_WEBHOOK_SECRET": "whsec",
            "BANXA_ENV": "sandbox",
        }
    )
    assert "passw" not in str(row["DATABASE_URL"])
    assert row["BANXA_API_KEY"] == "***"
    assert row["BANXA_API_SECRET"] == "***"
    assert row["BANXA_WEBHOOK_SECRET"] == "***"
    assert row["BANXA_ENV"] == "sandbox"


def test_redact_secrets_in_text_strips_configured_values() -> None:
    settings = Settings(
        database_url="postgresql://u:dbpass@localhost/db",
        mock_mode=True,
        banxa_api_key="ak_live_xyz",
        banxa_api_secret="",
        banxa_env="sandbox",
        banxa_webhook_secret="whook",
        log_level="INFO",
    )
    raw = "Request failed: ak_live_xyz and whook and dbpass"
    out = redact_secrets_in_text(raw, settings)
    assert "ak_live_xyz" not in out
    assert "whook" not in out
    assert "dbpass" not in out
    assert "***" in out
