"""
Business rules and strategies for the banking system.

This module implements the Strategy pattern for:
- Fee calculation strategies
- Risk/Fraud detection strategies

These strategies are configured and injected into services to make
business rules flexible and extensible.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, List, Optional, Protocol
from uuid import UUID


# ==================== Fee Strategies (Strategy Pattern) ====================


class FeeStrategy(ABC):
    """
    Abstract base class for fee calculation strategies.

    Implements the Strategy pattern to allow different fee calculation
    algorithms to be used interchangeably.
    """

    @abstractmethod
    def calculate_fee(self, amount: Decimal) -> Decimal:
        """
        Calculate the fee for a transaction.

        Args:
            amount: Transaction amount

        Returns:
            Fee amount to be charged
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this fee strategy."""
        pass


class NoFeeStrategy(FeeStrategy):
    """Strategy that charges no fee (0%)."""

    def calculate_fee(self, amount: Decimal) -> Decimal:
        """Returns zero fee."""
        return Decimal("0.00")

    def get_name(self) -> str:
        return "Sin comisión"


class FlatFeeStrategy(FeeStrategy):
    """
    Strategy that charges a flat fee per transaction.

    Example: $0.50 per transaction regardless of amount.
    """

    def __init__(self, flat_amount: Decimal):
        """
        Initialize flat fee strategy.

        Args:
            flat_amount: Fixed fee amount to charge
        """
        if flat_amount < 0:
            raise ValueError("La comisión fija no puede ser negativa")
        self._flat_amount = flat_amount

    def calculate_fee(self, amount: Decimal) -> Decimal:
        """Returns the flat fee amount."""
        return self._flat_amount

    def get_name(self) -> str:
        return f"Comisión fija: ${self._flat_amount}"


class PercentFeeStrategy(FeeStrategy):
    """
    Strategy that charges a percentage of the transaction amount.

    Example: 1.5% of transaction amount.
    """

    def __init__(self, percent: Decimal):
        """
        Initialize percent fee strategy.

        Args:
            percent: Percentage to charge (e.g., 1.5 for 1.5%)
        """
        if percent < 0 or percent > 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100")
        self._percent = percent

    def calculate_fee(self, amount: Decimal) -> Decimal:
        """Returns percentage of the amount."""
        return (amount * self._percent / Decimal("100")).quantize(Decimal("0.01"))

    def get_name(self) -> str:
        return f"Comisión porcentual: {self._percent}%"


class TieredFeeStrategy(FeeStrategy):
    """
    Strategy that charges different fees based on amount tiers.

    Example:
    - Low tier (< $100): $0.50 fee
    - High tier (>= $100): 1% fee
    """

    def __init__(
        self, threshold: Decimal, low_tier_fee: Decimal, high_tier_percent: Decimal
    ):
        """
        Initialize tiered fee strategy.

        Args:
            threshold: Amount threshold to switch from low to high tier
            low_tier_fee: Flat fee for amounts below threshold
            high_tier_percent: Percentage fee for amounts >= threshold
        """
        if threshold <= 0:
            raise ValueError("El umbral debe ser positivo")
        if low_tier_fee < 0:
            raise ValueError("La comisión del nivel bajo no puede ser negativa")
        if high_tier_percent < 0 or high_tier_percent > 100:
            raise ValueError("El porcentaje del nivel alto debe estar entre 0 y 100")

        self._threshold = threshold
        self._low_tier_fee = low_tier_fee
        self._high_tier_percent = high_tier_percent

    def calculate_fee(self, amount: Decimal) -> Decimal:
        """Returns fee based on amount tier."""
        if amount < self._threshold:
            return self._low_tier_fee
        else:
            return (amount * self._high_tier_percent / Decimal("100")).quantize(
                Decimal("0.01")
            )

    def get_name(self) -> str:
        return (
            f"Comisión escalonada: <${self._threshold}=${self._low_tier_fee}, "
            f">=${self._threshold}={self._high_tier_percent}%"
        )


# ==================== Risk/Fraud Strategies (Strategy Pattern) ====================


class RiskCheckResult:
    """
    Result of a risk check.

    Contains information about whether the transaction passed
    the risk check and any rejection reason.
    """

    def __init__(self, passed: bool, reason: Optional[str] = None):
        self.passed = passed
        self.reason = reason

    def __repr__(self) -> str:
        if self.passed:
            return "RiskCheckResult(passed=True)"
        return f"RiskCheckResult(passed=False, reason='{self.reason}')"


class RiskStrategy(ABC):
    """
    Abstract base class for risk/fraud detection strategies.

    Implements the Strategy pattern to allow different risk rules
    to be applied to transactions.
    """

    @abstractmethod
    def check(
        self,
        amount: Decimal,
        account_id: UUID,
        transaction_type: str,
        get_recent_transactions: Callable,
    ) -> RiskCheckResult:
        """
        Check if a transaction passes this risk rule.

        Args:
            amount: Transaction amount
            account_id: Account performing the transaction
            transaction_type: Type of transaction
            get_recent_transactions: Callable to get recent transactions for the account

        Returns:
            RiskCheckResult indicating if check passed
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this risk strategy."""
        pass


class MaxAmountRule(RiskStrategy):
    """
    Risk rule that rejects transactions exceeding a maximum amount.

    Example: Reject any transaction > $10,000
    """

    def __init__(self, max_amount: Decimal):
        """
        Initialize max amount rule.

        Args:
            max_amount: Maximum allowed transaction amount
        """
        if max_amount <= 0:
            raise ValueError("El monto máximo debe ser positivo")
        self._max_amount = max_amount

    def check(
        self,
        amount: Decimal,
        account_id: UUID,
        transaction_type: str,
        get_recent_transactions: Callable,
    ) -> RiskCheckResult:
        """Check if amount exceeds maximum."""
        if amount > self._max_amount:
            return RiskCheckResult(
                passed=False,
                reason=f"El monto ${amount} excede el límite máximo de ${self._max_amount}",
            )
        return RiskCheckResult(passed=True)

    def get_name(self) -> str:
        return f"Monto máximo: ${self._max_amount}"


class VelocityRule(RiskStrategy):
    """
    Risk rule that rejects transactions if too many occur in a time window.

    Example: Reject if more than 5 transactions in 10 minutes
    """

    def __init__(self, max_transactions: int, time_window_minutes: int):
        """
        Initialize velocity rule.

        Args:
            max_transactions: Maximum number of transactions allowed
            time_window_minutes: Time window in minutes
        """
        if max_transactions <= 0:
            raise ValueError("El número máximo de transacciones debe ser positivo")
        if time_window_minutes <= 0:
            raise ValueError("La ventana de tiempo debe ser positiva")

        self._max_transactions = max_transactions
        self._time_window_minutes = time_window_minutes

    def check(
        self,
        amount: Decimal,
        account_id: UUID,
        transaction_type: str,
        get_recent_transactions: Callable,
    ) -> RiskCheckResult:
        """Check if transaction velocity is within limits."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=self._time_window_minutes)
        recent_txns = get_recent_transactions(account_id, cutoff_time)

        if len(recent_txns) >= self._max_transactions:
            return RiskCheckResult(
                passed=False,
                reason=(
                    f"Demasiadas transacciones: {len(recent_txns)} en los últimos "
                    f"{self._time_window_minutes} minutos (máximo: {self._max_transactions})"
                ),
            )
        return RiskCheckResult(passed=True)

    def get_name(self) -> str:
        return (
            f"Velocidad: máx {self._max_transactions} txns en "
            f"{self._time_window_minutes} min"
        )


class DailyLimitRule(RiskStrategy):
    """
    Risk rule that rejects transactions if daily limit is exceeded.

    Example: Reject if total transactions today > $50,000
    """

    def __init__(self, daily_limit: Decimal):
        """
        Initialize daily limit rule.

        Args:
            daily_limit: Maximum total transaction amount per day
        """
        if daily_limit <= 0:
            raise ValueError("El límite diario debe ser positivo")
        self._daily_limit = daily_limit

    def check(
        self,
        amount: Decimal,
        account_id: UUID,
        transaction_type: str,
        get_recent_transactions: Callable,
    ) -> RiskCheckResult:
        """Check if daily limit would be exceeded."""
        start_of_day = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_txns = get_recent_transactions(account_id, start_of_day)

        # Sum today's transaction amounts
        today_total = sum(txn.amount for txn in today_txns)
        new_total = today_total + amount

        if new_total > self._daily_limit:
            return RiskCheckResult(
                passed=False,
                reason=(
                    f"Límite diario excedido: ${today_total} gastados hoy + "
                    f"${amount} = ${new_total} > límite de ${self._daily_limit}"
                ),
            )
        return RiskCheckResult(passed=True)

    def get_name(self) -> str:
        return f"Límite diario: ${self._daily_limit}"
