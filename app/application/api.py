"""
FastAPI application with REST endpoints for the banking system.

Implements RESTful API with Pydantic DTOs for request/response validation.
All endpoints are documented with Swagger/OpenAPI.
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from app.application.facade import BankingFacade
from app.repositories.database import get_db_session, create_tables
from app.domain.models import (
    Currency,
    AccountStatus,
    TransactionType,
    TransactionStatus,
    CustomerNotFoundError,
    AccountNotFoundError,
    DomainException,
)


# ==================== Pydantic DTOs ====================


# Customer DTOs
class CreateCustomerRequest(BaseModel):
    """Request DTO for creating a customer."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Nombre del cliente"
    )
    email: EmailStr = Field(..., description="Email del cliente (único)")

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "Juan Pérez", "email": "juan.perez@example.com"}]
        }
    }


class CustomerResponse(BaseModel):
    """Response DTO for customer."""

    id: UUID
    name: str
    email: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}


# Account DTOs
class CreateAccountRequest(BaseModel):
    """Request DTO for creating an account."""

    customer_id: UUID = Field(..., description="ID del cliente")
    currency: Currency = Field(default=Currency.USD, description="Moneda de la cuenta")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "123e4567-e89b-12d3-a456-426614174000",
                    "currency": "USD",
                }
            ]
        }
    }


class AccountResponse(BaseModel):
    """Response DTO for account."""

    id: UUID
    customer_id: UUID
    currency: str
    balance: Decimal
    status: str
    created_at: str

    model_config = {"from_attributes": True}


# Transaction DTOs
class DepositRequest(BaseModel):
    """Request DTO for deposit."""

    account_id: UUID = Field(..., description="ID de la cuenta de destino")
    amount: Decimal = Field(
        ..., gt=0, description="Monto a depositar (debe ser positivo)"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Descripción opcional"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "account_id": "123e4567-e89b-12d3-a456-426614174000",
                    "amount": "100.50",
                    "description": "Depósito inicial",
                }
            ]
        }
    }


class WithdrawRequest(BaseModel):
    """Request DTO for withdrawal."""

    account_id: UUID = Field(..., description="ID de la cuenta de origen")
    amount: Decimal = Field(
        ..., gt=0, description="Monto a retirar (debe ser positivo)"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Descripción opcional"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "account_id": "123e4567-e89b-12d3-a456-426614174000",
                    "amount": "50.00",
                    "description": "Retiro de efectivo",
                }
            ]
        }
    }


class TransferRequest(BaseModel):
    """Request DTO for transfer."""

    from_account_id: UUID = Field(..., description="ID de la cuenta de origen")
    to_account_id: UUID = Field(..., description="ID de la cuenta de destino")
    amount: Decimal = Field(
        ..., gt=0, description="Monto a transferir (debe ser positivo)"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Descripción opcional"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "from_account_id": "123e4567-e89b-12d3-a456-426614174000",
                    "to_account_id": "987e6543-e21b-12d3-a456-426614174999",
                    "amount": "200.00",
                    "description": "Pago de servicios",
                }
            ]
        }
    }


class TransactionResponse(BaseModel):
    """Response DTO for transaction."""

    id: UUID
    type: str
    amount: Decimal
    currency: str
    from_account_id: Optional[UUID]
    to_account_id: Optional[UUID]
    status: str
    fee: Decimal
    description: Optional[str]
    rejection_reason: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}


# ==================== FastAPI Application ====================

app = FastAPI(
    title="Banking System API",
    description="API REST para sistema bancario con operaciones de depósito, retiro y transferencia",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Dependency Injection ====================


def get_facade(db: Session = Depends(get_db_session)) -> BankingFacade:
    """Dependency to inject BankingFacade."""
    return BankingFacade(db, fee_strategy_name="flat")


# ==================== Startup Event ====================


@app.on_event("startup")
def startup_event():
    """Create database tables on startup."""
    create_tables()


# ==================== Health Check ====================


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Banking API is running"}


@app.get("/health", tags=["Health"])
def health():
    """Detailed health check."""
    return {"status": "healthy", "service": "banking-api", "version": "1.0.0"}


# ==================== Customer Endpoints ====================


@app.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Customers"],
    summary="Crear nuevo cliente",
    description="Crea un nuevo cliente en el sistema con nombre y email único",
)
def create_customer(
    request: CreateCustomerRequest, facade: BankingFacade = Depends(get_facade)
):
    """Create a new customer."""
    try:
        customer = facade.create_customer(request.name, request.email)
        return CustomerResponse(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            status=customer.status,
            created_at=customer.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


@app.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    tags=["Customers"],
    summary="Obtener cliente por ID",
    description="Obtiene la información de un cliente específico",
)
def get_customer(customer_id: UUID, facade: BankingFacade = Depends(get_facade)):
    """Get customer by ID."""
    try:
        customer = facade.get_customer(customer_id)
        return CustomerResponse(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            status=customer.status,
            created_at=customer.created_at.isoformat(),
        )
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


# ==================== Account Endpoints ====================


@app.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts"],
    summary="Crear nueva cuenta",
    description="Crea una nueva cuenta para un cliente existente",
)
def create_account(
    request: CreateAccountRequest, facade: BankingFacade = Depends(get_facade)
):
    """Create a new account."""
    try:
        account = facade.create_account(request.customer_id, request.currency)
        return AccountResponse(
            id=account.id,
            customer_id=account.customer_id,
            currency=account.currency.value,
            balance=account.balance,
            status=account.status.value,
            created_at=account.created_at.isoformat(),
        )
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


@app.get(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    tags=["Accounts"],
    summary="Obtener cuenta por ID",
    description="Obtiene la información y balance de una cuenta específica",
)
def get_account(account_id: UUID, facade: BankingFacade = Depends(get_facade)):
    """Get account by ID."""
    try:
        account = facade.get_account(account_id)
        return AccountResponse(
            id=account.id,
            customer_id=account.customer_id,
            currency=account.currency.value,
            balance=account.balance,
            status=account.status.value,
            created_at=account.created_at.isoformat(),
        )
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


@app.get(
    "/customers/{customer_id}/accounts",
    response_model=List[AccountResponse],
    tags=["Accounts"],
    summary="Listar cuentas de un cliente",
    description="Obtiene todas las cuentas de un cliente específico",
)
def list_customer_accounts(
    customer_id: UUID, facade: BankingFacade = Depends(get_facade)
):
    """List all accounts for a customer."""
    try:
        accounts = facade.get_customer_accounts(customer_id)
        return [
            AccountResponse(
                id=acc.id,
                customer_id=acc.customer_id,
                currency=acc.currency.value,
                balance=acc.balance,
                status=acc.status.value,
                created_at=acc.created_at.isoformat(),
            )
            for acc in accounts
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


# ==================== Transaction Endpoints ====================


@app.post(
    "/transactions/deposit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Transactions"],
    summary="Depositar dinero",
    description="Deposita dinero en una cuenta. Aplica comisiones y reglas de riesgo.",
)
def deposit(request: DepositRequest, facade: BankingFacade = Depends(get_facade)):
    """Deposit money into an account."""
    try:
        transaction = facade.deposit(
            request.account_id, request.amount, request.description
        )
        return _transaction_to_response(transaction)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


@app.post(
    "/transactions/withdraw",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Transactions"],
    summary="Retirar dinero",
    description="Retira dinero de una cuenta. Valida fondos suficientes, aplica comisiones y reglas de riesgo.",
)
def withdraw(request: WithdrawRequest, facade: BankingFacade = Depends(get_facade)):
    """Withdraw money from an account."""
    try:
        transaction = facade.withdraw(
            request.account_id, request.amount, request.description
        )
        return _transaction_to_response(transaction)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


@app.post(
    "/transactions/transfer",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Transactions"],
    summary="Transferir dinero",
    description="Transfiere dinero entre dos cuentas. Valida fondos, aplica comisiones y reglas de riesgo.",
)
def transfer(request: TransferRequest, facade: BankingFacade = Depends(get_facade)):
    """Transfer money between accounts."""
    try:
        transaction = facade.transfer(
            request.from_account_id,
            request.to_account_id,
            request.amount,
            request.description,
        )
        return _transaction_to_response(transaction)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


@app.get(
    "/accounts/{account_id}/transactions",
    response_model=List[TransactionResponse],
    tags=["Transactions"],
    summary="Listar transacciones de una cuenta",
    description="Obtiene el historial de transacciones de una cuenta con paginación",
)
def list_transactions(
    account_id: UUID,
    limit: int = 100,
    offset: int = 0,
    facade: BankingFacade = Depends(get_facade),
):
    """List transactions for an account."""
    try:
        transactions = facade.list_transactions(account_id, limit, offset)
        return [_transaction_to_response(txn) for txn in transactions]
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


@app.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    tags=["Transactions"],
    summary="Obtener transacción por ID",
    description="Obtiene los detalles de una transacción específica",
)
def get_transaction(transaction_id: UUID, facade: BankingFacade = Depends(get_facade)):
    """Get transaction by ID."""
    try:
        transaction = facade.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transacción {transaction_id} no encontrada",
            )
        return _transaction_to_response(transaction)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


# ==================== Helper Functions ====================


def _transaction_to_response(transaction) -> TransactionResponse:
    """Convert domain Transaction to TransactionResponse DTO."""
    return TransactionResponse(
        id=transaction.id,
        type=transaction.type.value,
        amount=transaction.amount,
        currency=transaction.currency.value,
        from_account_id=transaction.from_account_id,
        to_account_id=transaction.to_account_id,
        status=transaction.status.value,
        fee=transaction.fee,
        description=transaction.description,
        rejection_reason=transaction.rejection_reason,
        created_at=transaction.created_at.isoformat(),
    )
