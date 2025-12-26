"""
Database Configuration - Connection Settings

This file contains:
1. Database URL (connection string)
2. SQLAlchemy Engine (connection pool)
3. SessionLocal factory (creates database sessions)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================================
# STEP 1: Database Connection URL
# ============================================================================

# Format: dialect+driver://username:password@host:port/database
# Example: mysql+pymysql://root:root@localhost:3306/toll_management

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/toll_management"

# Breaking down the URL:
# - mysql        → Database type
# - pymysql      → Python driver (the network layer)
# - root         → MySQL username
# - root         → MySQL password
# - localhost    → MySQL server location (same machine)
# - 3306         → MySQL default port
# - toll_management → Database name (we'll create this)


# ============================================================================
# STEP 2: Create SQLAlchemy Engine
# ============================================================================

# The engine manages connections to the database
    # Think of it as a "connection pool" - reuses connections for efficiency

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set True to see SQL queries in console (for learning)
    pool_pre_ping=True,  # Check connection is alive before using
    pool_recycle=3600  # Recycle connections every hour
)

# What is 'echo=True'?
# - Shows actual SQL queries in console
# - Great for learning: you can see Python → SQL conversion!
# - Set to False in production


# ============================================================================
# STEP 3: Create Session Factory
# ============================================================================

# SessionLocal is a factory that creates database sessions
# A session = a "conversation" with the database
# - session.add() = "I want to save this"
# - session.commit() = "Actually save it now"
# - session.rollback() = "Cancel everything, undo!"

SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-save (we control with commit())
    autoflush=False,   # Don't auto-send to DB (we control timing)
    bind=engine        # Connect to our engine
)


# ============================================================================
# STEP 4: Create Base Class for Models
# ============================================================================

# All database models will inherit from this Base class
# This is how SQLAlchemy tracks our models and creates tables

Base = declarative_base()

# Example usage (we'll do this next):
# class TollPassDB(Base):
#     __tablename__ = "toll_passes"
#     id = Column(Integer, primary_key=True)
#     ...


# ============================================================================
# STEP 5: Helper Function - Get Database Session
# ============================================================================

def get_db():
    """
    Generator function that yields a database session.

    Used in repositories to get a database connection.
    Automatically closes the session when done.

    Usage:
        db = next(get_db())
        db.query(TollPassDB).all()
        db.close()

    Or with context manager:
        with next(get_db()) as db:
            db.query(TollPassDB).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Always close the session when done
