"""AI payout draft API tests for Epic 16."""

from __future__ import annotations

from collections.abc import Generator
import os
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from pathlib import Path

import app.api.ai as ai_api
from app.api.ai import router as ai_router
from app.api.payout_workflows import router as payout_workflows_router
from app.api.recipients import router as recipients_router
from app.api.treasury import router as treasury_router
from app.api.workspaces import get_db, router as workspaces_router
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.db import engine as db_engine
from app.db import models  # noqa: F401
import app.workflows  # noqa: F401


def _mk_settings(db_path: str, *, ai_mock_mode: bool = True) -> Settings:
    return Settings(
        database_url=f"sqlite:///{db_path}",
        mock_mode=True,
        ai_mock_mode=ai_mock_mode,
        ai_provider="openai",
        ai_model="gpt-4o-mini",
        openai_api_key="test-key",
        openai_base_url="https://api.openai.com/v1",
        ai_timeout_seconds=5.0,
        banxa_api_key="",
        banxa_api_secret="",
        banxa_env="sandbox",
        banxa_webhook_secret="",
        log_level="INFO",
    )


def _app_with_test_db(*, ai_mock_mode: bool = True) -> tuple[FastAPI, str]:
    fd, db_path = mkstemp(suffix=".sqlite3")
    os.close(fd)
    settings = _mk_settings(db_path, ai_mock_mode=ai_mock_mode)
    db_engine._engine = None
    engine = create_engine(settings.database_url)
    db_engine._engine = engine
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(workspaces_router)
    app.include_router(recipients_router)
    app.include_router(treasury_router)
    app.include_router(payout_workflows_router)
    app.include_router(ai_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[ai_api.get_db] = _get_db_override
    app.dependency_overrides[get_settings] = lambda: settings
    return app, db_path


def _bootstrap_alice(client: TestClient) -> int:
    client.post("/workspaces", json={"name": "Acme Ops"})
    recipient = client.post(
        "/recipients",
        json={
            "name": "Alice Chen",
            "wallet_address": "0x1111111111111111111111111111111111111111",
            "network": "base",
        },
    )
    return recipient.json()["id"]


def test_payout_draft_mock_parses_alice_friday_prompt() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_alice(client)
        res = client.post("/ai/payout-draft", json={"message": "Pay Alice 50 USDC every Friday"})
        assert res.status_code == 200
        payload = res.json()
        assert payload["draft_type"] == "contractor_payout"
        assert payload["amount"] == 50.0
        assert payload["asset"] == "USDC"
        assert payload["schedule_cadence"] == "weekly"
        assert payload["schedule_day"] == "friday"
        assert payload["recipient_name"] == "Alice"
        assert payload["recipient_resolved"] is True
        assert payload["recipient"]["name"] == "Alice Chen"
        assert payload["meta"]["mock_mode"] is True
        assert payload["meta"]["source"] == "mock"
    finally:
        db_engine._engine = None
        os.remove(db_path)


def test_payout_draft_roster_prompt_requires_manual_recipient() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_alice(client)
        res = client.post(
            "/ai/payout-draft",
            json={"message": "Pay my contractor roster every Friday in USDC"},
        )
        assert res.status_code == 200
        payload = res.json()
        assert payload["schedule_cadence"] == "weekly"
        assert payload["schedule_day"] == "friday"
        assert payload["recipient_resolved"] is False
        assert any("Select a recipient" in warning for warning in payload["warnings"])
    finally:
        db_engine._engine = None
        os.remove(db_path)


def test_payout_draft_recipient_picker_override() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        alice_id = _bootstrap_alice(client)
        res = client.post(
            "/ai/payout-draft",
            json={
                "message": "Pay my contractor roster every Friday in USDC",
                "recipient_id": alice_id,
            },
        )
        assert res.status_code == 200
        payload = res.json()
        assert payload["recipient_resolved"] is True
        assert payload["recipient_id"] == alice_id
    finally:
        db_engine._engine = None
        os.remove(db_path)


def test_payout_draft_mock_parses_bob_monthly_prompt() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        client.post("/workspaces", json={"name": "Acme Ops"})
        client.post(
            "/recipients",
            json={
                "name": "Bob Rivera",
                "wallet_address": "0x2222222222222222222222222222222222222222",
                "network": "base",
            },
        )
        res = client.post(
            "/ai/payout-draft",
            json={"message": "Send 100 USDC to Bob on the 1st of each month"},
        )
        assert res.status_code == 200
        payload = res.json()
        assert payload["amount"] == 100.0
        assert payload["asset"] == "USDC"
        assert payload["schedule_cadence"] == "monthly"
        assert payload["schedule_day"] == "1"
        assert payload["recipient_name"] == "Bob"
        assert payload["recipient_resolved"] is True
        assert payload["recipient"]["name"] == "Bob Rivera"
    finally:
        db_engine._engine = None
        os.remove(db_path)


def test_payout_draft_ambiguous_recipient_requires_manual_selection() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        client.post("/workspaces", json={"name": "Acme Ops"})
        client.post(
            "/recipients",
            json={
                "name": "Alice Chen",
                "wallet_address": "0x1111111111111111111111111111111111111111",
                "network": "base",
            },
        )
        client.post(
            "/recipients",
            json={
                "name": "Alice Smith",
                "wallet_address": "0x3333333333333333333333333333333333333333",
                "network": "base",
            },
        )
        res = client.post("/ai/payout-draft", json={"message": "Pay Alice 50 USDC every Friday"})
        assert res.status_code == 200
        payload = res.json()
        assert payload["recipient_resolved"] is False
        assert any("Multiple recipients match" in warning for warning in payload["warnings"])
    finally:
        db_engine._engine = None
        os.remove(db_path)


def test_save_payout_draft_creates_workflow_definition() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_alice(client)
        client.post("/treasury", json={})
        draft = client.post("/ai/payout-draft", json={"message": "Pay Alice 50 USDC every Friday"})
        assert draft.status_code == 200
        body = draft.json()
        saved = client.post(
            "/payout-workflows",
            json={
                "name": body["name"],
                "recipient_id": body["recipient_id"],
                "amount": body["amount"],
                "asset": body["asset"],
                "schedule_cadence": body["schedule_cadence"],
                "schedule_day": body["schedule_day"],
            },
        )
        assert saved.status_code == 200
        workflow = saved.json()
        assert workflow["recipient"]["name"] == "Alice Chen"
        assert workflow["amount"] == 50.0
        assert workflow["schedule_cadence"] == "weekly"
        assert workflow["schedule_day"] == "friday"
    finally:
        db_engine._engine = None
        os.remove(db_path)


def test_main_app_mounts_ai_router() -> None:
    main_py = (Path(__file__).resolve().parents[1] / "main.py").read_text(encoding="utf-8")
    assert "from app.api.ai import router as ai_router" in main_py
    assert "app.include_router(ai_router)" in main_py


def test_payout_draft_failure_returns_sanitized_error_envelope(monkeypatch) -> None:
    class _ExplodingService:
        def generate_payout_draft(self, _message: str):
            raise RuntimeError("boom test-key")

    monkeypatch.setattr(ai_api, "get_ai_service", lambda _settings: _ExplodingService())
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_alice(client)
        res = client.post("/ai/payout-draft", json={"message": "Pay Alice 50 USDC every Friday"})
        assert res.status_code == 502
        payload = res.json()
        assert payload["code"] == "AI_PAYOUT_DRAFT_FAILED"
        assert payload["message"] == "AI payout draft generation failed"
        assert "test-key" not in str(payload)
    finally:
        db_engine._engine = None
        os.remove(db_path)


def test_capabilities_reports_payout_draft_support() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        res = client.get("/ai/capabilities")
        assert res.status_code == 200
        assert res.json()["payout_draft_supported"] is True
    finally:
        db_engine._engine = None
        os.remove(db_path)
