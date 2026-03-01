from decimal import Decimal
from uuid import uuid4

from app.domain.rules import MaxAmountRule
from app.domain.rules import PercentFeeStrategy


def test_percent_fee_strategy_calculates_expected_fee() -> None:
    strategy = PercentFeeStrategy(Decimal("1.5"))

    fee = strategy.calculate_fee(Decimal("200.00"))

    assert fee == Decimal("3.00")


def test_max_amount_rule_rejects_amount_over_limit() -> None:
    rule = MaxAmountRule(Decimal("100.00"))

    result = rule.check(
        amount=Decimal("150.00"),
        account_id=uuid4(),
        transaction_type="DEPOSIT",
        get_recent_transactions=lambda *_: [],
    )

    assert result.passed is False
    assert "límite máximo" in (result.reason or "")
