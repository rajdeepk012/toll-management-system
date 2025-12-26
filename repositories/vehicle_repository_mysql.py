"""
Vehicle Repository - MySQL Version

Handles storage and retrieval of Vehicle entities using MySQL database.

KEY CHANGES from in-memory version:
1. Uses database session instead of dict storage
2. Converts domain models ↔ database models
3. Uses SQL queries instead of dict operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session

# Domain models (business logic)
from models import Vehicle

# Database models (SQLAlchemy)
from database.db_models import VehicleDB

# Converters (domain ↔ database)
from database.converters import vehicle_to_db, db_to_vehicle


class VehicleRepository:
    """
    Repository for managing Vehicle entities with MySQL storage.

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

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """
        Add a vehicle to MySQL database.

        Args:
            vehicle: Domain model Vehicle to store

        Process:
            1. Convert domain model → database model
            2. Add to database session
            3. Commit transaction

        SQL Generated:
            INSERT INTO vehicles (registration_number, vehicle_type)
            VALUES (?, ?)
        """
        # Convert domain → database
        db_vehicle = vehicle_to_db(vehicle)

        # Save to MySQL
        self.db.add(db_vehicle)
        self.db.commit()
        self.db.refresh(db_vehicle)  # Get any DB-generated values

    def get_vehicle(self, registration_number: str) -> Optional[Vehicle]:
        """
        Get a vehicle by registration number from MySQL.

        Args:
            registration_number: Vehicle registration number

        Returns:
            Domain model Vehicle if found, None otherwise

        Process:
            1. Query MySQL for database model
            2. Convert database model → domain model
            3. Return domain model

        SQL Generated:
            SELECT * FROM vehicles WHERE registration_number = ? LIMIT 1
        """
        # Query MySQL
        db_vehicle = self.db.query(VehicleDB).filter_by(
            registration_number=registration_number
        ).first()

        # Not found?
        if not db_vehicle:
            return None

        # Convert database → domain
        return db_to_vehicle(db_vehicle)

    def get_all_vehicles(self) -> List[Vehicle]:
        """
        Get all vehicles from MySQL.

        Returns:
            List of domain model Vehicle objects

        SQL Generated:
            SELECT * FROM vehicles
        """
        # Query MySQL for all vehicles
        db_vehicles = self.db.query(VehicleDB).all()

        # Convert each database model → domain model
        return [db_to_vehicle(db_vehicle) for db_vehicle in db_vehicles]

    def exists(self, registration_number: str) -> bool:
        """
        Check if a vehicle exists in MySQL.

        Args:
            registration_number: Vehicle registration number

        Returns:
            True if vehicle exists, False otherwise

        SQL Generated:
            SELECT COUNT(*) FROM vehicles WHERE registration_number = ?
        """
        # Use COUNT query (faster than fetching the whole object)
        count = self.db.query(VehicleDB).filter_by(
            registration_number=registration_number
        ).count()
        return count > 0

    def count(self) -> int:
        """
        Count total number of vehicles in MySQL.

        Returns:
            Total count of vehicles

        SQL Generated:
            SELECT COUNT(*) FROM vehicles
        """
        return self.db.query(VehicleDB).count()
