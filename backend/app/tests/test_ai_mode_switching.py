from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.ai as ai_api
from app.api.ai import router as ai_router
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers


def _mock_settings(*, mock_mode: bool) -> Settings:
    return Settings(
        database_url="sqlite:///./test.sqlite3",
        mock_mode=mock_mode,
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


def _ai_app(*, mock_mode: bool) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(ai_router)
    app.dependency_overrides[get_settings] = lambda: _mock_settings(mock_mode=mock_mode)
    return app


def test_ai_capabilities_reports_mock_mode() -> None:
    client = TestClient(_ai_app(mock_mode=True))
    res = client.get("/ai/capabilities")
    assert res.status_code == 200
    payload = res.json()
    assert payload["mock_mode"] is True
    assert payload["provider"] == "mock"
    assert payload["model"] == "rule-based"


def test_ai_config_status_never_returns_api_key_value() -> None:
    client = TestClient(_ai_app(mock_mode=False))
    res = client.get("/ai/config-status")
    assert res.status_code == 200
    payload = res.json()
    assert payload["mock_mode"] is False
    assert payload["provider"] == "openai"
    assert payload["model"] == "gpt-4o-mini"
    assert payload["openai_api_key_configured"] is True
    assert "openai_api_key" not in payload
    assert "test-key" not in str(payload)


def test_ai_interpret_returns_meta_for_mock_mode() -> None:
    client = TestClient(_ai_app(mock_mode=True))
    res = client.post("/ai/interpret", json={"message": "Create a wallet for me"})
    assert res.status_code == 200
    payload = res.json()
    assert "workflow_name" in payload
    assert isinstance(payload.get("steps"), list) and payload["steps"]
    meta = payload["meta"]
    assert meta["mock_mode"] is True
    assert meta["source"] == "mock"


def test_ai_interpret_failure_returns_sanitized_error_envelope(monkeypatch) -> None:
    class _ExplodingService:
        def generate_workflow(self, _message: str):
            raise RuntimeError("boom test-key")

    monkeypatch.setattr(ai_api, "get_ai_service", lambda _settings: _ExplodingService())
    client = TestClient(_ai_app(mock_mode=False))
    res = client.post("/ai/interpret", json={"message": "Create wallet for me"})
    assert res.status_code == 502
    payload = res.json()
    assert payload["code"] == "AI_INTERPRET_FAILED"
    assert payload["message"] == "AI workflow interpretation failed"
    assert "test-key" not in str(payload)
