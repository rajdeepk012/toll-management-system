"""
Pass Repository - MySQL Version

Handles storage and retrieval of TollPass entities using MySQL database.

KEY CHANGES from in-memory version:
1. Uses database session instead of dict storage
2. Converts domain models ↔ database models
3. Uses SQL queries instead of dict operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session

# Domain models (business logic)
from models import TollPass, PassStatus

# Database models (SQLAlchemy)
from database.db_models import TollPassDB, PassStatusDB

# Converters (domain ↔ database)
from database.converters import toll_pass_to_db, db_to_toll_pass, pass_status_to_db


class PassRepository:
    """
    Repository for managing TollPass entities with MySQL storage.

    This replaces the in-memory BaseRepository pattern.
    """

    def __init__(self, db_session: Session):
        """
        Initialize repository with database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    # ========================================================================
    # Basic CRUD Operations
    # ========================================================================

    def add_pass(self, toll_pass: TollPass) -> None:
        """
        Add a toll pass to MySQL database.

        Args:
            toll_pass: Domain model TollPass to store

        Process:
            1. Convert domain model → database model
            2. Add to database session
            3. Commit transaction
        """
        # Convert domain → database
        db_pass = toll_pass_to_db(toll_pass)

        # Save to MySQL
        self.db.add(db_pass)
        self.db.commit()
        self.db.refresh(db_pass)  # Get any DB-generated values

    def get_pass(self, pass_id: str) -> Optional[TollPass]:
        """
        Get a pass by ID from MySQL.

        Args:
            pass_id: Pass identifier

        Returns:
            Domain model TollPass if found, None otherwise

        Process:
            1. Query MySQL for database model
            2. Convert database model → domain model
            3. Return domain model
        """
        # Query MySQL
        db_pass = self.db.query(TollPassDB).filter_by(pass_id=pass_id).first()

        # Not found?
        if not db_pass:
            return None

        # Convert database → domain
        return db_to_toll_pass(db_pass)

    def get_all_passes(self) -> List[TollPass]:
        """
        Get all passes from MySQL.

        Returns:
            List of domain model TollPass objects
        """
        # Query MySQL for all passes
        db_passes = self.db.query(TollPassDB).all()

        # Convert each database model → domain model
        return [db_to_toll_pass(db_pass) for db_pass in db_passes]

    def exists(self, pass_id: str) -> bool:
        """
        Check if a pass exists in MySQL.

        Args:
            pass_id: Pass identifier

        Returns:
            True if pass exists, False otherwise
        """
        # Use COUNT query (faster than fetching the whole object)
        count = self.db.query(TollPassDB).filter_by(pass_id=pass_id).count()
        return count > 0

    def update_pass(self, toll_pass: TollPass) -> None:
        """
        Update an existing pass in MySQL.

        Args:
            toll_pass: Domain model TollPass with updated values

        Process:
            1. Find existing database record
            2. Update its fields
            3. Commit changes
        """
        # Find existing record
        db_pass = self.db.query(TollPassDB).filter_by(pass_id=toll_pass.pass_id).first()

        if not db_pass:
            raise ValueError(f"Pass {toll_pass.pass_id} not found for update")

        # Update fields (convert enums to DB enums)
        db_pass.vehicle_reg = toll_pass.vehicle_reg
        db_pass.toll_id = toll_pass.toll_id
        db_pass.status = pass_status_to_db(toll_pass.status)
        db_pass.uses_remaining = toll_pass.uses_remaining
        db_pass.first_used_at = toll_pass.first_used_at  # BUG FIX field!
        db_pass.valid_until = toll_pass.valid_until      # BUG FIX field!

        # Commit changes
        self.db.commit()
        self.db.refresh(db_pass)

    # ========================================================================
    # Custom Query Methods (Business Logic Specific)
    # ========================================================================

    def find_active_pass(self, vehicle_reg: str, toll_id: str) -> Optional[TollPass]:
        """
        Find active pass for a vehicle at a specific toll.

        This is a CUSTOM QUERY specific to pass business logic.
        Used by system.py to check if vehicle has valid pass.

        SQL Generated:
            SELECT * FROM toll_passes
            WHERE vehicle_reg = ? AND toll_id = ? AND status = 'ACTIVE'
            LIMIT 1

        Args:
            vehicle_reg: Vehicle registration number
            toll_id: Toll identifier

        Returns:
            Active domain model TollPass if found, None otherwise
        """
        # Query MySQL with multiple conditions
        db_pass = self.db.query(TollPassDB).filter_by(
            vehicle_reg=vehicle_reg,
            toll_id=toll_id,
            status=PassStatusDB.ACTIVE
        ).first()

        # Not found?
        if not db_pass:
            return None

        # Convert database → domain
        return db_to_toll_pass(db_pass)

    def find_passes_by_vehicle(self, vehicle_reg: str) -> List[TollPass]:
        """
        Find all passes for a specific vehicle.

        SQL Generated:
            SELECT * FROM toll_passes WHERE vehicle_reg = ?

        Args:
            vehicle_reg: Vehicle registration number

        Returns:
            List of domain model TollPass objects
        """
        # Query MySQL
        db_passes = self.db.query(TollPassDB).filter_by(
            vehicle_reg=vehicle_reg
        ).all()

        # Convert each database → domain
        return [db_to_toll_pass(db_pass) for db_pass in db_passes]

    def find_passes_by_toll(self, toll_id: str) -> List[TollPass]:
        """
        Find all passes for a specific toll.

        SQL Generated:
            SELECT * FROM toll_passes WHERE toll_id = ?

        Args:
            toll_id: Toll identifier

        Returns:
            List of domain model TollPass objects
        """
        # Query MySQL
        db_passes = self.db.query(TollPassDB).filter_by(
            toll_id=toll_id
        ).all()

        # Convert each database → domain
        return [db_to_toll_pass(db_pass) for db_pass in db_passes]

    def count(self) -> int:
        """
        Count total number of passes in MySQL.

        Returns:
            Total count of passes
        """
        return self.db.query(TollPassDB).count()
