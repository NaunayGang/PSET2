"""
Account repository interface and implementation.

Follows the Repository pattern with interface (Protocol) and concrete implementation.
"""

from datetime import datetime
from typing import List, Optional, Protocol
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.models import Account, AccountStatus, Currency
from app.repositories.orm_models import AccountORM


class AccountRepository(Protocol):
    """Interface for Account repository."""

    def save(self, account: Account) -> Account:
        """Save or update an account."""
        ...

    def find_by_id(self, account_id: UUID) -> Optional[Account]:
        """Find account by ID."""
        ...

    def find_by_customer_id(self, customer_id: UUID) -> List[Account]:
        """Find all accounts for a customer."""
        ...

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Account]:
        """List all accounts with pagination."""
        ...

    def delete(self, account_id: UUID) -> bool:
        """Delete an account."""
        ...


class SQLAlchemyAccountRepository:
    """SQLAlchemy implementation of AccountRepository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, account: Account) -> Account:
        """Save or update an account."""
        # Check if account exists
        existing = self._session.query(AccountORM).filter_by(id=account.id).first()

        if existing:
            # Update existing account
            existing.balance = account.balance
            existing.status = account.status
            existing.currency = account.currency
        else:
            # Create new account
            orm_account = AccountORM(
                id=account.id,
                customer_id=account.customer_id,
                currency=account.currency,
                balance=account.balance,
                status=account.status,
                created_at=account.created_at,
            )
            self._session.add(orm_account)

        self._session.flush()
        return account

    def find_by_id(self, account_id: UUID) -> Optional[Account]:
        """Find account by ID."""
        orm_account = self._session.query(AccountORM).filter_by(id=account_id).first()
        if not orm_account:
            return None
        return self._to_domain(orm_account)

    def find_by_customer_id(self, customer_id: UUID) -> List[Account]:
        """Find all accounts for a customer."""
        orm_accounts = (
            self._session.query(AccountORM)
            .filter_by(customer_id=customer_id)
            .order_by(AccountORM.created_at.desc())
            .all()
        )
        return [self._to_domain(a) for a in orm_accounts]

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Account]:
        """List all accounts with pagination."""
        orm_accounts = (
            self._session.query(AccountORM)
            .order_by(AccountORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_domain(a) for a in orm_accounts]

    def delete(self, account_id: UUID) -> bool:
        """Delete an account."""
        orm_account = self._session.query(AccountORM).filter_by(id=account_id).first()
        if not orm_account:
            return False
        self._session.delete(orm_account)
        self._session.flush()
        return True

    @staticmethod
    def _to_domain(orm_account: AccountORM) -> Account:
        """Convert ORM model to domain entity."""
        return Account(
            id=orm_account.id,
            customer_id=orm_account.customer_id,
            currency=orm_account.currency,
            balance=orm_account.balance,
            status=orm_account.status,
            created_at=orm_account.created_at,
        )
