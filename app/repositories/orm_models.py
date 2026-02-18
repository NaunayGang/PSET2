"""
ORM models for SQLAlchemy persistence layer.

Maps domain entities to database tables using SQLAlchemy ORM.
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.domain.models import (
    AccountStatus,
    TransactionType,
    TransactionStatus,
    LedgerDirection,
    Currency,
)

Base = declarative_base()


class CustomerORM(Base):
    """ORM model for Customer entity."""

    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(String(50), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    accounts = relationship(
        "AccountORM", back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CustomerORM(id={self.id}, name='{self.name}', email='{self.email}')>"


class AccountORM(Base):
    """ORM model for Account entity."""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False, default=Currency.USD)
    balance = Column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    status = Column(
        SQLEnum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    customer = relationship("CustomerORM", back_populates="accounts")
    ledger_entries = relationship(
        "LedgerEntryORM", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<AccountORM(id={self.id}, balance={self.balance}, status={self.status})>"
        )


class TransactionORM(Base):
    """ORM model for Transaction entity."""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False, default=Currency.USD)
    from_account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    status = Column(
        SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING
    )
    fee = Column(
        Numeric(precision=15, scale=2), nullable=False, default=Decimal("0.00")
    )
    description = Column(String(500), nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    ledger_entries = relationship(
        "LedgerEntryORM", back_populates="transaction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TransactionORM(id={self.id}, type={self.type}, amount={self.amount})>"


class LedgerEntryORM(Base):
    """ORM model for LedgerEntry entity."""

    __tablename__ = "ledger_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False
    )
    direction = Column(SQLEnum(LedgerDirection), nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    account = relationship("AccountORM", back_populates="ledger_entries")
    transaction = relationship("TransactionORM", back_populates="ledger_entries")

    def __repr__(self) -> str:
        return f"<LedgerEntryORM(id={self.id}, direction={self.direction}, amount={self.amount})>"
