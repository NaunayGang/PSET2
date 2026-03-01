from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient

from app.application.api import app
from app.application.api import get_facade
from app.domain.models import Currency
from app.domain.models import Transaction
from app.domain.models import TransactionStatus
from app.domain.models import TransactionType


class FakeFacade:
    def deposit(self, account_id: UUID, amount: Decimal, description: str | None = None) -> Transaction:
        return Transaction(
            type=TransactionType.DEPOSIT,
            amount=amount,
            currency=Currency.USD,
            to_account_id=account_id,
            status=TransactionStatus.APPROVED,
            fee=Decimal("0.00"),
            description=description,
        )

    def transfer(
        self,
        from_account_id: UUID,
        to_account_id: UUID,
        amount: Decimal,
        description: str | None = None,
    ) -> Transaction:
        return Transaction(
            type=TransactionType.TRANSFER,
            amount=amount,
            currency=Currency.USD,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            status=TransactionStatus.APPROVED,
            fee=Decimal("0.00"),
            description=description,
        )


def test_deposit_happy_path(monkeypatch) -> None:
    monkeypatch.setattr("app.application.api.create_tables", lambda: None)
    app.dependency_overrides[get_facade] = lambda: FakeFacade()

    with TestClient(app) as client:
        response = client.post(
            "/transactions/deposit",
            json={
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "amount": "100.00",
                "description": "Initial deposit",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert payload["type"] == "DEPOSIT"
    assert payload["status"] == "APPROVED"
    assert payload["amount"] == "100.00"


def test_transfer_happy_path(monkeypatch) -> None:
    monkeypatch.setattr("app.application.api.create_tables", lambda: None)
    app.dependency_overrides[get_facade] = lambda: FakeFacade()

    with TestClient(app) as client:
        response = client.post(
            "/transactions/transfer",
            json={
                "from_account_id": "123e4567-e89b-12d3-a456-426614174000",
                "to_account_id": "987e6543-e21b-12d3-a456-426614174999",
                "amount": "25.00",
                "description": "Transfer test",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert payload["type"] == "TRANSFER"
    assert payload["status"] == "APPROVED"
    assert payload["amount"] == "25.00"
