"""Story 2-1: workflow surfaces appear in OpenAPI with request/response schemas."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.workflows import router as workflows_router


def _workflows_app() -> FastAPI:
    app = FastAPI()
    app.include_router(workflows_router)
    return app


def test_openapi_lists_workflow_list_start_status_paths() -> None:
    client = TestClient(_workflows_app())
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json()["paths"]
    assert "/workflows/templates" in paths
    get_templates = paths["/workflows/templates"]["get"]
    assert "200" in get_templates["responses"]
    ref = get_templates["responses"]["200"]["content"]["application/json"]["schema"]
    assert ref.get("type") == "array"
    assert "#/components/schemas/" in ref["items"]["$ref"]

    assert "/workflows/run/{template_name}" in paths
    post_run = paths["/workflows/run/{template_name}"]["post"]
    assert "requestBody" in post_run
    body = post_run["requestBody"]["content"]["application/json"]["schema"]
    assert "$ref" in body
    assert "RunWorkflowRequest" in body["$ref"]

    assert "/workflows/runs" in paths
    assert "/workflows/runs/{run_id}" in paths
    assert "/workflows/runs/{run_id}/steps" in paths
    assert "/workflows/runs/{run_id}/inspection" in paths


def test_openapi_component_schemas_include_workflow_models() -> None:
    client = TestClient(_workflows_app())
    spec = client.get("/openapi.json").json()
    names = set(spec["components"]["schemas"].keys())
    assert "WorkflowRunResponse" in names
    assert "RunWorkflowRequest" in names
    assert "WorkflowTemplateSummary" in names
    assert "WorkflowTemplateDetail" in names
    assert "WorkflowRunStepResponse" in names
    assert "WorkflowRunInspectionResponse" in names
    assert "WorkflowWebhookEventResponse" in names
