"""
Transaction and LedgerEntry repository interfaces and implementations.

Follows the Repository pattern with interface (Protocol) and concrete implementation.
"""

from datetime import datetime
from typing import List, Optional, Protocol
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.models import (
    Transaction,
    LedgerEntry,
    TransactionType,
    TransactionStatus,
    LedgerDirection,
    Currency,
)
from app.repositories.orm_models import TransactionORM, LedgerEntryORM


class TransactionRepository(Protocol):
    """Interface for Transaction repository."""

    def save(self, transaction: Transaction) -> Transaction:
        """Save or update a transaction."""
        ...

    def find_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """Find transaction by ID."""
        ...

    def find_by_account_id(
        self, account_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[Transaction]:
        """Find all transactions for an account."""
        ...

    def find_recent_by_account(
        self, account_id: UUID, since: datetime
    ) -> List[Transaction]:
        """Find recent transactions for an account since a given time."""
        ...

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Transaction]:
        """List all transactions with pagination."""
        ...


class SQLAlchemyTransactionRepository:
    """SQLAlchemy implementation of TransactionRepository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, transaction: Transaction) -> Transaction:
        """Save or update a transaction."""
        # Check if transaction exists
        existing = (
            self._session.query(TransactionORM).filter_by(id=transaction.id).first()
        )

        if existing:
            # Update existing transaction
            existing.status = transaction.status
            existing.fee = transaction.fee
            existing.rejection_reason = transaction.rejection_reason
            existing.description = transaction.description
        else:
            # Create new transaction
            orm_transaction = TransactionORM(
                id=transaction.id,
                type=transaction.type,
                amount=transaction.amount,
                currency=transaction.currency,
                from_account_id=transaction.from_account_id,
                to_account_id=transaction.to_account_id,
                status=transaction.status,
                fee=transaction.fee,
                description=transaction.description,
                rejection_reason=transaction.rejection_reason,
                created_at=transaction.created_at,
            )
            self._session.add(orm_transaction)

        self._session.flush()
        return transaction

    def find_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """Find transaction by ID."""
        orm_txn = (
            self._session.query(TransactionORM).filter_by(id=transaction_id).first()
        )
        if not orm_txn:
            return None
        return self._to_domain(orm_txn)

    def find_by_account_id(
        self, account_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[Transaction]:
        """Find all transactions for an account."""
        orm_txns = (
            self._session.query(TransactionORM)
            .filter(
                (TransactionORM.from_account_id == account_id)
                | (TransactionORM.to_account_id == account_id)
            )
            .order_by(TransactionORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_domain(t) for t in orm_txns]

    def find_recent_by_account(
        self, account_id: UUID, since: datetime
    ) -> List[Transaction]:
        """Find recent transactions for an account since a given time."""
        orm_txns = (
            self._session.query(TransactionORM)
            .filter(
                (
                    (TransactionORM.from_account_id == account_id)
                    | (TransactionORM.to_account_id == account_id)
                )
                & (TransactionORM.created_at >= since)
                & (TransactionORM.status == TransactionStatus.APPROVED)
            )
            .order_by(TransactionORM.created_at.desc())
            .all()
        )
        return [self._to_domain(t) for t in orm_txns]

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Transaction]:
        """List all transactions with pagination."""
        orm_txns = (
            self._session.query(TransactionORM)
            .order_by(TransactionORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_domain(t) for t in orm_txns]

    @staticmethod
    def _to_domain(orm_txn: TransactionORM) -> Transaction:
        """Convert ORM model to domain entity."""
        return Transaction(
            id=orm_txn.id,
            type=orm_txn.type,
            amount=orm_txn.amount,
            currency=orm_txn.currency,
            from_account_id=orm_txn.from_account_id,
            to_account_id=orm_txn.to_account_id,
            status=orm_txn.status,
            fee=orm_txn.fee,
            description=orm_txn.description,
            rejection_reason=orm_txn.rejection_reason,
            created_at=orm_txn.created_at,
        )


class LedgerEntryRepository(Protocol):
    """Interface for LedgerEntry repository."""

    def save(self, entry: LedgerEntry) -> LedgerEntry:
        """Save a ledger entry."""
        ...

    def find_by_account_id(
        self, account_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[LedgerEntry]:
        """Find all ledger entries for an account."""
        ...

    def find_by_transaction_id(self, transaction_id: UUID) -> List[LedgerEntry]:
        """Find all ledger entries for a transaction."""
        ...


class SQLAlchemyLedgerEntryRepository:
    """SQLAlchemy implementation of LedgerEntryRepository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, entry: LedgerEntry) -> LedgerEntry:
        """Save a ledger entry."""
        orm_entry = LedgerEntryORM(
            id=entry.id,
            account_id=entry.account_id,
            transaction_id=entry.transaction_id,
            direction=entry.direction,
            amount=entry.amount,
            description=entry.description,
            created_at=entry.created_at,
        )
        self._session.add(orm_entry)
        self._session.flush()
        return entry

    def find_by_account_id(
        self, account_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[LedgerEntry]:
        """Find all ledger entries for an account."""
        orm_entries = (
            self._session.query(LedgerEntryORM)
            .filter_by(account_id=account_id)
            .order_by(LedgerEntryORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_domain(e) for e in orm_entries]

    def find_by_transaction_id(self, transaction_id: UUID) -> List[LedgerEntry]:
        """Find all ledger entries for a transaction."""
        orm_entries = (
            self._session.query(LedgerEntryORM)
            .filter_by(transaction_id=transaction_id)
            .order_by(LedgerEntryORM.created_at.asc())
            .all()
        )
        return [self._to_domain(e) for e in orm_entries]

    @staticmethod
    def _to_domain(orm_entry: LedgerEntryORM) -> LedgerEntry:
        """Convert ORM model to domain entity."""
        return LedgerEntry(
            id=orm_entry.id,
            account_id=orm_entry.account_id,
            transaction_id=orm_entry.transaction_id,
            direction=orm_entry.direction,
            amount=orm_entry.amount,
            description=orm_entry.description,
            created_at=orm_entry.created_at,
        )
