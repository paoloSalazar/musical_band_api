from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL_SQLALCHEMY = os.getenv("DATABASE_URL", "postgresql+pg8000://user:password@localhost/musical_band_db")
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