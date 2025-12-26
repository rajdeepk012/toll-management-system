"""
Toll Repository - MySQL Version

Handles storage and retrieval of Toll entities using MySQL database.

COMPLEXITY: Toll has a booths dictionary (composition relationship)
- Tolls stored in 'tolls' table
- TollBooths stored in 'toll_booths' table (separate table)
- When loading Toll, must reconstruct booths dictionary from toll_booths

KEY CHANGES from in-memory version:
1. Uses database session instead of dict storage
2. Manages TWO tables: tolls + toll_booths
3. Reconstructs booths dictionary when loading Toll
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session

# Domain models (business logic)
from models import Toll, TollBooth

# Database models (SQLAlchemy)
from database.db_models import TollDB, TollBoothDB

# Converters (domain ↔ database)
from database.converters import (
    toll_to_db, db_to_toll,
    toll_booth_to_db, db_to_toll_booth
)


class TollRepository:
    """
    Repository for managing Toll entities with MySQL storage.

    COMPLEXITY: Manages composition relationship (Toll HAS-MANY TollBooths)
    - Toll stored in 'tolls' table
    - TollBooths stored in 'toll_booths' table
    - Must coordinate saving/loading across both tables
    """

    def __init__(self, db_session: Session):
        """
        Initialize repository with database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    # ========================================================================
    # Basic CRUD Operations (with Booth Management)
    # ========================================================================

    def add_toll(self, toll: Toll) -> None:
        """
        Add a toll plaza to MySQL (including its booths).

        Args:
            toll: Domain model Toll to store

        Process:
            1. Convert Toll domain → database model (without booths)
            2. Save Toll to 'tolls' table
            3. For each booth in toll.booths:
               - Convert booth domain → database model
               - Save to 'toll_booths' table
            4. Commit transaction

        SQL Generated:
            INSERT INTO tolls (toll_id, name, location) VALUES (?, ?, ?)
            INSERT INTO toll_booths (booth_id, toll_id, name, ...) VALUES (?, ?, ?, ...)
            (one INSERT per booth)
        """
        # Step 1: Convert and save Toll (without booths)
        db_toll = toll_to_db(toll)
        self.db.add(db_toll)

        # Step 2: Convert and save each TollBooth
        for booth in toll.booths.values():
            db_booth = toll_booth_to_db(booth)
            self.db.add(db_booth)

        # Step 3: Commit everything together (transaction)
        self.db.commit()
        self.db.refresh(db_toll)

    def get_toll(self, toll_id: str) -> Optional[Toll]:
        """
        Get a toll by ID from MySQL (with its booths).

        Args:
            toll_id: Toll identifier

        Returns:
            Domain model Toll with booths dictionary if found, None otherwise

        Process:
            1. Query 'tolls' table for the toll
            2. Query 'toll_booths' table for all booths with this toll_id
            3. Convert booths to domain models and build dictionary
            4. Convert toll to domain model with booths dictionary
            5. Return domain model

        SQL Generated:
            SELECT * FROM tolls WHERE toll_id = ? LIMIT 1
            SELECT * FROM toll_booths WHERE toll_id = ?
        """
        # Step 1: Query toll from 'tolls' table
        db_toll = self.db.query(TollDB).filter_by(toll_id=toll_id).first()

        # Not found?
        if not db_toll:
            return None

        # Step 2: Query booths from 'toll_booths' table
        db_booths = self.db.query(TollBoothDB).filter_by(toll_id=toll_id).all()

        # Step 3: Convert booths to domain models and build dictionary
        booths_dict = {
            db_booth.booth_id: db_to_toll_booth(db_booth)
            for db_booth in db_booths
        }

        # Step 4: Convert toll to domain model with booths
        return db_to_toll(db_toll, booths_dict=booths_dict)

    def get_all_tolls(self) -> List[Toll]:
        """
        Get all tolls from MySQL (each with its booths).

        Returns:
            List of domain model Toll objects with booths

        Process:
            1. Query all tolls from 'tolls' table
            2. For each toll:
               - Query its booths from 'toll_booths' table
               - Build booths dictionary
               - Convert to domain model
            3. Return list of domain models

        SQL Generated:
            SELECT * FROM tolls
            SELECT * FROM toll_booths WHERE toll_id = ? (one per toll)
        """
        # Step 1: Query all tolls
        db_tolls = self.db.query(TollDB).all()

        # Step 2: For each toll, load its booths and convert
        tolls = []
        for db_toll in db_tolls:
            # Query booths for this toll
            db_booths = self.db.query(TollBoothDB).filter_by(
                toll_id=db_toll.toll_id
            ).all()

            # Build booths dictionary
            booths_dict = {
                db_booth.booth_id: db_to_toll_booth(db_booth)
                for db_booth in db_booths
            }

            # Convert to domain model with booths
            toll = db_to_toll(db_toll, booths_dict=booths_dict)
            tolls.append(toll)

        return tolls

    def exists(self, toll_id: str) -> bool:
        """
        Check if a toll exists in MySQL.

        Args:
            toll_id: Toll identifier

        Returns:
            True if toll exists, False otherwise

        SQL Generated:
            SELECT COUNT(*) FROM tolls WHERE toll_id = ?
        """
        count = self.db.query(TollDB).filter_by(toll_id=toll_id).count()
        return count > 0

    # ========================================================================
    # Booth Management Methods
    # ========================================================================

    def add_booth(self, booth: TollBooth) -> None:
        """
        Add a booth to an existing toll.

        Args:
            booth: Domain model TollBooth to add

        Process:
            1. Convert booth domain → database model
            2. Save to 'toll_booths' table
            3. Commit

        SQL Generated:
            INSERT INTO toll_booths (booth_id, toll_id, name, ...) VALUES (?, ?, ?, ...)

        Note: This allows adding booths after toll creation
        """
        db_booth = toll_booth_to_db(booth)
        self.db.add(db_booth)
        self.db.commit()
        self.db.refresh(db_booth)

    def get_booth(self, booth_id: str, toll_id: str) -> Optional[TollBooth]:
        """
        Get a specific booth by ID.

        Args:
            booth_id: Booth identifier
            toll_id: Toll identifier (booths are unique within a toll)

        Returns:
            Domain model TollBooth if found, None otherwise

        SQL Generated:
            SELECT * FROM toll_booths WHERE booth_id = ? AND toll_id = ? LIMIT 1
        """
        db_booth = self.db.query(TollBoothDB).filter_by(
            booth_id=booth_id,
            toll_id=toll_id
        ).first()

        if not db_booth:
            return None

        return db_to_toll_booth(db_booth)

    def update_booth(self, booth: TollBooth) -> None:
        """
        Update booth statistics (for leaderboard).

        Args:
            booth: Domain model TollBooth with updated statistics

        Process:
            1. Find existing booth in database
            2. Update its fields
            3. Commit changes

        SQL Generated:
            UPDATE toll_booths
            SET vehicles_processed = ?, total_charges_collected = ?
            WHERE booth_id = ? AND toll_id = ?
        """
        # Find existing booth
        db_booth = self.db.query(TollBoothDB).filter_by(
            booth_id=booth.booth_id,
            toll_id=booth.toll_id
        ).first()

        if not db_booth:
            raise ValueError(f"Booth {booth.booth_id} not found for update")

        # Update fields
        db_booth.name = booth.name
        db_booth.vehicles_processed = booth.vehicles_processed
        db_booth.total_charges_collected = booth.total_charges_collected

        # Commit changes
        self.db.commit()
        self.db.refresh(db_booth)

    def get_all_booths_for_toll(self, toll_id: str) -> List[TollBooth]:
        """
        Get all booths for a specific toll.

        Args:
            toll_id: Toll identifier

        Returns:
            List of domain model TollBooth objects

        SQL Generated:
            SELECT * FROM toll_booths WHERE toll_id = ?
        """
        db_booths = self.db.query(TollBoothDB).filter_by(toll_id=toll_id).all()
        return [db_to_toll_booth(db_booth) for db_booth in db_booths]

    def count(self) -> int:
        """
        Count total number of tolls in MySQL.

        Returns:
            Total count of tolls

        SQL Generated:
            SELECT COUNT(*) FROM tolls
        """
        return self.db.query(TollDB).count()
