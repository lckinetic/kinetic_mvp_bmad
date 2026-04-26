"""Story 6-1: support can inspect failed runs with linked webhook events."""

from __future__ import annotations

from collections.abc import Generator
import os
from tempfile import mkstemp
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.api.workflows import get_db, router as workflows_router
from app.core.config import Settings
from app.core.errors import register_error_handlers
from app.db import models  # noqa: F401  # ensure metadata registered
from app.db.models import WebhookEvent, WorkflowRun, WorkflowStep


def _mk_settings(db_path: str) -> Settings:
    return Settings(
        database_url=f"sqlite:///{db_path}",
        mock_mode=True,
        banxa_api_key="",
        banxa_api_secret="",
        banxa_env="sandbox",
        banxa_webhook_secret="",
        log_level="INFO",
    )


def _app_with_test_db() -> tuple[FastAPI, str, Any]:
    fd, db_path = mkstemp(suffix=".sqlite3")
    os.close(fd)
    settings = _mk_settings(db_path)
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(workflows_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path, engine


def test_failed_run_inspection_includes_steps_and_linked_webhooks() -> None:
    app, db_path, engine = _app_with_test_db()
    try:
        client = TestClient(app)
        with Session(engine) as db:
            run = WorkflowRun(
                template_name="managed_treasury",
                status="failed",
                input={"user_email": "ops@example.com"},
                output={"onramp_order_id": "order_abc123"},
                error="Provider timeout",
            )
            db.add(run)
            db.commit()
            db.refresh(run)

            step = WorkflowStep(
                run_id=run.id,
                seq=1,
                step_name="onramp.create",
                status="failed",
                data={"order_id": "order_abc123"},
                error="onramp failed",
            )
            db.add(step)

            webhook = WebhookEvent(
                provider="banxa",
                direction="onramp",
                event_type="order.failed",
                order_id="order_abc123",
                payload={"order": {"id": "order_abc123"}, "status": "failed"},
                processed=True,
                idempotency_key="evt_abc123",
            )
            db.add(webhook)
            db.commit()
            run_id = run.id

        res = client.get(f"/workflows/runs/{run_id}/inspection")
        assert res.status_code == 200
        payload = res.json()

        assert payload["run"]["id"] == run_id
        assert payload["run"]["status"] == "failed"
        assert payload["steps"][0]["step_name"] == "onramp.create"
        assert "order_abc123" in payload["linked_order_ids"]
        assert len(payload["webhook_events"]) == 1
        assert payload["webhook_events"][0]["order_id"] == "order_abc123"
        assert payload["webhook_events"][0]["event_type"] == "order.failed"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
