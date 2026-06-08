"""Alerts API tests for Epic 15."""

from __future__ import annotations

from collections.abc import Generator
import os
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from pathlib import Path

from app.api.activity import router as activity_router
from app.api.alerts import router as alerts_router
from app.api.payout_workflows import router as payout_workflows_router
from app.api.recipients import router as recipients_router
from app.api.treasury import router as treasury_router
from app.api.workspaces import get_db, router as workspaces_router
from app.core.config import Settings
from app.core.errors import register_error_handlers
from app.db import models  # noqa: F401
import app.workflows  # noqa: F401


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
    app.include_router(treasury_router)
    app.include_router(recipients_router)
    app.include_router(payout_workflows_router)
    app.include_router(alerts_router)
    app.include_router(activity_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path


def _bootstrap(client: TestClient) -> tuple[int, int]:
    client.post("/workspaces", json={"name": "Acme Ops"})
    client.post("/treasury", json={})
    client.post("/treasury/transfers/simulate-deposit", json={"amount": 100})
    recipient = client.post(
        "/recipients",
        json={
            "name": "Alice Chen",
            "wallet_address": "0x1111111111111111111111111111111111111111",
            "network": "base",
        },
    )
    workflow = client.post(
        "/payout-workflows",
        json={"name": "Large payout", "recipient_id": recipient.json()["id"], "amount": 250},
    )
    return recipient.json()["id"], workflow.json()["id"]


def test_insufficient_balance_creates_open_alert() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _, workflow_id = _bootstrap(client)

        run = client.post(f"/payout-workflows/{workflow_id}/run")
        assert run.status_code == 409
        assert run.json()["code"] == "INSUFFICIENT_BALANCE"

        alerts = client.get("/alerts", params={"status": "open"})
        assert alerts.status_code == 200
        items = alerts.json()["items"]
        assert len(items) == 1
        assert items[0]["alert_type"] == "insufficient_balance"
        assert items[0]["recovery_action"] == "fund_treasury"
    finally:
        os.unlink(db_path)


def test_acknowledge_alert_deemphasizes_prominence() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _, workflow_id = _bootstrap(client)
        client.post(f"/payout-workflows/{workflow_id}/run")

        alert_id = client.get("/alerts").json()["items"][0]["id"]
        ack = client.post(f"/alerts/{alert_id}/acknowledge")
        assert ack.status_code == 200
        assert ack.json()["status"] == "acknowledged"
        assert ack.json()["is_prominent"] is False
    finally:
        os.unlink(db_path)


def test_main_app_mounts_alerts_router() -> None:
    main_py = (Path(__file__).resolve().parents[1] / "main.py").read_text(encoding="utf-8")
    assert "from app.api.alerts import router as alerts_router" in main_py
    assert "app.include_router(alerts_router)" in main_py


def test_disabled_workflow_creates_alert() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _, workflow_id = _bootstrap(client)
        client.post(f"/payout-workflows/{workflow_id}/disable")

        run = client.post(f"/payout-workflows/{workflow_id}/run")
        assert run.status_code == 409
        assert run.json()["code"] == "PAYOUT_WORKFLOW_DISABLED"

        alerts = client.get("/alerts", params={"status": "open"})
        assert alerts.json()["items"][0]["alert_type"] == "workflow.disabled"
    finally:
        os.unlink(db_path)


def test_inactive_recipient_creates_recipient_invalid_alert() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        recipient_id, workflow_id = _bootstrap(client)
        client.post(f"/recipients/{recipient_id}/deactivate")

        run = client.post(f"/payout-workflows/{workflow_id}/run")
        assert run.status_code == 409
        assert run.json()["code"] == "RECIPIENT_INACTIVE"

        alerts = client.get("/alerts", params={"status": "open"})
        assert alerts.json()["items"][0]["alert_type"] == "recipient.invalid"
    finally:
        os.unlink(db_path)


def test_insufficient_balance_creates_blocked_activity_event() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _, workflow_id = _bootstrap(client)
        client.post(f"/payout-workflows/{workflow_id}/run")

        activity = client.get("/activity")
        assert activity.status_code == 200
        blocked = [row for row in activity.json()["items"] if row["event_type"] == "payout.blocked"]
        assert len(blocked) == 1
        assert blocked[0]["payload"]["block_reason"] == "insufficient_balance"
    finally:
        os.unlink(db_path)


def test_simulate_failed_payout_creates_transfer_failed_alert() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        client.post("/workspaces", json={"name": "Acme Ops"})
        client.post("/treasury", json={})

        failed = client.post("/treasury/transfers/simulate-failed-payout", json={"amount": 25})
        assert failed.status_code == 200
        assert failed.json()["transfer"]["status"] == "failed"

        alerts = client.get("/alerts", params={"status": "open"})
        assert alerts.json()["items"][0]["alert_type"] == "transfer.failed"
    finally:
        os.unlink(db_path)


def test_successful_run_resolves_workflow_alerts() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _, workflow_id = _bootstrap(client)
        client.post(f"/payout-workflows/{workflow_id}/run")
        client.post("/treasury/transfers/simulate-deposit", json={"amount": 500})

        client.post(f"/payout-workflows/{workflow_id}/run")
        open_alerts = client.get("/alerts", params={"status": "open"})
        assert open_alerts.json()["items"] == []
    finally:
        os.unlink(db_path)
