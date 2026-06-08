"""Payout workflow API tests for Epic 13."""

from __future__ import annotations

from collections.abc import Generator
import os
from pathlib import Path
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

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

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path


def _bootstrap_payout_setup(client: TestClient) -> int:
    client.post("/workspaces", json={"name": "Acme Ops"})
    client.post("/treasury", json={})
    client.post("/treasury/transfers/simulate-deposit", json={"amount": 1000})
    recipient = client.post(
        "/recipients",
        json={
            "name": "Alice Chen",
            "wallet_address": "0x1111111111111111111111111111111111111111",
            "network": "base",
        },
    )
    return recipient.json()["id"]


def test_create_and_run_payout_workflow() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        recipient_id = _bootstrap_payout_setup(client)

        created = client.post(
            "/payout-workflows",
            json={
                "name": "Friday contractor payout",
                "recipient_id": recipient_id,
                "amount": 250,
                "schedule_cadence": "weekly",
                "schedule_day": "friday",
            },
        )
        assert created.status_code == 200
        payload = created.json()
        assert payload["enabled"] is True
        assert payload["schedule_label"] == "Every Friday"
        workflow_id = payload["id"]

        run = client.post(f"/payout-workflows/{workflow_id}/run")
        assert run.status_code == 200
        body = run.json()
        assert body["run"]["status"] == "completed"
        assert body["run"]["template_name"] == "contractor_payout"
        assert body["workflow"]["last_run_id"] == body["run"]["id"]

        treasury = client.get("/treasury")
        assert treasury.json()["balance"] == 750.0
    finally:
        os.unlink(db_path)


def test_run_blocked_when_workflow_disabled() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        recipient_id = _bootstrap_payout_setup(client)
        created = client.post(
            "/payout-workflows",
            json={"name": "Paused payout", "recipient_id": recipient_id, "amount": 50},
        )
        workflow_id = created.json()["id"]
        client.post(f"/payout-workflows/{workflow_id}/disable")
        run = client.post(f"/payout-workflows/{workflow_id}/run")
        assert run.status_code == 409
        assert run.json()["code"] == "PAYOUT_WORKFLOW_DISABLED"
    finally:
        os.unlink(db_path)


def test_run_blocked_on_insufficient_balance() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        recipient_id = _bootstrap_payout_setup(client)
        created = client.post(
            "/payout-workflows",
            json={"name": "Large payout", "recipient_id": recipient_id, "amount": 1500},
        )
        workflow_id = created.json()["id"]
        run = client.post(f"/payout-workflows/{workflow_id}/run")
        assert run.status_code == 409
        assert run.json()["code"] == "INSUFFICIENT_BALANCE"
    finally:
        os.unlink(db_path)


def test_main_app_mounts_payout_workflows_router() -> None:
    main_py = (Path(__file__).resolve().parents[1] / "main.py").read_text(encoding="utf-8")
    assert "from app.api.payout_workflows import router as payout_workflows_router" in main_py
    assert "app.include_router(payout_workflows_router)" in main_py


def test_create_blocked_without_treasury() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        client.post("/workspaces", json={"name": "Acme Ops"})
        recipient = client.post(
            "/recipients",
            json={
                "name": "Alice Chen",
                "wallet_address": "0x1111111111111111111111111111111111111111",
                "network": "base",
            },
        )
        res = client.post(
            "/payout-workflows",
            json={"name": "No treasury payout", "recipient_id": recipient.json()["id"], "amount": 50},
        )
        assert res.status_code == 409
        assert res.json()["code"] == "PAYOUT_WORKFLOW_GUARD"
    finally:
        os.unlink(db_path)


def test_run_blocked_when_recipient_inactive() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        recipient_id = _bootstrap_payout_setup(client)
        created = client.post(
            "/payout-workflows",
            json={"name": "Friday payout", "recipient_id": recipient_id, "amount": 50},
        )
        workflow_id = created.json()["id"]
        client.post(f"/recipients/{recipient_id}/deactivate")
        run = client.post(f"/payout-workflows/{workflow_id}/run")
        assert run.status_code == 409
        assert run.json()["code"] == "PAYOUT_WORKFLOW_GUARD"
    finally:
        os.unlink(db_path)


def test_deactivate_recipient_warns_when_linked_to_enabled_workflow() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        recipient_id = _bootstrap_payout_setup(client)
        client.post(
            "/payout-workflows",
            json={"name": "Friday payout", "recipient_id": recipient_id, "amount": 50},
        )
        deactivated = client.post(f"/recipients/{recipient_id}/deactivate")
        assert deactivated.status_code == 200
        body = deactivated.json()
        assert body["status"] == "inactive"
        assert body["workflow_warning"]
        assert "active payout workflow" in body["workflow_warning"]
    finally:
        os.unlink(db_path)


def test_contractor_payout_template_is_registered() -> None:
    from app.workflows.registry import get_template

    template = get_template("contractor_payout")
    assert template["category"] == "payout"
    assert "balance.check" in template["step_outline"]
