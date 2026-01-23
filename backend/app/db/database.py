"""
Database Connection and Session Management
Uses SQLAlchemy with async support and connection pooling
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import time

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Database URL
DATABASE_URL = str(settings.DATABASE_URL)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


# Event listeners for query logging
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.time())


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info["query_start_time"].pop(-1)
    if total_time > 1.0:  # Log slow queries (> 1 second)
        logger.warning(f"Slow query detected ({total_time:.2f}s): {statement[:100]}...")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Ensures proper cleanup after request completion.
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions (non-dependency use)"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction error: {e}", exc_info=True)
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables"""
    from .base import Base
    from app.models import user, nutrition, exercise, water, food_scan  # Import all models
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def check_db_connection() -> bool:
    """Check database connectivity"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
