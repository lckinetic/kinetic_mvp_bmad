"""Recipient API contract tests for Sprint 3 (Epic 12)."""

from __future__ import annotations

from collections.abc import Generator
import os
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.api.recipients import router as recipients_router
from app.api.workspaces import get_db, router as workspaces_router
from app.core.config import Settings
from app.core.errors import register_error_handlers
from app.db import models  # noqa: F401


def _mk_settings(db_path: str) -> Settings:
    return Settings(
        database_url=f"sqlite:///{db_path}",
        mock_mode=True,
        ai_mock_mode=True,
        ai_provider="openai",
        ai_model="gpt-4o-mini",
        openai_api_key="",
        openai_base_url="https://api.openai.com/v1",
        ai_timeout_seconds=5.0,
        banxa_api_key="",
        banxa_api_secret="",
        banxa_env="sandbox",
        banxa_webhook_secret="",
        log_level="INFO",
    )


def _app_with_test_db() -> tuple[FastAPI, str]:
    fd, db_path = mkstemp(suffix=".sqlite3")
    os.close(fd)
    settings = _mk_settings(db_path)
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(workspaces_router)
    app.include_router(recipients_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path


def _bootstrap_workspace(client: TestClient) -> None:
    res = client.post("/workspaces", json={"name": "Acme Treasury Ops"})
    assert res.status_code == 200


def test_create_list_and_get_recipient() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)

        created = client.post(
            "/recipients",
            json={
                "name": "Alice Chen",
                "wallet_address": "0xAbCdEf0123456789AbCdEf0123456789AbCdEf01",
                "network": "base",
                "notes": "Design contractor",
            },
        )
        assert created.status_code == 200
        payload = created.json()
        assert payload["name"] == "Alice Chen"
        assert payload["status"] == "active"
        assert payload["wallet_address"].startswith("0xabcdef")
        assert payload["wallet_address_short"].startswith("0xabcd")

        listed = client.get("/recipients")
        assert listed.status_code == 200
        assert len(listed.json()["items"]) == 1

        fetched = client.get(f"/recipients/{payload['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["network_label"] == "Base"
    finally:
        os.unlink(db_path)


def test_recipient_validation_rejects_invalid_address() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)

        res = client.post(
            "/recipients",
            json={
                "name": "Bob",
                "wallet_address": "not-an-address",
                "network": "base",
            },
        )
        assert res.status_code == 400
        assert res.json()["code"] == "RECIPIENT_INVALID"
    finally:
        os.unlink(db_path)


def test_list_recipient_networks() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        res = client.get("/recipients/networks")
        assert res.status_code == 200
        labels = {row["id"]: row["label"] for row in res.json()["items"]}
        assert labels["base"] == "Base"
        assert labels["ethereum"] == "Ethereum"
    finally:
        os.unlink(db_path)


def test_recipient_duplicate_address_is_rejected() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)
        body = {
            "name": "Alice Chen",
            "wallet_address": "0x1111111111111111111111111111111111111111",
            "network": "base",
        }
        assert client.post("/recipients", json=body).status_code == 200
        dup = client.post("/recipients", json={**body, "name": "Alice Duplicate"})
        assert dup.status_code == 409
        assert dup.json()["code"] == "RECIPIENT_ALREADY_EXISTS"
    finally:
        os.unlink(db_path)


def test_recipient_duplicate_address_rejected_across_case() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)
        assert client.post(
            "/recipients",
            json={
                "name": "Alice Chen",
                "wallet_address": "0xAbCdEf0123456789AbCdEf0123456789AbCdEf01",
                "network": "base",
            },
        ).status_code == 200
        dup = client.post(
            "/recipients",
            json={
                "name": "Alice Duplicate",
                "wallet_address": "0xabcdef0123456789abcdef0123456789abcdef01",
                "network": "base",
            },
        )
        assert dup.status_code == 409
        assert dup.json()["code"] == "RECIPIENT_ALREADY_EXISTS"
    finally:
        os.unlink(db_path)


def test_update_deactivate_and_search_recipients() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)
        created = client.post(
            "/recipients",
            json={
                "name": "Charlie Ops",
                "wallet_address": "0x2222222222222222222222222222222222222222",
                "network": "ethereum",
            },
        )
        recipient_id = created.json()["id"]

        updated = client.patch(
            f"/recipients/{recipient_id}",
            json={"name": "Charlie Finance", "notes": "Monthly retainer"},
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Charlie Finance"
        assert updated.json()["notes"] == "Monthly retainer"

        search = client.get("/recipients", params={"search": "finance"})
        assert search.status_code == 200
        assert len(search.json()["items"]) == 1

        deactivated = client.post(f"/recipients/{recipient_id}/deactivate")
        assert deactivated.status_code == 200
        assert deactivated.json()["status"] == "inactive"

        active_only = client.get("/recipients")
        assert active_only.json()["items"] == []

        with_inactive = client.get("/recipients", params={"include_inactive": "true"})
        assert len(with_inactive.json()["items"]) == 1
    finally:
        os.unlink(db_path)


def test_recipient_payout_defaults_round_trip() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)

        created = client.post(
            "/recipients",
            json={
                "name": "Alice Chen",
                "wallet_address": "0xAbCdEf0123456789AbCdEf0123456789AbCdEf01",
                "network": "base",
                "default_payout_amount": 500,
                "default_schedule_cadence": "weekly",
                "default_schedule_day": "friday",
            },
        )
        assert created.status_code == 200
        payload = created.json()
        assert payload["default_payout_amount"] == 500
        assert payload["default_payout_asset"] == "USDC"
        assert payload["default_schedule_cadence"] == "weekly"
        assert payload["default_schedule_day"] == "friday"
        assert payload["default_schedule_label"] == "Every Friday"
    finally:
        os.unlink(db_path)
