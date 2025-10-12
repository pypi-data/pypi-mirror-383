from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session as SASession

# Base class for SQLAlchemy models used internally by Spiderweb
Base = declarative_base()

# Type alias for sessions
DBSession = SASession


def create_sqlite_engine(db_path: Union[str, Path]) -> Engine:
    """Create a SQLite engine from a file path."""
    path = Path(db_path)
    # Ensure directory exists
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}", future=True)


def create_session_factory(engine: Engine):
    """Return a configured sessionmaker bound to the given engine."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
