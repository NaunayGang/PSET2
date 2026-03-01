from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.models import Account
from app.domain.models import AccountFrozenError
from app.domain.models import AccountStatus
from app.domain.models import InsufficientFundsError


def test_account_debit_raises_insufficient_funds() -> None:
    account = Account(customer_id=uuid4(), balance=Decimal("50.00"))

    with pytest.raises(InsufficientFundsError):
        account.debit(Decimal("100.00"))


def test_account_debit_rejected_when_account_frozen() -> None:
    account = Account(customer_id=uuid4(), balance=Decimal("100.00"))
    account.status = AccountStatus.FROZEN

    with pytest.raises(AccountFrozenError):
        account.debit(Decimal("10.00"))
