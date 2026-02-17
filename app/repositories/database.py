"""
Database configuration and session management.

Provides database connection, session factory, and table creation utilities.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.repositories.orm_models import Base


# Database configuration from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "pset2")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pset2password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "pset2_db")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get a database session with automatic commit/rollback.

    Usage:
        with get_session() as session:
            # Use session here
            ...
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to inject database session.

    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db_session)):
            ...
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Commit after successful request
    except Exception:
        session.rollback()  # Rollback on error
        raise
    finally:
        session.close()
