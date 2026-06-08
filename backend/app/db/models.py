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


class Workspace(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Treasury(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("workspace_id", name="uq_treasury_workspace"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    name: str = Field(default="Treasury", index=True)
    asset: str = Field(default="USDC", index=True)
    network: str = Field(default="base", index=True)
    status: str = Field(default="active", index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class TreasuryWallet(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("treasury_id", name="uq_treasury_wallet_treasury"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    treasury_id: int = Field(foreign_key="treasury.id", index=True)
    provider: str = Field(default="privy", index=True)
    provider_wallet_id: str = Field(index=True)
    address: str = Field(index=True)
    network: str = Field(index=True)
    created_at: datetime = Field(default_factory=utcnow)


class TreasuryTransfer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    treasury_id: int = Field(foreign_key="treasury.id", index=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    direction: str = Field(index=True)  # inbound | outbound
    amount: float = Field(index=True)
    asset: str = Field(default="USDC", index=True)
    status: str = Field(default="completed", index=True)
    counterparty_label: Optional[str] = Field(default=None, index=True)
    reference: Optional[str] = Field(default=None, index=True)
    transaction_hash: Optional[str] = Field(default=None, index=True)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Recipient(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "wallet_address",
            "network",
            name="uq_recipient_workspace_address_network",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    name: str = Field(index=True)
    wallet_address: str = Field(index=True)
    network: str = Field(index=True)
    notes: Optional[str] = None
    status: str = Field(default="active", index=True)  # active | inactive
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class PayoutWorkflowDefinition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    name: str = Field(index=True)
    template_name: str = Field(default="contractor_payout", index=True)
    recipient_id: int = Field(foreign_key="recipient.id", index=True)
    amount: float = Field(index=True)
    asset: str = Field(default="USDC", index=True)
    schedule_cadence: str = Field(default="manual", index=True)  # manual | weekly | monthly
    schedule_day: Optional[str] = Field(default=None, index=True)
    enabled: bool = Field(default=True, index=True)
    last_run_id: Optional[int] = Field(default=None, index=True)
    last_run_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ActivityEvent(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("source_kind", "source_id", "event_type", name="uq_activity_source_event"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    event_type: str = Field(index=True)
    status: str = Field(default="completed", index=True)
    title: str = Field(index=True)
    summary: str
    source_kind: str = Field(index=True)
    source_id: int = Field(index=True)
    links: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    payload: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class Alert(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("source_kind", "source_id", "alert_type", name="uq_alert_source_type"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    alert_type: str = Field(index=True)
    severity: str = Field(default="warning", index=True)  # critical | warning | info
    status: str = Field(default="open", index=True)  # open | acknowledged | resolved
    title: str = Field(index=True)
    message: str
    recovery_action: str = Field(index=True)
    recovery_label: str
    source_kind: str = Field(index=True)
    source_id: int = Field(index=True)
    links: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    payload: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


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
