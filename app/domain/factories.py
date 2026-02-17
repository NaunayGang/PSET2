"""
Creational patterns for domain entities.

This module implements creational design patterns:
- Factory Method: TransactionFactory for creating different transaction types
- Builder: TransactionBuilder for complex transaction construction with metadata

These patterns provide flexible and consistent object creation while
encapsulating construction complexity.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.models import (
    Currency,
    Transaction,
    TransactionStatus,
    TransactionType,
    InvalidTransactionError,
)


# ==================== Factory Method Pattern ====================


class TransactionFactory:
    """
    Factory for creating Transaction objects (Factory Method pattern).

    Provides static methods to create different types of transactions
    with proper validation and default values.
    """

    @staticmethod
    def create_deposit(
        to_account_id: UUID,
        amount: Decimal,
        currency: Currency = Currency.USD,
        description: Optional[str] = None,
        fee: Decimal = Decimal("0.00"),
    ) -> Transaction:
        """
        Create a deposit transaction.

        Args:
            to_account_id: Account receiving the deposit
            amount: Amount to deposit
            currency: Currency of the transaction
            description: Optional description
            fee: Fee to be charged

        Returns:
            Transaction object configured for deposit
        """
        if amount <= 0:
            raise ValueError("El monto del depósito debe ser positivo")

        return Transaction(
            type=TransactionType.DEPOSIT,
            amount=amount,
            currency=currency,
            to_account_id=to_account_id,
            fee=fee,
            description=description or "Depósito",
            status=TransactionStatus.PENDING,
        )

    @staticmethod
    def create_withdraw(
        from_account_id: UUID,
        amount: Decimal,
        currency: Currency = Currency.USD,
        description: Optional[str] = None,
        fee: Decimal = Decimal("0.00"),
    ) -> Transaction:
        """
        Create a withdraw transaction.

        Args:
            from_account_id: Account to withdraw from
            amount: Amount to withdraw
            currency: Currency of the transaction
            description: Optional description
            fee: Fee to be charged

        Returns:
            Transaction object configured for withdrawal
        """
        if amount <= 0:
            raise ValueError("El monto del retiro debe ser positivo")

        return Transaction(
            type=TransactionType.WITHDRAW,
            amount=amount,
            currency=currency,
            from_account_id=from_account_id,
            fee=fee,
            description=description or "Retiro",
            status=TransactionStatus.PENDING,
        )

    @staticmethod
    def create_transfer(
        from_account_id: UUID,
        to_account_id: UUID,
        amount: Decimal,
        currency: Currency = Currency.USD,
        description: Optional[str] = None,
        fee: Decimal = Decimal("0.00"),
    ) -> Transaction:
        """
        Create a transfer transaction.

        Args:
            from_account_id: Account to transfer from
            to_account_id: Account to transfer to
            amount: Amount to transfer
            currency: Currency of the transaction
            description: Optional description
            fee: Fee to be charged

        Returns:
            Transaction object configured for transfer
        """
        if amount <= 0:
            raise ValueError("El monto de la transferencia debe ser positivo")
        if from_account_id == to_account_id:
            raise InvalidTransactionError("No se puede transferir a la misma cuenta")

        return Transaction(
            type=TransactionType.TRANSFER,
            amount=amount,
            currency=currency,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            fee=fee,
            description=description or "Transferencia",
            status=TransactionStatus.PENDING,
        )


# ==================== Builder Pattern ====================


class TransactionBuilder:
    """
    Builder for constructing complex Transaction objects (Builder pattern).

    Provides a fluent interface for building transactions step-by-step
    with optional metadata, risk results, and validation.

    Example:
        transaction = (TransactionBuilder()
            .with_type(TransactionType.TRANSFER)
            .with_amount(Decimal("100.00"))
            .from_account(source_id)
            .to_account(dest_id)
            .with_fee(Decimal("1.50"))
            .with_description("Payment for services")
            .with_status(TransactionStatus.APPROVED)
            .build())
    """

    def __init__(self):
        """Initialize empty builder."""
        self._type: Optional[TransactionType] = None
        self._amount: Optional[Decimal] = None
        self._currency: Currency = Currency.USD
        self._from_account_id: Optional[UUID] = None
        self._to_account_id: Optional[UUID] = None
        self._status: TransactionStatus = TransactionStatus.PENDING
        self._fee: Decimal = Decimal("0.00")
        self._description: Optional[str] = None
        self._rejection_reason: Optional[str] = None
        self._created_at: Optional[datetime] = None
        self._id: Optional[UUID] = None

    def with_id(self, id: UUID) -> "TransactionBuilder":
        """Set transaction ID."""
        self._id = id
        return self

    def with_type(self, transaction_type: TransactionType) -> "TransactionBuilder":
        """Set transaction type."""
        self._type = transaction_type
        return self

    def with_amount(self, amount: Decimal) -> "TransactionBuilder":
        """Set transaction amount."""
        if amount <= 0:
            raise ValueError("El monto debe ser positivo")
        self._amount = amount
        return self

    def with_currency(self, currency: Currency) -> "TransactionBuilder":
        """Set transaction currency."""
        self._currency = currency
        return self

    def from_account(self, account_id: UUID) -> "TransactionBuilder":
        """Set source account."""
        self._from_account_id = account_id
        return self

    def to_account(self, account_id: UUID) -> "TransactionBuilder":
        """Set destination account."""
        self._to_account_id = account_id
        return self

    def with_status(self, status: TransactionStatus) -> "TransactionBuilder":
        """Set transaction status."""
        self._status = status
        return self

    def with_fee(self, fee: Decimal) -> "TransactionBuilder":
        """Set transaction fee."""
        if fee < 0:
            raise ValueError("La comisión no puede ser negativa")
        self._fee = fee
        return self

    def with_description(self, description: str) -> "TransactionBuilder":
        """Set transaction description."""
        self._description = description
        return self

    def with_rejection_reason(self, reason: str) -> "TransactionBuilder":
        """Set rejection reason (for rejected transactions)."""
        self._rejection_reason = reason
        return self

    def with_created_at(self, created_at: datetime) -> "TransactionBuilder":
        """Set creation timestamp."""
        self._created_at = created_at
        return self

    def build(self) -> Transaction:
        """
        Build and validate the transaction.

        Returns:
            Constructed Transaction object

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if self._type is None:
            raise ValueError("El tipo de transacción es requerido")
        if self._amount is None:
            raise ValueError("El monto es requerido")

        # Validate transaction type constraints
        if self._type == TransactionType.DEPOSIT and not self._to_account_id:
            raise InvalidTransactionError(
                "Un depósito debe tener una cuenta de destino"
            )
        if self._type == TransactionType.WITHDRAW and not self._from_account_id:
            raise InvalidTransactionError("Un retiro debe tener una cuenta de origen")
        if self._type == TransactionType.TRANSFER:
            if not self._from_account_id or not self._to_account_id:
                raise InvalidTransactionError(
                    "Una transferencia debe tener cuenta de origen y destino"
                )
            if self._from_account_id == self._to_account_id:
                raise InvalidTransactionError(
                    "La cuenta de origen y destino no pueden ser la misma"
                )

        return Transaction(
            id=self._id,
            type=self._type,
            amount=self._amount,
            currency=self._currency,
            from_account_id=self._from_account_id,
            to_account_id=self._to_account_id,
            status=self._status,
            fee=self._fee,
            description=self._description,
            rejection_reason=self._rejection_reason,
            created_at=self._created_at,
        )

    def reset(self) -> "TransactionBuilder":
        """Reset builder to initial state."""
        self.__init__()
        return self
