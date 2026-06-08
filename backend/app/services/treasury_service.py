from __future__ import annotations

from typing import Any
import hashlib

from sqlmodel import Session, select

from app.adapters.privy.client import PrivyClient
from app.core.config import Settings
from app.db.models import Treasury, TreasuryTransfer, TreasuryWallet, utcnow
from app.services.workspace_service import get_current_workspace


class TreasuryNotFoundError(LookupError):
    pass


class TreasuryAlreadyExistsError(ValueError):
    pass


class InsufficientBalanceError(ValueError):
    def __init__(self, *, balance: float, required: float):
        self.balance = balance
        self.required = required
        self.shortfall = round(max(required - balance, 0.0), 2)
        super().__init__(
            f"Treasury balance is too low for this payout. "
            f"Available {balance:.2f} USDC, required {required:.2f} USDC."
        )


class MockOnlyOperationError(PermissionError):
    pass


class TreasuryProviderNotConfiguredError(PermissionError):
    pass


NETWORK_LABELS = {
    "base": "Base",
    "ethereum": "Ethereum",
}


def _build_privy(settings: Settings) -> PrivyClient:
    return PrivyClient(mock_mode=settings.mock_mode)


def get_treasury_for_workspace(db: Session, *, workspace_id: int) -> Treasury | None:
    return db.exec(select(Treasury).where(Treasury.workspace_id == workspace_id)).first()


def get_wallet_for_treasury(db: Session, *, treasury_id: int) -> TreasuryWallet | None:
    return db.exec(select(TreasuryWallet).where(TreasuryWallet.treasury_id == treasury_id)).first()


def compute_balance(db: Session, *, treasury_id: int) -> float:
    transfers = db.exec(
        select(TreasuryTransfer).where(
            TreasuryTransfer.treasury_id == treasury_id,
            TreasuryTransfer.status == "completed",
        )
    ).all()
    balance = 0.0
    for transfer in transfers:
        if transfer.direction == "inbound":
            balance += transfer.amount
        elif transfer.direction == "outbound":
            balance -= transfer.amount
    return round(balance, 2)


def list_transfers(db: Session, *, treasury_id: int, limit: int = 50) -> list[TreasuryTransfer]:
    rows = db.exec(
        select(TreasuryTransfer)
        .where(TreasuryTransfer.treasury_id == treasury_id)
        .order_by(TreasuryTransfer.created_at.desc())
        .limit(limit)
    ).all()
    return list(rows)


def create_treasury(
    db: Session,
    *,
    settings: Settings,
    name: str | None = None,
) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    existing = get_treasury_for_workspace(db, workspace_id=workspace.id)
    if existing:
        raise TreasuryAlreadyExistsError("A treasury wallet already exists for this workspace.")

    privy = _build_privy(settings)
    label = (name or workspace.name or "Treasury").strip() or "Treasury"
    try:
        wallet = privy.create_treasury_wallet(workspace_id=workspace.id, label=label, network="base")
    except NotImplementedError as exc:
        raise TreasuryProviderNotConfiguredError(str(exc)) from exc

    treasury = Treasury(
        workspace_id=workspace.id,
        name=label,
        asset="USDC",
        network=wallet.network,
        status="active",
    )
    db.add(treasury)
    db.flush()

    treasury_wallet = TreasuryWallet(
        treasury_id=treasury.id,
        provider="privy",
        provider_wallet_id=wallet.wallet_id,
        address=wallet.address,
        network=wallet.network,
    )
    db.add(treasury_wallet)
    db.commit()
    db.refresh(treasury)
    db.refresh(treasury_wallet)

    return build_treasury_view(db, treasury=treasury, wallet=treasury_wallet, settings=settings)


def get_current_treasury(db: Session, *, settings: Settings) -> dict[str, Any]:
    workspace = get_current_workspace(db)
    treasury = get_treasury_for_workspace(db, workspace_id=workspace.id)
    if not treasury:
        raise TreasuryNotFoundError("No treasury exists for this workspace yet.")
    wallet = get_wallet_for_treasury(db, treasury_id=treasury.id)
    if not wallet:
        raise TreasuryNotFoundError("Treasury wallet record is missing.")
    return build_treasury_view(db, treasury=treasury, wallet=wallet, settings=settings)


def build_treasury_view(
    db: Session,
    *,
    treasury: Treasury,
    wallet: TreasuryWallet,
    settings: Settings,
) -> dict[str, Any]:
    balance = compute_balance(db, treasury_id=treasury.id)
    network_label = NETWORK_LABELS.get(treasury.network, treasury.network)
    return {
        "id": treasury.id,
        "workspace_id": treasury.workspace_id,
        "name": treasury.name,
        "asset": treasury.asset,
        "network": treasury.network,
        "network_label": network_label,
        "status": treasury.status,
        "balance": balance,
        "wallet": {
            "id": wallet.id,
            "provider_label": "Connected wallet",
            "address": wallet.address,
            "network": wallet.network,
            "network_label": network_label,
        },
        "funding": {
            "asset": treasury.asset,
            "network": treasury.network,
            "network_label": network_label,
            "address": wallet.address,
            "warning": f"Send only {treasury.asset} on {network_label}. Other assets may be lost.",
        },
        "mock_mode": settings.mock_mode,
        "created_at": treasury.created_at.isoformat(),
        "updated_at": treasury.updated_at.isoformat(),
    }


def check_sufficient_balance(db: Session, *, treasury_id: int, amount: float) -> dict[str, Any]:
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    balance = compute_balance(db, treasury_id=treasury_id)
    sufficient = balance >= amount
    payload = {
        "sufficient": sufficient,
        "balance": balance,
        "required": round(amount, 2),
        "shortfall": round(max(amount - balance, 0.0), 2),
        "asset": "USDC",
    }
    if not sufficient:
        raise InsufficientBalanceError(balance=balance, required=amount)
    return payload


def simulate_deposit(
    db: Session,
    *,
    settings: Settings,
    amount: float,
    counterparty_label: str = "Demo deposit",
) -> dict[str, Any]:
    if not settings.mock_mode:
        raise MockOnlyOperationError("Simulated deposits are only available in mock mode.")

    if amount <= 0:
        raise ValueError("Deposit amount must be greater than zero.")

    view = get_current_treasury(db, settings=settings)
    treasury_id = view["id"]
    workspace_id = view["workspace_id"]

    fp = f"mock_deposit_{treasury_id}_{int(utcnow().timestamp())}"
    tx_hash = hashlib.sha256(fp.encode("utf-8")).hexdigest()
    transfer = TreasuryTransfer(
        treasury_id=treasury_id,
        workspace_id=workspace_id,
        direction="inbound",
        amount=round(amount, 2),
        asset="USDC",
        status="completed",
        counterparty_label=counterparty_label,
        reference=fp,
        transaction_hash=f"0x{tx_hash[:40]}",
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)

    return {
        "transfer": serialize_transfer(transfer),
        "treasury": get_current_treasury(db, settings=settings),
    }


def serialize_transfer(row: TreasuryTransfer) -> dict[str, Any]:
    return {
        "id": row.id,
        "treasury_id": row.treasury_id,
        "direction": row.direction,
        "amount": row.amount,
        "asset": row.asset,
        "status": row.status,
        "counterparty_label": row.counterparty_label,
        "reference": row.reference,
        "transaction_hash": row.transaction_hash,
        "error_message": row.error_message,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
    }
