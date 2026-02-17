"""
Business rules and strategies for the banking system.

This module implements the Strategy pattern for fee calculation.
"""

from abc import ABC, abstractmethod
from decimal import Decimal


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
