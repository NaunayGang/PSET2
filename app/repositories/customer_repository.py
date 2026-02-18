"""
Customer repository interface and implementation.

Follows the Repository pattern with interface (Protocol) and concrete implementation.
"""

from datetime import datetime
from typing import List, Optional, Protocol
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.models import Customer
from app.repositories.orm_models import CustomerORM


class CustomerRepository(Protocol):
    """Interface for Customer repository."""

    def save(self, customer: Customer) -> Customer:
        """Save or update a customer."""
        ...

    def find_by_id(self, customer_id: UUID) -> Optional[Customer]:
        """Find customer by ID."""
        ...

    def find_by_email(self, email: str) -> Optional[Customer]:
        """Find customer by email."""
        ...

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Customer]:
        """List all customers with pagination."""
        ...

    def delete(self, customer_id: UUID) -> bool:
        """Delete a customer."""
        ...


class SQLAlchemyCustomerRepository:
    """SQLAlchemy implementation of CustomerRepository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, customer: Customer) -> Customer:
        """Save or update a customer."""
        # Check if customer exists
        existing = self._session.query(CustomerORM).filter_by(id=customer.id).first()

        if existing:
            # Update existing customer
            existing.name = customer.name
            existing.email = customer.email
            existing.status = customer.status
        else:
            # Create new customer
            orm_customer = CustomerORM(
                id=customer.id,
                name=customer.name,
                email=customer.email,
                status=customer.status,
                created_at=customer.created_at,
            )
            self._session.add(orm_customer)

        self._session.flush()
        return customer

    def find_by_id(self, customer_id: UUID) -> Optional[Customer]:
        """Find customer by ID."""
        orm_customer = (
            self._session.query(CustomerORM).filter_by(id=customer_id).first()
        )
        if not orm_customer:
            return None
        return self._to_domain(orm_customer)

    def find_by_email(self, email: str) -> Optional[Customer]:
        """Find customer by email."""
        orm_customer = (
            self._session.query(CustomerORM).filter_by(email=email.lower()).first()
        )
        if not orm_customer:
            return None
        return self._to_domain(orm_customer)

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Customer]:
        """List all customers with pagination."""
        orm_customers = (
            self._session.query(CustomerORM)
            .order_by(CustomerORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_domain(c) for c in orm_customers]

    def delete(self, customer_id: UUID) -> bool:
        """Delete a customer."""
        orm_customer = (
            self._session.query(CustomerORM).filter_by(id=customer_id).first()
        )
        if not orm_customer:
            return False
        self._session.delete(orm_customer)
        self._session.flush()
        return True

    @staticmethod
    def _to_domain(orm_customer: CustomerORM) -> Customer:
        """Convert ORM model to domain entity."""
        return Customer(
            id=orm_customer.id,
            name=orm_customer.name,
            email=orm_customer.email,
            status=orm_customer.status,
            created_at=orm_customer.created_at,
        )
