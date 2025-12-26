"""
Transaction Repository - MySQL Version

Handles storage and retrieval of Transaction entities using MySQL database.
Transactions are append-only (audit log) - no updates or deletes.

KEY CHANGES from in-memory version:
1. Uses database session instead of list storage
2. Converts domain models ↔ database models
3. Uses SQL queries instead of list operations
4. Maintains chronological order with ORDER BY timestamp
"""

from typing import List, Optional
from sqlalchemy.orm import Session

# Domain models (business logic)
from models import Transaction

# Database models (SQLAlchemy)
from database.db_models import TransactionDB

# Converters (domain ↔ database)
from database.converters import transaction_to_db, db_to_transaction


class TransactionRepository:
    """
    Repository for managing Transaction entities with MySQL storage.

    Transactions are stored as an append-only audit log.
    NO UPDATES OR DELETES ALLOWED - only inserts and queries.
    """

    def __init__(self, db_session: Session):
        """
        Initialize repository with database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    # ========================================================================
    # Basic CRUD Operations (Append-Only)
    # ========================================================================

    def add_transaction(self, transaction: Transaction) -> None:
        """
        Add a transaction to MySQL audit log.

        Args:
            transaction: Domain model Transaction to store

        Process:
            1. Convert domain model → database model
            2. Add to database session
            3. Commit transaction

        SQL Generated:
            INSERT INTO transactions
            (transaction_id, booth_id, toll_id, vehicle_reg, vehicle_type,
             transaction_type, pass_id, amount, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        Note: This is APPEND-ONLY. No updates or deletes for audit integrity.
        """
        # Convert domain → database
        db_transaction = transaction_to_db(transaction)

        # Save to MySQL (audit log)
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)  # Get any DB-generated values

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get a transaction by ID from MySQL.

        Args:
            transaction_id: Transaction identifier

        Returns:
            Domain model Transaction if found, None otherwise

        SQL Generated:
            SELECT * FROM transactions WHERE transaction_id = ? LIMIT 1
        """
        # Query MySQL
        db_transaction = self.db.query(TransactionDB).filter_by(
            transaction_id=transaction_id
        ).first()

        # Not found?
        if not db_transaction:
            return None

        # Convert database → domain
        return db_to_transaction(db_transaction)

    def get_all_transactions(self) -> List[Transaction]:
        """
        Get all transactions from MySQL in chronological order.

        Returns:
            List of domain model Transaction objects (ordered by timestamp)

        SQL Generated:
            SELECT * FROM transactions ORDER BY timestamp ASC
        """
        # Query MySQL for all transactions (ordered chronologically)
        db_transactions = self.db.query(TransactionDB).order_by(
            TransactionDB.timestamp.asc()
        ).all()

        # Convert each database model → domain model
        return [db_to_transaction(db_txn) for db_txn in db_transactions]

    # ========================================================================
    # Custom Query Methods (Business Logic Specific)
    # ========================================================================

    def find_by_vehicle(self, vehicle_reg: str) -> List[Transaction]:
        """
        Find all transactions for a specific vehicle.

        SQL Generated:
            SELECT * FROM transactions
            WHERE vehicle_reg = ?
            ORDER BY timestamp ASC

        Args:
            vehicle_reg: Vehicle registration number

        Returns:
            List of domain model Transaction objects
        """
        # Query MySQL with filter
        db_transactions = self.db.query(TransactionDB).filter_by(
            vehicle_reg=vehicle_reg
        ).order_by(TransactionDB.timestamp.asc()).all()

        # Convert each database → domain
        return [db_to_transaction(db_txn) for db_txn in db_transactions]

    def find_by_toll(self, toll_id: str) -> List[Transaction]:
        """
        Find all transactions at a specific toll.

        SQL Generated:
            SELECT * FROM transactions
            WHERE toll_id = ?
            ORDER BY timestamp ASC

        Args:
            toll_id: Toll identifier

        Returns:
            List of domain model Transaction objects
        """
        # Query MySQL with filter
        db_transactions = self.db.query(TransactionDB).filter_by(
            toll_id=toll_id
        ).order_by(TransactionDB.timestamp.asc()).all()

        # Convert each database → domain
        return [db_to_transaction(db_txn) for db_txn in db_transactions]

    def find_by_booth(self, booth_id: str, toll_id: str) -> List[Transaction]:
        """
        Find all transactions at a specific booth.

        SQL Generated:
            SELECT * FROM transactions
            WHERE booth_id = ? AND toll_id = ?
            ORDER BY timestamp ASC

        Args:
            booth_id: Booth identifier
            toll_id: Toll identifier

        Returns:
            List of domain model Transaction objects
        """
        # Query MySQL with multiple filters
        db_transactions = self.db.query(TransactionDB).filter_by(
            booth_id=booth_id,
            toll_id=toll_id
        ).order_by(TransactionDB.timestamp.asc()).all()

        # Convert each database → domain
        return [db_to_transaction(db_txn) for db_txn in db_transactions]

    def find_by_type(self, transaction_type: str) -> List[Transaction]:
        """
        Find all transactions of a specific type.

        SQL Generated:
            SELECT * FROM transactions
            WHERE transaction_type = ?
            ORDER BY timestamp ASC

        Args:
            transaction_type: "PASSAGE" or "PURCHASE"

        Returns:
            List of domain model Transaction objects
        """
        # Query MySQL with filter
        db_transactions = self.db.query(TransactionDB).filter_by(
            transaction_type=transaction_type
        ).order_by(TransactionDB.timestamp.asc()).all()

        # Convert each database → domain
        return [db_to_transaction(db_txn) for db_txn in db_transactions]

    def count(self) -> int:
        """
        Count total number of transactions in MySQL.

        Returns:
            Total count of transactions

        SQL Generated:
            SELECT COUNT(*) FROM transactions
        """
        return self.db.query(TransactionDB).count()

    def count_by_type(self, transaction_type: str) -> int:
        """
        Count transactions of a specific type.

        Args:
            transaction_type: "PASSAGE" or "PURCHASE"

        Returns:
            Count of transactions of that type

        SQL Generated:
            SELECT COUNT(*) FROM transactions WHERE transaction_type = ?
        """
        return self.db.query(TransactionDB).filter_by(
            transaction_type=transaction_type
        ).count()
