"""Story 5-1: chat prompt returns a structured proposal artifact."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.assistant import router as assistant_router
from app.core.errors import register_error_handlers
from app.services import assistant_proposals as proposals_service


def _assistant_app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(assistant_router)
    return app


def test_create_proposal_returns_structured_artifact() -> None:
    client = TestClient(_assistant_app())
    res = client.post(
        "/assistant/proposals",
        json={"message": "Fund wallet with USDC", "session_id": "chat_demo"},
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["proposal_id"].startswith("prop_")
    assert payload["session_id"] == "chat_demo"
    assert payload["status"] == "proposed"
    assert payload["validation"]["is_valid"] is True
    assert isinstance(payload["workflow"]["steps"], list)
    assert payload["workflow"]["steps"]


def test_create_proposal_rejects_non_actionable_prompt() -> None:
    client = TestClient(_assistant_app())
    res = client.post("/assistant/proposals", json={"message": "1234"})
    assert res.status_code == 400
    payload = res.json()
    assert payload["code"] == "INVALID_PROMPT"
    assert "reason" in payload["details"]


def test_get_proposal_by_id_after_creation() -> None:
    client = TestClient(_assistant_app())
    created = client.post("/assistant/proposals", json={"message": "Create wallet for me"})
    assert created.status_code == 200
    proposal_id = created.json()["proposal_id"]

    fetched = client.get(f"/assistant/proposals/{proposal_id}")
    assert fetched.status_code == 200
    payload = fetched.json()
    assert payload["proposal_id"] == proposal_id
    assert payload["workflow"]["workflow_name"]


def test_get_proposal_unknown_id_returns_not_found_envelope() -> None:
    client = TestClient(_assistant_app())
    res = client.get("/assistant/proposals/prop_missing")
    assert res.status_code == 404
    payload = res.json()
    assert payload["code"] == "NOT_FOUND"
    assert payload["message"] == "Assistant proposal not found"


def test_concurrent_same_prompt_returns_same_proposal_id() -> None:
    proposals_service._PROPOSALS.clear()
    message = "Create wallet for me"
    session_id = "chat_concurrent"

    def _create() -> str:
        proposal = proposals_service.create_proposal(message=message, session_id=session_id)
        return proposal["proposal_id"]

    with ThreadPoolExecutor(max_workers=8) as executor:
        proposal_ids = list(executor.map(lambda _: _create(), range(16)))

    assert len(set(proposal_ids)) == 1
    assert len(proposals_service._PROPOSALS) == 1


def test_concurrent_same_prompt_different_sessions_produce_distinct_proposals() -> None:
    proposals_service._PROPOSALS.clear()
    message = "Create wallet for me"
    session_ids = [f"chat_session_{i}" for i in range(8)]

    def _create(session_id: str) -> str:
        proposal = proposals_service.create_proposal(message=message, session_id=session_id)
        return proposal["proposal_id"]

    with ThreadPoolExecutor(max_workers=8) as executor:
        proposal_ids = list(executor.map(_create, session_ids))

    assert len(set(proposal_ids)) == len(session_ids)
    assert len(proposals_service._PROPOSALS) == len(session_ids)
