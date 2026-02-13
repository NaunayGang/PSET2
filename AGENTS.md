# AGENTS.md: Development Guidelines

This document provides guidelines for agentic coding agents working on the PSET2 Banking System project.

## Project Overview

A university project implementing a clean architecture banking system with:
- **Backend**: FastAPI + SQLAlchemy (REST API)
- **Frontend**: Streamlit (UI)
- **Architecture**: Domain-Driven Design with repositories, services, and domain models

## Build, Lint, and Test Commands

### Environment Setup
```bash
# Nix (recommended)
nix develop

# Or with pip
pip install -r requirements.txt
```

### Run Backend
```bash
uvicorn app.application.api:app --reload --host 0.0.0.0 --port 8000
```

### Run Frontend
```bash
streamlit run frontend/streamlit_app.py
```

### Testing
```bash
# Run all tests
pytest

# Run a single test
pytest tests/test_banking_service.py::test_create_customer
```

### Optional: Formatting & Linting
```bash
# Optional: Ruff for linting/formatting
ruff check . && ruff format .
```

## Code Style and Conventions

### Directory Structure
```
app/
├── domain/           # Core business logic and models
│   ├── models.py     # Entity, Value Object, Aggregate Root definitions
│   └── rules.py      # Strategy patterns, business rules
├── services/         # Application logic and orchestration
├── repositories/     # Data persistence abstractions
└── application/      # API layer and facades
    ├── api.py        # FastAPI routes and DTOs
    └── facade.py     # Single entry point for business logic
```

### Imports
- Use absolute imports: `from app.domain.models import Customer` (not relative)
- Group imports in order: stdlib → third-party → local
- One import per line for clarity
- Order third-party by: fastapi, sqlalchemy, pydantic, then others

### Type Hints
- **Required** for all function signatures and class attributes
- Define types in domain models using Pydantic models
- Example:
```python
from pydantic import BaseModel

class CreateCustomerRequest(BaseModel):
    name: str
    email: str
    
def create_customer(request: CreateCustomerRequest) -> Customer:
    pass
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `Customer`, `BankingService`, `CustomerRepository`)
- **Functions/Methods**: snake_case (e.g., `create_customer`, `get_account_balance`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_TRANSACTION_AMOUNT`)
- **Private attributes**: `_prefix` (e.g., `_balance`)
- **Domain entities**: Singular nouns (e.g., `Customer`, not `Customers`)

### Formatting
- **Line length**: Max 100 characters
- **Indentation**: 4 spaces
- **Blank lines**: 2 between top-level definitions, 1 between methods
- Optional: Use Ruff for formatting and type checking: `ruff check app/ && ruff format app/`

### Error Handling
- Define custom exceptions in `domain/` for business logic errors
- Use descriptive exception names: `InsufficientFundsError`, `CustomerNotFoundError`
- Catch specific exceptions, never bare `except:`
- Log errors with context before raising:
```python
try:
    # operation
except SpecificError as e:
    logger.error(f"Failed to process transaction: {e}", exc_info=True)
    raise
```

### Domain-Driven Design Principles
- **Models** (`domain/models.py`): Pure business logic, no external dependencies
- **Rules/Strategies** (`domain/rules.py`): Fee calculations, risk assessments
- **Repositories** (`repositories/`): Abstract data access, return domain entities
- **Services** (`services/`): Orchestrate repositories and apply business logic
- **Application** (`application/`): FastAPI routes, DTOs (data transfer objects for API only)
- Use Pydantic models only for API request/response, not for domain entities

### Testing
- **Location**: `tests/` directory mirroring `app/` structure
- **Naming**: `test_*.py` files with `test_*()` functions
- **Fixtures**: Use pytest fixtures in `conftest.py` for test setup
- **Mocking**: Mock repositories in service tests, not domain logic
```python
def test_create_customer():
    # Arrange
    repo = MockCustomerRepository()
    service = BankingService(repo)
    
    # Act
    customer = service.create_customer("John Doe", "john@example.com")
    
    # Assert
    assert customer.name == "John Doe"
```

### Git Workflow
Follow Angular commit style:
- **Prefix**: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`
- **Form**: Use imperative form: "adds feature" not "added feature"
- **Example**: `feat: adds Customer entity to domain models`
- Keep commits atomic and focused
- Link PRs to related issues when applicable

### Branch Naming
- Feature branches: `feature/<issue-description>`
- Fix branches: `fix/<issue-description>`

### Documentation
- Module docstrings explaining purpose
- Function docstrings for public APIs (use Google-style format)
- Complex business logic should have inline comments
- Keep docs in `docs-src/` directory in the case of markdown files, and `docs` for everything else (diagrams, architecture notes, etc.)

## Key Technologies

- **FastAPI**: Modern async web framework with automatic validation
- **SQLAlchemy 2.0**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Pytest**: Testing framework
- **Streamlit**: Rapid UI prototyping for data/business applications

## Development Tips

1. Optional: Use Ruff for linting and formatting: `ruff check app/ && ruff format app/`
2. Run full test suite before pushing: `pytest`
3. Ensure Docker builds pass: `docker compose build`
4. API documentation is auto-generated at `/docs` endpoint
5. Keep domain models persistence-agnostic; repositories handle DB details
