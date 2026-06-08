"""Activity Centre API tests for Epic 14."""

from __future__ import annotations

from collections.abc import Generator
import os
from pathlib import Path
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.api.activity import router as activity_router
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
    app.include_router(activity_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path


def _bootstrap_and_run_payout(client: TestClient) -> None:
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
    workflow = client.post(
        "/payout-workflows",
        json={"name": "Friday payout", "recipient_id": recipient.json()["id"], "amount": 200},
    )
    client.post(f"/payout-workflows/{workflow.json()['id']}/run")


def test_main_app_mounts_activity_router() -> None:
    main_py = (Path(__file__).resolve().parents[1] / "main.py").read_text(encoding="utf-8")
    assert "from app.api.activity import router as activity_router" in main_py
    assert "app.include_router(activity_router)" in main_py


def test_list_activity_event_types() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        res = client.get("/activity/event-types")
        assert res.status_code == 200
        labels = {row["id"]: row["label"] for row in res.json()["items"]}
        assert labels["payout.completed"] == "Payout completed"
        assert labels["workflow.run_completed"] == "Workflow run completed"
    finally:
        os.unlink(db_path)


def test_activity_feed_after_treasury_and_payout_operations() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_and_run_payout(client)

        feed = client.get("/activity")
        assert feed.status_code == 200
        items = feed.json()["items"]
        assert len(items) >= 3
        event_types = {item["event_type"] for item in items}
        assert "treasury.deposit" in event_types
        assert "treasury.payout" in event_types
        assert "payout.completed" in event_types

        payout_event = next(item for item in items if item["event_type"] == "payout.completed")
        detail = client.get(f"/activity/{payout_event['id']}")
        assert detail.status_code == 200
        links = detail.json()["links"]
        assert links.get("recipient_id")
        assert links.get("run_id")
    finally:
        os.unlink(db_path)


def test_activity_filters_by_event_type() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        _bootstrap_and_run_payout(client)

        filtered = client.get("/activity", params={"event_type": "payout.completed"})
        assert filtered.status_code == 200
        items = filtered.json()["items"]
        assert len(items) == 1
        assert items[0]["event_type"] == "payout.completed"
    finally:
        os.unlink(db_path)
