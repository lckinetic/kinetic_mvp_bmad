"""Treasury API contract tests for Sprint 2."""

from __future__ import annotations

from collections.abc import Generator
import os
from tempfile import mkstemp

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.api.treasury import router as treasury_router
from app.api.workspaces import get_db, router as workspaces_router
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.db import models  # noqa: F401


def _mk_settings(db_path: str, *, mock_mode: bool = True) -> Settings:
    return Settings(
        database_url=f"sqlite:///{db_path}",
        mock_mode=mock_mode,
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


def _app_with_test_db(*, mock_mode: bool = True) -> tuple[FastAPI, str]:
    fd, db_path = mkstemp(suffix=".sqlite3")
    os.close(fd)
    settings = _mk_settings(db_path, mock_mode=mock_mode)
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(workspaces_router)
    app.include_router(treasury_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_settings] = lambda: settings
    return app, db_path


def _bootstrap_workspace(client: TestClient) -> None:
    res = client.post("/workspaces", json={"name": "Acme Treasury Ops"})
    assert res.status_code == 200


def test_create_and_get_treasury() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)

        missing = client.get("/treasury")
        assert missing.status_code == 404
        assert missing.json()["code"] == "TREASURY_NOT_FOUND"

        created = client.post("/treasury", json={"name": "Ops Treasury"})
        assert created.status_code == 200
        payload = created.json()
        assert payload["name"] == "Ops Treasury"
        assert payload["asset"] == "USDC"
        assert payload["balance"] == 0.0
        assert payload["wallet"]["address"].startswith("0x")
        assert payload["funding"]["warning"]

        current = client.get("/treasury")
        assert current.status_code == 200
        assert current.json()["id"] == payload["id"]
    finally:
        os.unlink(db_path)


def test_create_treasury_is_idempotent_per_workspace() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)

        first = client.post("/treasury", json={})
        assert first.status_code == 200

        second = client.post("/treasury", json={})
        assert second.status_code == 409
        assert second.json()["code"] == "TREASURY_ALREADY_EXISTS"
    finally:
        os.unlink(db_path)


def test_simulate_deposit_and_transfer_history() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)
        client.post("/treasury", json={})

        deposit = client.post("/treasury/transfers/simulate-deposit", json={"amount": 500})
        assert deposit.status_code == 200
        body = deposit.json()
        assert body["treasury"]["balance"] == 500.0
        assert body["transfer"]["direction"] == "inbound"
        assert body["transfer"]["status"] == "completed"

        transfers = client.get("/treasury/transfers")
        assert transfers.status_code == 200
        items = transfers.json()["items"]
        assert len(items) == 1
        assert items[0]["amount"] == 500.0
    finally:
        os.unlink(db_path)


def test_main_app_mounts_treasury_router() -> None:
    main_py = (Path(__file__).resolve().parents[1] / "main.py").read_text(encoding="utf-8")
    assert "from app.api.treasury import router as treasury_router" in main_py
    assert "app.include_router(treasury_router)" in main_py


def test_create_treasury_rejects_live_mode_without_provider() -> None:
    app, db_path = _app_with_test_db(mock_mode=False)
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)

        res = client.post("/treasury", json={})
        assert res.status_code == 501
        assert res.json()["code"] == "TREASURY_PROVIDER_NOT_CONFIGURED"
    finally:
        os.unlink(db_path)


def test_balance_check_reports_insufficient_funds() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_workspace(client)
        client.post("/treasury", json={})

        res = client.post("/treasury/balance/check", json={"amount": 100})
        assert res.status_code == 409
        body = res.json()
        assert body["code"] == "INSUFFICIENT_BALANCE"
        assert body["details"]["shortfall"] == 100.0

        client.post("/treasury/transfers/simulate-deposit", json={"amount": 250})
        ok = client.post("/treasury/balance/check", json={"amount": 100})
        assert ok.status_code == 200
        assert ok.json()["sufficient"] is True
    finally:
        os.unlink(db_path)
