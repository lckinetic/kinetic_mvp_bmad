"""Story 2-3: structured error envelope on workflow API surfaces."""

from __future__ import annotations

from collections.abc import Generator
import os
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.api.workflows import get_db, router as workflows_router
from app.core.config import Settings
from app.core.errors import _default_http_message, register_error_handlers
from app.db import models  # noqa: F401  # ensure metadata is registered


def _mk_settings(db_path: str) -> Settings:
    return Settings(
        database_url=f"sqlite:///{db_path}",
        mock_mode=True,
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
    app.include_router(workflows_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path


def test_not_found_uses_standard_error_envelope() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        res = client.get("/workflows/runs/999999")
        assert res.status_code == 404
        payload = res.json()
        assert payload["code"] == "NOT_FOUND"
        assert payload["message"] == "Workflow run not found"
        assert "details" in payload
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_invalid_input_uses_standard_error_envelope() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        res = client.post("/workflows/run/managed_treasury", json={"input": {}})
        assert res.status_code == 400
        payload = res.json()
        assert payload["code"] == "BAD_REQUEST"
        assert "required" in payload["message"].lower()
        assert "details" in payload
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_default_http_message_falls_back_for_unknown_status_codes() -> None:
    assert _default_http_message(499) == "HTTP error"
