from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

if os.getenv("TESTING"):
    # Use in-memory SQLite for tests
    DATABASE_URL_SQLALCHEMY = "sqlite:///:memory:"
    DATABASE_URL_PG8000 = DATABASE_URL_SQLALCHEMY  # Not used in tests, but set for consistency
else:
    base_url = os.getenv("DATABASE_URL", "postgresql+pg8000://user:password@localhost/musical_band_db")
    DATABASE_URL_SQLALCHEMY = base_url
    DATABASE_URL_PG8000 = DATABASE_URL_SQLALCHEMY.replace('+pg8000', '') if '+pg8000' in DATABASE_URL_SQLALCHEMY else DATABASE_URL_SQLALCHEMY

DATABASE_URL = DATABASE_URL_SQLALCHEMY

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)