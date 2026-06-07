"""Workspace API contract tests for Sprint 1."""

from __future__ import annotations

from collections.abc import Generator
import os
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

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

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path


def test_create_and_get_current_workspace() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        create = client.post("/workspaces", json={"name": "Acme Treasury Ops"})
        assert create.status_code == 200
        payload = create.json()
        assert payload["name"] == "Acme Treasury Ops"
        assert isinstance(payload["id"], int)

        current = client.get("/workspaces/current")
        assert current.status_code == 200
        assert current.json()["id"] == payload["id"]
    finally:
        os.unlink(db_path)


def test_get_current_workspace_returns_404_when_missing() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        res = client.get("/workspaces/current")
        assert res.status_code == 404
        body = res.json()
        assert body["code"] == "WORKSPACE_NOT_FOUND"
    finally:
        os.unlink(db_path)


def test_create_workspace_rejects_empty_name() -> None:
    app, db_path = _app_with_test_db()
    try:
        client = TestClient(app)
        res = client.post("/workspaces", json={"name": "   "})
        assert res.status_code == 400
        body = res.json()
        assert body["code"] in {"WORKSPACE_INVALID", "VALIDATION_ERROR", "BAD_REQUEST"}
    finally:
        os.unlink(db_path)
