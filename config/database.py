"""
Database configuration and connection management.

Provides SQLAlchemy engine, session factory, and database dependency
for the Musical Band API.

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (default: postgresql+pg8000://user:password@localhost/musical_band_db)
    TESTING: If set to "1", uses in-memory SQLite for testing

Example:
    >>> from config.database import get_db, engine
    >>> # Database dependency
    >>> @app.get("/users")
    >>> def get_users(db: Session = Depends(get_db)):
    >>>     return db.query(User).all()
"""

from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

if os.getenv("TESTING"):
    # Use in-memory SQLite for tests
    DATABASE_URL_SQLALCHEMY = "sqlite:///:memory:"
    DATABASE_URL_PG8000 = DATABASE_URL_SQLALCHEMY  # Not used in tests, but set for consistency
else:
    load_dotenv()
    base_url = os.getenv("DATABASE_URL", "postgresql+pg8000://user:password@localhost/musical_band_db")
    DATABASE_URL_SQLALCHEMY = base_url
    DATABASE_URL_PG8000 = DATABASE_URL_SQLALCHEMY.replace('+pg8000', '') if '+pg8000' in DATABASE_URL_SQLALCHEMY else DATABASE_URL_SQLALCHEMY

DATABASE_URL = DATABASE_URL_SQLALCHEMY

# SQLAlchemy engine for database connections
engine = create_engine(DATABASE_URL)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session.

    Yields a session that is automatically closed after use.

    Yields:
        Session: SQLAlchemy database session.

    Example:
        >>> @app.get("/users")
        >>> def get_users(db: Session = Depends(get_db)):
        >>>     return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables only if not testing
if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)
