"""
Database Models - SQLAlchemy ORM Models

These models map to MySQL database tables.
They are DIFFERENT from domain models (models.py).

Domain Models (models.py):
  - Used by business logic (services, system.py)
  - Python dataclasses
  - In-memory

Database Models (this file):
  - Used by repositories for MySQL storage
  - SQLAlchemy models
  - Persisted to disk
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database.config import Base


# ============================================================================
# Enums (must match domain models)
# ============================================================================

class VehicleTypeDB(str, enum.Enum):
    """Vehicle type enum for database"""
    TWO_WHEELER = "two_wheeler"
    FOUR_WHEELER = "four_wheeler"


class PassTypeDB(str, enum.Enum):
    """Pass type enum for database"""
    SINGLE = "single"
    RETURN = "return"
    SEVEN_DAY = "seven_day"


class PassStatusDB(str, enum.Enum):
    """Pass status enum for database"""
    ACTIVE = "active"
    EXPIRED = "expired"
    EXHAUSTED = "exhausted"


# ============================================================================
# Database Models (Tables)
# ============================================================================

class TollDB(Base):
    """
    Toll plaza database model.

    Maps to MySQL table: tolls
    """
    __tablename__ = "tolls"

    # Primary key (technical ID)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Business fields
    toll_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships (we'll add these later)
    # booths = relationship("TollBoothDB", back_populates="toll")

    def __repr__(self):
        return f"<TollDB(toll_id='{self.toll_id}', name='{self.name}')>"


class VehicleDB(Base):
    """
    Vehicle database model.

    Maps to MySQL table: vehicles
    """
    __tablename__ = "vehicles"

    # Primary key (technical ID)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Business fields
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_type = Column(SQLEnum(VehicleTypeDB), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<VehicleDB(reg='{self.registration_number}', type='{self.vehicle_type}')>"


class TollPassDB(Base):
    """
    Toll pass database model.

    Maps to MySQL table: toll_passes

    This is the central entity linking vehicles and tolls.
    """
    __tablename__ = "toll_passes"

    # Primary key (technical ID)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Business identifier
    pass_id = Column(String(50), unique=True, nullable=False, index=True)

    # Foreign keys (links to other tables)
    vehicle_reg = Column(String(50), nullable=False, index=True)
    toll_id = Column(String(50), nullable=False, index=True)

    # Pass details
    pass_type = Column(SQLEnum(PassTypeDB), nullable=False)
    vehicle_type = Column(SQLEnum(VehicleTypeDB), nullable=False)
    price = Column(Integer, nullable=False)

    # Status tracking
    status = Column(SQLEnum(PassStatusDB), default=PassStatusDB.ACTIVE, nullable=False)
    uses_remaining = Column(Integer, nullable=False)

    # Timestamps (BUG FIX fields!)
    purchased_at = Column(DateTime, nullable=False)
    first_used_at = Column(DateTime, nullable=True)  # None until first use
    valid_until = Column(DateTime, nullable=True)    # Set on first use

    # Audit timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<TollPassDB(pass_id='{self.pass_id}', vehicle='{self.vehicle_reg}', status='{self.status}')>"


class TransactionDB(Base):
    """
    Transaction database model.

    Maps to MySQL table: transactions

    Records all activities (purchases and passages).
    """
    __tablename__ = "transactions"

    # Primary key (technical ID)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Business identifier
    transaction_id = Column(String(50), unique=True, nullable=False, index=True)

    # Transaction details
    booth_id = Column(String(50), nullable=False)
    toll_id = Column(String(50), nullable=False, index=True)
    vehicle_reg = Column(String(50), nullable=False, index=True)
    vehicle_type = Column(SQLEnum(VehicleTypeDB), nullable=False)

    # Transaction type and details
    transaction_type = Column(String(20), nullable=False)  # "PURCHASE" or "PASSAGE"
    pass_id = Column(String(50), nullable=True)  # Null for cash transactions
    amount = Column(Integer, nullable=False)

    # Timestamp
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<TransactionDB(txn_id='{self.transaction_id}', type='{self.transaction_type}', amount={self.amount})>"


class TollBoothDB(Base):
    """
    Toll booth database model.

    Maps to MySQL table: toll_booths

    Note: In domain model, booths are nested in Toll.
    In database, they're a separate table (normalized design).
    """
    __tablename__ = "toll_booths"

    # Primary key (technical ID)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Business identifier
    booth_id = Column(String(50), nullable=False, index=True)

    # Foreign key to toll
    toll_id = Column(String(50), nullable=False, index=True)

    # Booth details
    name = Column(String(200), nullable=False)

    # Statistics
    vehicles_processed = Column(Integer, default=0, nullable=False)
    total_charges_collected = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Composite unique constraint (booth_id + toll_id must be unique together)
    __table_args__ = (
        # This ensures B1 at T1 is different from B1 at T2
        # UniqueConstraint('booth_id', 'toll_id', name='uix_booth_toll'),
    )

    def __repr__(self):
        return f"<TollBoothDB(booth_id='{self.booth_id}', toll='{self.toll_id}')>"
