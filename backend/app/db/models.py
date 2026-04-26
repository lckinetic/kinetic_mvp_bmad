from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Index, UniqueConstraint, Column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Order(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("provider", "order_id", name="uq_order_provider_orderid"),
        UniqueConstraint("provider", "direction", "client_reference", name="uq_order_provider_direction_clientref"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)

    provider: str = Field(default="banxa", index=True)
    direction: str = Field(index=True)  # "onramp" | "offramp"

    order_id: str = Field(index=True)  # provider order id
    order_status: str = Field(default="pending", index=True)
    client_reference: Optional[str] = Field(default=None, index=True)
    
    user_email: str = Field(index=True)
    fiat_amount: Optional[float] = None  # onramp
    fiat_currency: Optional[str] = Field(default=None, index=True)
    crypto_currency: Optional[str] = Field(default=None, index=True)
    crypto_amount: Optional[float] = None  # offramp

    wallet_address: Optional[str] = None  # onramp
    blockchain: Optional[str] = None  # onramp
    destination_reference: Optional[str] = None  # offramp (e.g. bank account)

    checkout_url: Optional[str] = None
    transaction_hash: Optional[str] = None

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    completed_at: Optional[datetime] = None


class WebhookEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    provider: str = Field(default="banxa", index=True)
    direction: str = Field(index=True)

    event_type: str = Field(index=True)
    order_id: Optional[str] = Field(default=None, index=True)

    payload: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)

    processed: bool = Field(default=False, index=True)
    received_at: datetime = Field(default_factory=utcnow)

    idempotency_key: str = Field(index=True)

class WorkflowRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    template_name: str = Field(index=True)
    status: str = Field(default="running", index=True)  # running|completed|failed

    # raw inputs/outputs for demo + debugging
    input: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    output: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    error: Optional[str] = None

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


Index(
    "ix_webhook_events_provider_direction_key",
    WebhookEvent.provider,
    WebhookEvent.direction,
    WebhookEvent.idempotency_key,
    unique=True,
)

class WorkflowStep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    run_id: int = Field(index=True, foreign_key="workflowrun.id")
    seq: int = Field(index=True)  # 1..n within a run

    step_name: str = Field(index=True)  # e.g. "onramp.create"
    status: str = Field(default="running", index=True)  # running|completed|failed

    data: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    error: Optional[str] = None

    started_at: datetime = Field(default_factory=utcnow)
    ended_at: Optional[datetime] = None


class AssistantProposal(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("proposal_id", name="uq_assistant_proposal_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    proposal_id: str = Field(index=True)
    session_id: str = Field(index=True)
    message: str
    status: str = Field(default="proposed", index=True)

    created_at: datetime = Field(default_factory=utcnow)
    confirmed: bool = Field(default=False, index=True)
    confirmed_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None

    workflow: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    validation: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    execution: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON), default=None)
