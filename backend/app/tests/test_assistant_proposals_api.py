"""Stories 5-1/5-2: assistant proposals API behavior."""

from __future__ import annotations

from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
import os
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from app.api.assistant import get_db, router as assistant_router
from app.core.config import Settings
from app.core.errors import register_error_handlers
from app.db import models  # noqa: F401  # ensure metadata registration
from app.db.models import AssistantProposal


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


def _assistant_app() -> tuple[FastAPI, str]:
    fd, db_path = mkstemp(suffix=".sqlite3")
    os.close(fd)
    settings = _mk_settings(db_path)
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(assistant_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path


def test_create_proposal_returns_structured_artifact() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
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
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_create_proposal_rejects_non_actionable_prompt() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        res = client.post("/assistant/proposals", json={"message": "1234"})
        assert res.status_code == 400
        payload = res.json()
        assert payload["code"] == "INVALID_PROMPT"
        assert "reason" in payload["details"]
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_proposal_by_id_after_creation() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        created = client.post("/assistant/proposals", json={"message": "Create wallet for me"})
        assert created.status_code == 200
        proposal_id = created.json()["proposal_id"]

        fetched = client.get(f"/assistant/proposals/{proposal_id}")
        assert fetched.status_code == 200
        payload = fetched.json()
        assert payload["proposal_id"] == proposal_id
        assert payload["workflow"]["workflow_name"]
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_proposal_unknown_id_returns_not_found_envelope() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        res = client.get("/assistant/proposals/prop_missing")
        assert res.status_code == 404
        payload = res.json()
        assert payload["code"] == "NOT_FOUND"
        assert payload["message"] == "Assistant proposal not found"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_execute_requires_confirmation_first() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        created = client.post("/assistant/proposals", json={"message": "Create wallet for me"})
        proposal_id = created.json()["proposal_id"]

        blocked = client.post(f"/assistant/proposals/{proposal_id}/execute")
        assert blocked.status_code == 409
        payload = blocked.json()
        assert payload["code"] == "CONFIRMATION_REQUIRED"
        assert "reason" in payload["details"]
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_confirm_then_execute_succeeds() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        created = client.post("/assistant/proposals", json={"message": "Fund wallet with USDC"})
        proposal_id = created.json()["proposal_id"]

        confirmed = client.post(f"/assistant/proposals/{proposal_id}/confirm")
        assert confirmed.status_code == 200
        confirm_payload = confirmed.json()
        assert confirm_payload["confirmed"] is True
        assert confirm_payload["status"] == "confirmed"
        assert confirm_payload["confirmed_at"] is not None

        executed = client.post(f"/assistant/proposals/{proposal_id}/execute")
        assert executed.status_code == 200
        exec_payload = executed.json()
        assert exec_payload["status"] == "executed"
        assert exec_payload["execution"]["status"] == "accepted"
        assert exec_payload["executed_at"] is not None
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_concurrent_same_prompt_returns_same_proposal_id() -> None:
    app, db_path = _assistant_app()
    try:
        message = "Create wallet for me"
        session_id = "chat_concurrent"

        def _create() -> str:
            client = TestClient(app)
            proposal = client.post(
                "/assistant/proposals",
                json={"message": message, "session_id": session_id},
            ).json()
            return proposal["proposal_id"]

        with ThreadPoolExecutor(max_workers=8) as executor:
            proposal_ids = list(executor.map(lambda _: _create(), range(16)))

        assert len(set(proposal_ids)) == 1
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_concurrent_same_prompt_different_sessions_produce_distinct_proposals() -> None:
    app, db_path = _assistant_app()
    try:
        message = "Create wallet for me"
        session_ids = [f"chat_session_{i}" for i in range(8)]

        def _create(session_id: str) -> str:
            client = TestClient(app)
            proposal = client.post(
                "/assistant/proposals",
                json={"message": message, "session_id": session_id},
            ).json()
            return proposal["proposal_id"]

        with ThreadPoolExecutor(max_workers=8) as executor:
            proposal_ids = list(executor.map(_create, session_ids))

        assert len(set(proposal_ids)) == len(session_ids)
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_confirm_after_execute_is_idempotent_no_op() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        created = client.post("/assistant/proposals", json={"message": "Fund wallet with USDC"})
        proposal_id = created.json()["proposal_id"]
        client.post(f"/assistant/proposals/{proposal_id}/confirm")
        executed = client.post(f"/assistant/proposals/{proposal_id}/execute")
        executed_payload = executed.json()

        reconfirmed = client.post(f"/assistant/proposals/{proposal_id}/confirm")
        assert reconfirmed.status_code == 200
        payload = reconfirmed.json()
        assert payload["status"] == "executed"
        assert payload["executed_at"] == executed_payload["executed_at"]
        assert payload["execution"] == executed_payload["execution"]
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_proposal_persists_across_app_recreation() -> None:
    app1, db_path = _assistant_app()
    try:
        client1 = TestClient(app1)
        created = client1.post(
            "/assistant/proposals",
            json={"message": "Create wallet for me", "session_id": "chat_persist"},
        )
        proposal_id = created.json()["proposal_id"]

        app2 = FastAPI()
        register_error_handlers(app2)
        app2.include_router(assistant_router)
        app2.dependency_overrides = app1.dependency_overrides
        client2 = TestClient(app2)
        fetched = client2.get(f"/assistant/proposals/{proposal_id}")
        assert fetched.status_code == 200
        assert fetched.json()["proposal_id"] == proposal_id
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_ui_handoff_requires_confirmed_state() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        created = client.post("/assistant/proposals", json={"message": "Create wallet for me"})
        proposal_id = created.json()["proposal_id"]

        res = client.get(f"/assistant/proposals/{proposal_id}/ui-handoff")
        assert res.status_code == 409
        payload = res.json()
        assert payload["code"] == "INVALID_PROPOSAL_STATE"
        assert "reason" in payload["details"]
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_ui_handoff_returns_builder_payload_after_confirm() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        created = client.post("/assistant/proposals", json={"message": "Fund wallet with USDC"})
        proposal_id = created.json()["proposal_id"]
        client.post(f"/assistant/proposals/{proposal_id}/confirm")

        res = client.get(f"/assistant/proposals/{proposal_id}/ui-handoff")
        assert res.status_code == 200
        payload = res.json()
        assert payload["proposal_id"] == proposal_id
        assert payload["source"] == "assistant_proposal"
        assert isinstance(payload["nodes"], list) and payload["nodes"]
        assert isinstance(payload["edges"], list)
        assert payload["nodes"][0]["id"].startswith("node_")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_ui_handoff_preserves_explicit_branch_edges_when_present() -> None:
    app, db_path = _assistant_app()
    try:
        client = TestClient(app)
        created = client.post("/assistant/proposals", json={"message": "Fund wallet with USDC"})
        proposal_id = created.json()["proposal_id"]
        client.post(f"/assistant/proposals/{proposal_id}/confirm")

        engine = create_engine(f"sqlite:///{db_path}")
        with Session(engine) as db:
            row = db.exec(select(AssistantProposal).where(AssistantProposal.proposal_id == proposal_id)).first()
            assert row is not None
            row.workflow = {
                "workflow_name": "branch_demo",
                "steps": [
                    {"id": "step_1", "type": "engine.start", "next_steps": ["step_2", "step_3"]},
                    {"id": "step_2", "type": "engine.path_a", "next": "step_4"},
                    {"id": "step_3", "type": "engine.path_b", "next": "step_4"},
                    {"id": "step_4", "type": "engine.join"},
                ],
            }
            db.add(row)
            db.commit()

        res = client.get(f"/assistant/proposals/{proposal_id}/ui-handoff")
        assert res.status_code == 200
        payload = res.json()
        edge_pairs = {(e["from"], e["to"]) for e in payload["edges"]}
        assert edge_pairs == {
            ("node_step_1", "node_step_2"),
            ("node_step_1", "node_step_3"),
            ("node_step_2", "node_step_4"),
            ("node_step_3", "node_step_4"),
        }
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
