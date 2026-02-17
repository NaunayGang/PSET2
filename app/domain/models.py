"""
Domain models for the banking system.

This module contains the core domain entities following DDD principles:
- Customer: Represents a bank customer
- Account: Represents a customer's account/wallet
- Transaction: Represents a financial transaction
- LedgerEntry: Represents a double-entry ledger movement

All models include invariants and business logic validations.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


# ==================== Enums ====================


class AccountStatus(str, Enum):
    """Status of an account."""

    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class TransactionType(str, Enum):
    """Type of transaction."""

    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"


class TransactionStatus(str, Enum):
    """Status of a transaction."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LedgerDirection(str, Enum):
    """Direction of a ledger entry."""

    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class Currency(str, Enum):
    """Supported currencies."""

    USD = "USD"


# ==================== Value Objects ====================


class Money:
    """
    Value object representing a monetary amount with currency.

    Invariants:
    - Amount must be non-negative
    - Currency must be valid
    """

    def __init__(self, amount: Decimal, currency: Currency = Currency.USD):
        if amount < 0:
            raise ValueError("El monto no puede ser negativo")
        self._amount = amount
        self._currency = currency

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> Currency:
        return self._currency

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("No se pueden sumar montos de diferentes monedas")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("No se pueden restar montos de diferentes monedas")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("El resultado no puede ser negativo")
        return Money(result, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __repr__(self) -> str:
        return f"Money({self.amount}, {self.currency.value})"


# ==================== Domain Exceptions ====================


class DomainException(Exception):
    """Base exception for domain errors."""

    pass


class InsufficientFundsError(DomainException):
    """Raised when account has insufficient funds for an operation."""

    pass


class AccountFrozenError(DomainException):
    """Raised when attempting to operate on a frozen account."""

    pass


class AccountClosedError(DomainException):
    """Raised when attempting to operate on a closed account."""

    pass


class InvalidTransactionError(DomainException):
    """Raised when transaction is invalid."""

    pass


class CustomerNotFoundError(DomainException):
    """Raised when customer is not found."""

    pass


class AccountNotFoundError(DomainException):
    """Raised when account is not found."""

    pass


class TransactionNotFoundError(DomainException):
    """Raised when transaction is not found."""

    pass


# ==================== Domain Entities ====================


class Customer:
    """
    Customer entity (Aggregate Root).

    Represents a bank customer with unique identification.

    Invariants:
    - Customer must have a valid name
    - Customer must have a valid email
    """

    def __init__(
        self,
        name: str,
        email: str,
        id: Optional[UUID] = None,
        status: str = "ACTIVE",
        created_at: Optional[datetime] = None,
    ):
        if not name or not name.strip():
            raise ValueError("El nombre del cliente no puede estar vacío")
        if not email or "@" not in email:
            raise ValueError("El email del cliente debe ser válido")

        self.id = id or uuid4()
        self.name = name.strip()
        self.email = email.strip().lower()
        self.status = status
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"Customer(id={self.id}, name={self.name}, email={self.email})"


class Account:
    """
    Account entity (Aggregate Root).

    Represents a customer's account/wallet with balance and currency.

    Invariants:
    - Account must belong to a customer
    - Balance cannot be negative
    - Cannot withdraw/transfer from frozen or closed account
    - Cannot operate on closed account
    """

    def __init__(
        self,
        customer_id: UUID,
        currency: Currency = Currency.USD,
        id: Optional[UUID] = None,
        balance: Decimal = Decimal("0.00"),
        status: AccountStatus = AccountStatus.ACTIVE,
        created_at: Optional[datetime] = None,
    ):
        if balance < 0:
            raise ValueError("El balance no puede ser negativo")

        self.id = id or uuid4()
        self.customer_id = customer_id
        self.currency = currency
        self._balance = balance
        self.status = status
        self.created_at = created_at or datetime.utcnow()

    @property
    def balance(self) -> Decimal:
        """Get current balance."""
        return self._balance

    def can_operate(self) -> bool:
        """Check if account can be operated on."""
        return self.status == AccountStatus.ACTIVE

    def credit(self, amount: Decimal) -> None:
        """
        Credit (add) amount to account.

        Args:
            amount: Amount to credit (must be positive)

        Raises:
            ValueError: If amount is not positive
            AccountClosedError: If account is closed
        """
        if amount <= 0:
            raise ValueError("El monto a acreditar debe ser positivo")
        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError("No se puede operar en una cuenta cerrada")

        self._balance += amount

    def debit(self, amount: Decimal) -> None:
        """
        Debit (subtract) amount from account.

        Args:
            amount: Amount to debit (must be positive)

        Raises:
            ValueError: If amount is not positive
            InsufficientFundsError: If insufficient balance
            AccountFrozenError: If account is frozen
            AccountClosedError: If account is closed
        """
        if amount <= 0:
            raise ValueError("El monto a debitar debe ser positivo")
        if self.status == AccountStatus.FROZEN:
            raise AccountFrozenError("No se puede debitar de una cuenta congelada")
        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError("No se puede operar en una cuenta cerrada")
        if self._balance < amount:
            raise InsufficientFundsError(
                f"Fondos insuficientes: balance={self._balance}, monto solicitado={amount}"
            )

        self._balance -= amount

    def freeze(self) -> None:
        """Freeze the account."""
        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError("No se puede congelar una cuenta cerrada")
        self.status = AccountStatus.FROZEN

    def unfreeze(self) -> None:
        """Unfreeze the account."""
        if self.status == AccountStatus.FROZEN:
            self.status = AccountStatus.ACTIVE

    def close(self) -> None:
        """Close the account."""
        self.status = AccountStatus.CLOSED

    def __repr__(self) -> str:
        return (
            f"Account(id={self.id}, customer_id={self.customer_id}, "
            f"balance={self.balance}, status={self.status.value})"
        )


class Transaction:
    """
    Transaction entity.

    Represents a financial transaction in the system.

    Invariants:
    - Transaction must have a valid type
    - Amount must be positive
    - Must have at least one account involved
    """

    def __init__(
        self,
        type: TransactionType,
        amount: Decimal,
        currency: Currency,
        from_account_id: Optional[UUID] = None,
        to_account_id: Optional[UUID] = None,
        id: Optional[UUID] = None,
        status: TransactionStatus = TransactionStatus.PENDING,
        fee: Decimal = Decimal("0.00"),
        description: Optional[str] = None,
        rejection_reason: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        if amount <= 0:
            raise ValueError("El monto de la transacción debe ser positivo")

        # Validate transaction type constraints
        if type == TransactionType.DEPOSIT and not to_account_id:
            raise InvalidTransactionError(
                "Un depósito debe tener una cuenta de destino"
            )
        if type == TransactionType.WITHDRAW and not from_account_id:
            raise InvalidTransactionError("Un retiro debe tener una cuenta de origen")
        if type == TransactionType.TRANSFER:
            if not from_account_id or not to_account_id:
                raise InvalidTransactionError(
                    "Una transferencia debe tener cuenta de origen y destino"
                )
            if from_account_id == to_account_id:
                raise InvalidTransactionError(
                    "La cuenta de origen y destino no pueden ser la misma"
                )

        self.id = id or uuid4()
        self.type = type
        self.amount = amount
        self.currency = currency
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.status = status
        self.fee = fee
        self.description = description
        self.rejection_reason = rejection_reason
        self.created_at = created_at or datetime.utcnow()

    def approve(self) -> None:
        """Approve the transaction."""
        if self.status != TransactionStatus.PENDING:
            raise InvalidTransactionError(
                "Solo se pueden aprobar transacciones pendientes"
            )
        self.status = TransactionStatus.APPROVED

    def reject(self, reason: str) -> None:
        """Reject the transaction with a reason."""
        if self.status != TransactionStatus.PENDING:
            raise InvalidTransactionError(
                "Solo se pueden rechazar transacciones pendientes"
            )
        self.status = TransactionStatus.REJECTED
        self.rejection_reason = reason

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self.id}, type={self.type.value}, "
            f"amount={self.amount}, status={self.status.value})"
        )


class LedgerEntry:
    """
    Ledger entry entity.

    Represents a single entry in the double-entry ledger system.
    Each transaction generates one or more ledger entries.

    Invariants:
    - Must be linked to an account
    - Must be linked to a transaction
    - Amount must be positive
    - Direction must be valid (DEBIT or CREDIT)
    """

    def __init__(
        self,
        account_id: UUID,
        transaction_id: UUID,
        direction: LedgerDirection,
        amount: Decimal,
        id: Optional[UUID] = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        if amount <= 0:
            raise ValueError("El monto del asiento debe ser positivo")

        self.id = id or uuid4()
        self.account_id = account_id
        self.transaction_id = transaction_id
        self.direction = direction
        self.amount = amount
        self.description = description
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"LedgerEntry(id={self.id}, account_id={self.account_id}, "
            f"direction={self.direction.value}, amount={self.amount})"
        )
