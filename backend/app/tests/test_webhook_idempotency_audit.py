from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone
import os
from tempfile import mkstemp

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from app.api.webhooks import get_db, router as webhooks_router
from app.core.config import Settings
from app.db import models  # noqa: F401  # ensure metadata is registered
from app.db.models import Order, WebhookEvent


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


def _app_with_test_db() -> tuple[FastAPI, str, object]:
    fd, db_path = mkstemp(suffix=".sqlite3")
    os.close(fd)
    settings = _mk_settings(db_path)
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(webhooks_router)

    def _get_db_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    return app, db_path, engine


def test_duplicate_webhook_is_idempotent_and_audited_once() -> None:
    app, db_path, engine = _app_with_test_db()
    try:
        with Session(engine) as db:
            db.add(
                Order(
                    provider="banxa",
                    direction="onramp",
                    order_id="banxa_order_1",
                    order_status="pending",
                    user_email="demo@example.com",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            db.commit()

        client = TestClient(app)
        payload = {"order_id": "banxa_order_1", "status": "success", "direction": "onramp"}
        headers = {"x-idempotency-key": "idem-123"}

        r1 = client.post("/webhooks/banxa", json=payload, headers=headers)
        assert r1.status_code == 200
        assert r1.json()["status"] == "received"

        with Session(engine) as db:
            order_after_first = db.exec(select(Order).where(Order.order_id == "banxa_order_1")).first()
            assert order_after_first is not None
            assert order_after_first.order_status == "completed"
            first_updated_at = order_after_first.updated_at

            events = db.exec(select(WebhookEvent)).all()
            assert len(events) == 1
            assert events[0].processed is True

        r2 = client.post("/webhooks/banxa", json=payload, headers=headers)
        assert r2.status_code == 200
        assert r2.json()["status"] == "duplicate_ignored"

        with Session(engine) as db:
            order_after_second = db.exec(select(Order).where(Order.order_id == "banxa_order_1")).first()
            assert order_after_second is not None
            assert order_after_second.updated_at == first_updated_at

            events = db.exec(select(WebhookEvent)).all()
            assert len(events) == 1
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_duplicate_webhook_without_header_uses_derived_idempotency_key() -> None:
    app, db_path, engine = _app_with_test_db()
    try:
        with Session(engine) as db:
            db.add(
                Order(
                    provider="banxa",
                    direction="onramp",
                    order_id="banxa_order_2",
                    order_status="pending",
                    user_email="demo@example.com",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            db.commit()

        client = TestClient(app)
        payload = {"order_id": "banxa_order_2", "status": "success", "direction": "onramp"}

        r1 = client.post("/webhooks/banxa", json=payload)
        assert r1.status_code == 200
        first = r1.json()
        assert first["status"] == "received"
        derived_key = first["idempotency_key"]
        assert isinstance(derived_key, str) and derived_key

        r2 = client.post("/webhooks/banxa", json=payload)
        assert r2.status_code == 200
        second = r2.json()
        assert second["status"] == "duplicate_ignored"
        assert second["idempotency_key"] == derived_key

        with Session(engine) as db:
            order_after_second = db.exec(select(Order).where(Order.order_id == "banxa_order_2")).first()
            assert order_after_second is not None
            assert order_after_second.order_status == "completed"

            events = db.exec(select(WebhookEvent).where(WebhookEvent.order_id == "banxa_order_2")).all()
            assert len(events) == 1
            assert events[0].idempotency_key == derived_key
            assert events[0].processed is True
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
