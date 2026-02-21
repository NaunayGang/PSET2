"""
Banking service for orchestrating business logic.

This service coordinates repositories, strategies, and domain logic
to implement banking use cases.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.domain.models import (
    Customer,
    Account,
    Transaction,
    LedgerEntry,
    Currency,
    TransactionType,
    TransactionStatus,
    LedgerDirection,
    CustomerNotFoundError,
    AccountNotFoundError,
    InsufficientFundsError,
)
from app.domain.rules import FeeStrategy, RiskStrategy, RiskCheckResult
from app.domain.factories import TransactionFactory, TransactionBuilder
from app.repositories.customer_repository import CustomerRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import (
    TransactionRepository,
    LedgerEntryRepository,
)


class BankingService:
    """
    Banking service orchestrating domain operations.

    Coordinates repositories, fee strategies, and risk strategies
    to execute banking transactions with proper validation.
    """

    def __init__(
        self,
        customer_repo: CustomerRepository,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
        ledger_repo: LedgerEntryRepository,
        fee_strategy: FeeStrategy,
        risk_strategies: List[RiskStrategy],
    ):
        self._customer_repo = customer_repo
        self._account_repo = account_repo
        self._transaction_repo = transaction_repo
        self._ledger_repo = ledger_repo
        self._fee_strategy = fee_strategy
        self._risk_strategies = risk_strategies

    def create_customer(self, name: str, email: str) -> Customer:
        """Create a new customer."""
        # Check if email already exists
        existing = self._customer_repo.find_by_email(email)
        if existing:
            raise ValueError(f"El cliente con email {email} ya existe")

        customer = Customer(name=name, email=email)
        return self._customer_repo.save(customer)

    def get_customer(self, customer_id: UUID) -> Customer:
        """Get customer by ID."""
        customer = self._customer_repo.find_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Cliente {customer_id} no encontrado")
        return customer

    def create_account(
        self, customer_id: UUID, currency: Currency = Currency.USD
    ) -> Account:
        """Create a new account for a customer."""
        # Verify customer exists
        customer = self.get_customer(customer_id)

        account = Account(customer_id=customer_id, currency=currency)
        return self._account_repo.save(account)

    def get_account(self, account_id: UUID) -> Account:
        """Get account by ID."""
        account = self._account_repo.find_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Cuenta {account_id} no encontrada")
        return account

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
            Approved transaction
        """
        # Get account and validate
        account = self.get_account(account_id)

        # Calculate fee
        fee = self._fee_strategy.calculate_fee(amount)

        # Check risk rules
        risk_result = self._check_risk_rules(
            amount, account_id, TransactionType.DEPOSIT
        )

        # Create transaction
        transaction = TransactionFactory.create_deposit(
            to_account_id=account_id,
            amount=amount,
            currency=account.currency,
            description=description,
            fee=fee,
        )

        if not risk_result.passed:
            # Reject transaction
            transaction.reject(risk_result.reason or "Regla de riesgo no pasada")
            self._transaction_repo.save(transaction)
            return transaction

        # Apply deposit
        net_amount = amount - fee
        account.credit(net_amount)

        # Approve transaction
        transaction.approve()

        # Save account and transaction
        self._account_repo.save(account)
        self._transaction_repo.save(transaction)

        # Create ledger entry
        ledger_entry = LedgerEntry(
            account_id=account_id,
            transaction_id=transaction.id,
            direction=LedgerDirection.CREDIT,
            amount=net_amount,
            description=f"Depósito - Fee: ${fee}",
        )
        self._ledger_repo.save(ledger_entry)

        return transaction

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
            Approved or rejected transaction
        """
        # Get account and validate
        account = self.get_account(account_id)

        # Calculate fee
        fee = self._fee_strategy.calculate_fee(amount)
        total_amount = amount + fee

        # Check risk rules
        risk_result = self._check_risk_rules(
            amount, account_id, TransactionType.WITHDRAW
        )

        # Create transaction
        transaction = TransactionFactory.create_withdraw(
            from_account_id=account_id,
            amount=amount,
            currency=account.currency,
            description=description,
            fee=fee,
        )

        if not risk_result.passed:
            # Reject transaction
            transaction.reject(risk_result.reason or "Regla de riesgo no pasada")
            self._transaction_repo.save(transaction)
            return transaction

        # Check sufficient funds
        if account.balance < total_amount:
            reason = (
                f"Fondos insuficientes: balance=${account.balance}, "
                f"requerido=${total_amount} (monto=${amount} + fee=${fee})"
            )
            transaction.reject(reason)
            self._transaction_repo.save(transaction)
            return transaction

        # Apply withdrawal
        account.debit(total_amount)

        # Approve transaction
        transaction.approve()

        # Save account and transaction
        self._account_repo.save(account)
        self._transaction_repo.save(transaction)

        # Create ledger entry
        ledger_entry = LedgerEntry(
            account_id=account_id,
            transaction_id=transaction.id,
            direction=LedgerDirection.DEBIT,
            amount=total_amount,
            description=f"Retiro - Fee: ${fee}",
        )
        self._ledger_repo.save(ledger_entry)

        return transaction

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
            Approved or rejected transaction
        """
        # Get accounts and validate
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)

        # Verify same currency
        if from_account.currency != to_account.currency:
            raise ValueError("Las cuentas deben tener la misma moneda para transferir")

        # Calculate fee
        fee = self._fee_strategy.calculate_fee(amount)
        total_amount = amount + fee

        # Check risk rules
        risk_result = self._check_risk_rules(
            amount, from_account_id, TransactionType.TRANSFER
        )

        # Create transaction
        transaction = TransactionFactory.create_transfer(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            currency=from_account.currency,
            description=description,
            fee=fee,
        )

        if not risk_result.passed:
            # Reject transaction
            transaction.reject(risk_result.reason or "Regla de riesgo no pasada")
            self._transaction_repo.save(transaction)
            return transaction

        # Check sufficient funds
        if from_account.balance < total_amount:
            reason = (
                f"Fondos insuficientes: balance=${from_account.balance}, "
                f"requerido=${total_amount} (monto=${amount} + fee=${fee})"
            )
            transaction.reject(reason)
            self._transaction_repo.save(transaction)
            return transaction

        # Apply transfer (atomic at application level)
        from_account.debit(total_amount)
        to_account.credit(amount)

        # Approve transaction
        transaction.approve()

        # Save accounts and transaction
        self._account_repo.save(from_account)
        self._account_repo.save(to_account)
        self._transaction_repo.save(transaction)

        # Create ledger entries (double-entry)
        debit_entry = LedgerEntry(
            account_id=from_account_id,
            transaction_id=transaction.id,
            direction=LedgerDirection.DEBIT,
            amount=total_amount,
            description=f"Transferencia enviada - Fee: ${fee}",
        )
        credit_entry = LedgerEntry(
            account_id=to_account_id,
            transaction_id=transaction.id,
            direction=LedgerDirection.CREDIT,
            amount=amount,
            description="Transferencia recibida",
        )

        self._ledger_repo.save(debit_entry)
        self._ledger_repo.save(credit_entry)

        return transaction

    def list_transactions(
        self, account_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[Transaction]:
        """List transactions for an account."""
        # Verify account exists
        self.get_account(account_id)

        return self._transaction_repo.find_by_account_id(
            account_id, limit=limit, offset=offset
        )

    def _check_risk_rules(
        self, amount: Decimal, account_id: UUID, transaction_type: TransactionType
    ) -> RiskCheckResult:
        """
        Check all risk strategies.

        Returns the first failed check or success if all pass.
        """

        def get_recent_transactions(acc_id: UUID, since: datetime) -> List[Transaction]:
            return self._transaction_repo.find_recent_by_account(acc_id, since)

        for strategy in self._risk_strategies:
            result = strategy.check(
                amount=amount,
                account_id=account_id,
                transaction_type=transaction_type.value,
                get_recent_transactions=get_recent_transactions,
            )
            if not result.passed:
                return result

        return RiskCheckResult(passed=True)
