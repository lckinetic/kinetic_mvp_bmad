"""Story 5-1: assistant proposal endpoints appear in OpenAPI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.assistant import router as assistant_router


def _assistant_app() -> FastAPI:
    app = FastAPI()
    app.include_router(assistant_router)
    return app


def test_openapi_lists_assistant_proposal_routes_and_schemas() -> None:
    client = TestClient(_assistant_app())
    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    payload = spec.json()

    paths = payload["paths"]
    assert "/assistant/proposals" in paths
    assert "/assistant/proposals/{proposal_id}" in paths
    assert "/assistant/proposals/{proposal_id}/confirm" in paths
    assert "/assistant/proposals/{proposal_id}/execute" in paths

    post_proposals = paths["/assistant/proposals"]["post"]
    assert "requestBody" in post_proposals
    req_schema = post_proposals["requestBody"]["content"]["application/json"]["schema"]
    assert "AssistantProposalRequest" in req_schema["$ref"]

    components = payload["components"]["schemas"]
    assert "AssistantProposalRequest" in components
    assert "AssistantProposalResponse" in components
    assert "AssistantProposalValidation" in components
