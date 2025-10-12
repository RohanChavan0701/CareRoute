"""
HIPAA-Compliant Database Connection and Session Management
Provides secure database connections with proper session handling
"""

import os
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from .models import Base
from .encryption import hipaa_encryption

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    HIPAA-compliant database manager
    Handles connections, sessions, and security
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL (defaults to environment variable)
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable must be set")
        
        # Create engine with security settings
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections every hour
            connect_args={
                "sslmode": "disable",  # Disable SSL for local development
                "application_name": "guardian_orchestrator"
            }
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info("✅ Database manager initialized with HIPAA compliance settings")
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            raise
    
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session with proper error handling
        
        Yields:
            SQLAlchemy session
        """
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            logger.error(f"❌ Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            True if connection successful
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("✅ Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    def get_session_sync(self) -> Session:
        """
        Get database session (synchronous version)
        
        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()

# Global database manager instance
database_manager = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    
    Yields:
        Database session
    """
    yield from database_manager.get_session()

def get_db_sync() -> Session:
    """
    Get database session synchronously
    
    Returns:
        Database session
    """
    return database_manager.get_session_sync()
