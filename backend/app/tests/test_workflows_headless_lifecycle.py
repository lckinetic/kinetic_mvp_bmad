"""Story 2-2: headless list/start/poll lifecycle over HTTP."""

from __future__ import annotations

from collections.abc import Generator
import os
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.api.workflows import get_db, router as workflows_router
from app.core.config import Settings
from app.db import models  # noqa: F401  # ensure metadata is registered


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


def _app_with_test_db() -> tuple[FastAPI, str]:
    fd, db_path = mkstemp(suffix=".sqlite3")
    os.close(fd)
    settings = _mk_settings(db_path)
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(workflows_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path


def test_headless_lifecycle_list_start_poll() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)

        templates_res = client.get("/workflows/templates")
        assert templates_res.status_code == 200
        templates = templates_res.json()
        assert isinstance(templates, list) and templates

        template_names = {t["name"] for t in templates}
        assert "managed_treasury" in template_names

        run_res = client.post(
            "/workflows/run/managed_treasury",
            json={"input": {"user_email": "demo@example.com", "trade_symbol": "BTC-USD", "trade_amount": 100}},
        )
        assert run_res.status_code == 200
        run = run_res.json()
        assert run["status"] in {"completed", "failed"}
        assert run["template_name"] == "managed_treasury"
        run_id = run["id"]

        poll_res = client.get(f"/workflows/runs/{run_id}")
        assert poll_res.status_code == 200
        polled = poll_res.json()
        assert polled["id"] == run_id
        assert polled["status"] == run["status"]

        list_res = client.get("/workflows/runs")
        assert list_res.status_code == 200
        runs = list_res.json()
        assert any(r["id"] == run_id for r in runs)
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
