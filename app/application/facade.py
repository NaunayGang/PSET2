"""
Banking Facade - Single entry point for all banking operations.

Implements the Facade pattern to provide a simplified interface
to the complex subsystems (services, repositories, strategies).
This is the only interface that the API layer should interact with.
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.models import Customer, Account, Transaction, Currency
from app.domain.rules import (
    NoFeeStrategy,
    FlatFeeStrategy,
    PercentFeeStrategy,
    TieredFeeStrategy,
    MaxAmountRule,
    VelocityRule,
    DailyLimitRule,
)
from app.services.banking_service import BankingService
from app.repositories.customer_repository import SQLAlchemyCustomerRepository
from app.repositories.account_repository import SQLAlchemyAccountRepository
from app.repositories.transaction_repository import (
    SQLAlchemyTransactionRepository,
    SQLAlchemyLedgerEntryRepository,
)


class BankingFacade:
    """
    Facade providing simplified access to banking operations.

    Coordinates all subsystems and provides a clean API for the
    application layer. Handles dependency injection and configuration.
    """

    def __init__(self, session: Session, fee_strategy_name: str = "flat"):
        """
        Initialize banking facade.

        Args:
            session: Database session
            fee_strategy_name: Fee strategy to use ("none", "flat", "percent", "tiered")
        """
        # Initialize repositories
        self._customer_repo = SQLAlchemyCustomerRepository(session)
        self._account_repo = SQLAlchemyAccountRepository(session)
        self._transaction_repo = SQLAlchemyTransactionRepository(session)
        self._ledger_repo = SQLAlchemyLedgerEntryRepository(session)

        # Configure fee strategy
        self._fee_strategy = self._get_fee_strategy(fee_strategy_name)

        # Configure risk strategies
        self._risk_strategies = [
            MaxAmountRule(Decimal("10000.00")),  # Max $10,000 per transaction
            VelocityRule(5, 10),  # Max 5 transactions in 10 minutes
            DailyLimitRule(Decimal("50000.00")),  # Max $50,000 per day
        ]

        # Initialize service
        self._service = BankingService(
            customer_repo=self._customer_repo,
            account_repo=self._account_repo,
            transaction_repo=self._transaction_repo,
            ledger_repo=self._ledger_repo,
            fee_strategy=self._fee_strategy,
            risk_strategies=self._risk_strategies,
        )

    def _get_fee_strategy(self, strategy_name: str):
        """Get fee strategy by name."""
        strategies = {
            "none": NoFeeStrategy(),
            "flat": FlatFeeStrategy(Decimal("0.50")),  # $0.50 per transaction
            "percent": PercentFeeStrategy(Decimal("1.5")),  # 1.5%
            "tiered": TieredFeeStrategy(
                threshold=Decimal("100.00"),
                low_tier_fee=Decimal("0.50"),
                high_tier_percent=Decimal("1.0"),
            ),
        }
        return strategies.get(strategy_name, strategies["flat"])

    # ==================== Customer Operations ====================

    def create_customer(self, name: str, email: str) -> Customer:
        """
        Create a new customer.

        Args:
            name: Customer name
            email: Customer email (must be unique)

        Returns:
            Created customer
        """
        return self._service.create_customer(name, email)

    def get_customer(self, customer_id: UUID) -> Customer:
        """
        Get customer by ID.

        Args:
            customer_id: Customer ID

        Returns:
            Customer
        """
        return self._service.get_customer(customer_id)

    # ==================== Account Operations ====================

    def create_account(
        self, customer_id: UUID, currency: Currency = Currency.USD
    ) -> Account:
        """
        Create a new account for a customer.

        Args:
            customer_id: Customer ID
            currency: Account currency

        Returns:
            Created account
        """
        return self._service.create_account(customer_id, currency)

    def get_account(self, account_id: UUID) -> Account:
        """
        Get account by ID.

        Args:
            account_id: Account ID

        Returns:
            Account with current balance
        """
        return self._service.get_account(account_id)

    def get_customer_accounts(self, customer_id: UUID) -> List[Account]:
        """
        Get all accounts for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of customer accounts
        """
        return self._account_repo.find_by_customer_id(customer_id)

    # ==================== Transaction Operations ====================

    def deposit(
        self, account_id: UUID, amount: Decimal, description: Optional[str] = None
    ) -> Transaction:
        """
        Deposit money into an account.

        Args:
            account_id: Account to deposit to
            amount: Amount to deposit
            description: Optional description

        Returns:
            Transaction (approved or rejected)
        """
        return self._service.deposit(account_id, amount, description)

    def withdraw(
        self, account_id: UUID, amount: Decimal, description: Optional[str] = None
    ) -> Transaction:
        """
        Withdraw money from an account.

        Args:
            account_id: Account to withdraw from
            amount: Amount to withdraw
            description: Optional description

        Returns:
            Transaction (approved or rejected)
        """
        return self._service.withdraw(account_id, amount, description)

    def transfer(
        self,
        from_account_id: UUID,
        to_account_id: UUID,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> Transaction:
        """
        Transfer money between accounts.

        Args:
            from_account_id: Source account
            to_account_id: Destination account
            amount: Amount to transfer
            description: Optional description

        Returns:
            Transaction (approved or rejected)
        """
        return self._service.transfer(
            from_account_id, to_account_id, amount, description
        )

    def list_transactions(
        self, account_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[Transaction]:
        """
        List transactions for an account.

        Args:
            account_id: Account ID
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip

        Returns:
            List of transactions
        """
        return self._service.list_transactions(account_id, limit, offset)

    def get_transaction(self, transaction_id: UUID) -> Optional[Transaction]:
        """
        Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction or None if not found
        """
        return self._transaction_repo.find_by_id(transaction_id)
