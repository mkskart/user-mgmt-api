"""Database configuration & bootstrap utilities."""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/postgres",
)

# SQLAlchemy engine & session factory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative model base class
Base = declarative_base()


def init_db() -> None:
    """Create all tables if they don’t already exist."""
    # Circular‑import safe import
    from backend.app import models  # noqa: F401 ensures model metadata registered

    logger.info("Ensuring database schema exists…")
    Base.metadata.create_all(bind=engine)
    logger.success("Database schema ready ✅")


# Dependency helper for routes
def get_db():
    """Generator that yields DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()