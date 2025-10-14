"""Database connection and session management."""

from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import settings
from .models import Base


# Create engine based on configuration
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DATABASE_ECHO,
    )

    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DATABASE_ECHO,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all database tables.

    This should be called during application startup or migrations.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all database tables.

    WARNING: This will delete all data. Use only for testing or development.
    """
    Base.metadata.drop_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency for FastAPI.

    Yields:
        Database session that will be automatically closed after request.

    Example:
        ```python
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Get database session context manager for standalone use.

    Yields:
        Database session that will be automatically committed and closed.

    Example:
        ```python
        with get_db_context() as db:
            user = User(username="john", email="john@example.com")
            db.add(user)
            db.commit()
        ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class DatabaseManager:
    """Database manager for common operations."""

    def __init__(self):
        """Initialize database manager."""
        self.engine = engine
        self.SessionLocal = SessionLocal

    def create_all(self) -> None:
        """Create all tables."""
        create_tables()

    def drop_all(self) -> None:
        """Drop all tables."""
        drop_tables()

    def reset(self) -> None:
        """Reset database (drop and create all tables)."""
        self.drop_all()
        self.create_all()

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            New database session. Caller is responsible for closing.
        """
        return SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around operations.

        Yields:
            Database session with automatic commit/rollback.
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def check_connection(self) -> bool:
        """Check if database connection is working.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            with self.session_scope() as session:
                session.execute("SELECT 1")
            return True
        except Exception:
            return False


# Global database manager instance
db_manager = DatabaseManager()
