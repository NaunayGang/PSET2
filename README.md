# PSET2 Banking System (Course Project)

End-to-end fintech mini-bank built for System Design PSET #2.

This repository implements:
- FastAPI backend with documented REST endpoints.
- Streamlit frontend that consumes the API (no direct DB access).
- PostgreSQL persistence via SQLAlchemy.
- Clean architecture with Domain, Services, Repositories, and Application layers.
- Docker Compose orchestration for the complete stack.

## 1) Project Scope (MVP)

Functional scope implemented in this project:
- Create customers.
- Create accounts for customers.
- Execute `deposit`, `withdraw`, and `transfer` transactions.
- Query account details and balance.
- List account transactions.
- Apply configurable business rules (fees and risk validations).

## 2) Technology Stack

- Backend: FastAPI + Uvicorn
- ORM/Persistence: SQLAlchemy 2.0 + PostgreSQL 15
- Frontend: Streamlit
- Validation: Pydantic
- Containers: Docker + Docker Compose

## 3) Repository Structure

```text
app/
  application/    # API layer + facade integration
  domain/         # core entities, rules, invariants, exceptions
  services/       # use case orchestration
  repositories/   # repository interfaces + SQLAlchemy implementations
frontend/
  streamlit_app.py
docs/
docs-src/
  diagrams/
```

## 4) Docker-Only Setup (Required)

This project is designed to be evaluated with one command:

```bash
docker compose up --build
```

### 4.1 Prerequisites

- Docker Engine/Desktop installed.
- Docker Compose v2 available (`docker compose version`).
- Free ports:
  - `8000` for API
  - `8501` for Streamlit UI
  - `5432` for PostgreSQL

### 4.2 Step-by-Step Run Guide (Professor Workflow)

1. Clone and enter repository:

```bash
git clone https://github.com/NaunayGang/PSET2.git
cd PSET2
```

2. Start all services (db + api + ui):

```bash
docker compose up --build
```

3. Wait until startup logs show services are ready.

4. In a second terminal, verify service status:

```bash
docker compose ps
```

Expected: `db`, `api`, and `ui` are running.

5. Verify backend health:

```bash
curl http://localhost:8000/health
```

Expected response includes:
- `status: healthy`
- `service: banking-api`

6. Open application URLs:
- API root: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Streamlit UI: http://localhost:8501

7. (Optional quick smoke test script):

```bash
bash test_api.sh
```

### 4.3 Stop Services

```bash
docker compose down
```

Remove DB volume as well:

```bash
docker compose down -v
```

## 5) API Endpoints (Key)

### Health
- `GET /`
- `GET /health`

### Customers
- `POST /customers`
- `GET /customers/{customer_id}`

### Accounts
- `POST /accounts`
- `GET /accounts/{account_id}`
- `GET /customers/{customer_id}/accounts`

### Transactions
- `POST /transactions/deposit`
- `POST /transactions/withdraw`
- `POST /transactions/transfer`
- `GET /accounts/{account_id}/transactions`
- `GET /transactions/{transaction_id}`

Authoritative API contract is available in Swagger: http://localhost:8000/docs

## 6) UI Flows (Streamlit)

Main pages in the frontend:
1. **Create Customer**: validates name/email and creates a customer.
2. **Create Account**: creates account by customer UUID and currency.
3. **Account Details**: shows balance, metadata, and transaction history.
4. **Deposit**: submits deposit transaction.
5. **Withdraw**: submits withdrawal transaction with validation.
6. **Transfer**: submits transfer between two accounts.

Recommended demo flow:
1. Create customer.
2. Create account.
3. Deposit funds.
4. Withdraw funds.
5. Transfer between two accounts.
6. Verify ledger effect through account transaction history.

## 7) Design Decisions (Why these patterns)

### 7.1 Layered / Clean Architecture

- `domain`: pure business logic and invariants.
- `services`: orchestrates use cases.
- `repositories`: persistence abstraction and ORM implementations.
- `application`: HTTP API + DTOs + dependency wiring.

Reason: keeps business rules independent from framework/DB details and improves testability.

### 7.2 Facade Pattern (`BankingFacade`)

API endpoints call a single facade entrypoint for core operations:
- `create_customer`
- `create_account`
- `deposit`
- `withdraw`
- `transfer`
- `get_account`
- `list_transactions`

Reason: centralizes use-case orchestration and prevents route handlers from coupling to lower layers.

### 7.3 Strategy Pattern

Fee and risk behavior are modeled as interchangeable strategies.

Reason: policy changes are isolated and can evolve without rewriting endpoint logic.

### 7.4 Creational Patterns

Factory/Builder are used for transaction construction and consistency.

Reason: enforces valid transaction creation paths and keeps object assembly explicit.

## 8) UML and Supporting Documentation

Diagrams are maintained under `docs-src/diagrams/`:
- `use-case-diagram.puml`
- `class-diagram.puml`
- `sequence-transfer.puml`

Additional generated documentation/resources are under `docs/`.

## 9) Professor Verification Checklist (Aligned to PSET2 Instructions)

Use this checklist to validate deliverables quickly.

### 9.1 DevOps / Compose
- [x] `docker compose up --build` starts `db`, `api`, and `ui`.
- [x] API responds at `http://localhost:8000/health`.
- [x] UI is reachable at `http://localhost:8501`.

### 9.2 Backend Scope
- [x] Customer creation endpoint works.
- [x] Account creation endpoint works.
- [x] Deposit/withdraw/transfer endpoints work.
- [x] Account query + account transaction list work.

### 9.3 Frontend Scope
- [x] UI can create customer and account.
- [x] UI can execute deposit/withdraw/transfer.
- [x] UI displays account details and transactions.
- [x] UI displays business-rule errors clearly.

### 9.4 Architecture & Patterns
- [x] Facade is used as API entrypoint for business operations.
- [x] Strategy is used for fees/risk policies.
- [x] Repository abstraction separates persistence from domain logic.
- [x] Creational pattern(s) are documented and used.

### 9.5 Course PM / Delivery Artifacts
- [x] GitHub Project board exists with required columns.
- [x] Issues include labels + acceptance checklist + estimate.
- [x] PRs reference issues and include review checklist.
- [x] UML deliverables are present in project docs.

## 10) Notes for Evaluation

- The official execution path for this README is Docker Compose only.
- Swagger (`/docs`) is the best source to inspect request/response DTOs.
- For practical API exercise, `test_api.sh` can be used as a quick smoke test.
- For the full issue #12 submission flow, see `docs-src/DEMO_CHECKLIST.md` and run `bash test_api.sh`.
