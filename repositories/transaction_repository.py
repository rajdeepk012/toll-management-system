"""
Transaction Repository - Handles storage and retrieval of Transaction entities.
Transactions are append-only (audit log).
"""

from typing import List
from .base_repository import BaseRepository
from models import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    """
    Repository for managing Transaction entities.
    Transactions are stored as an append-only log (no updates/deletes).
    """

    def __init__(self):
        """Initialize with list storage (append-only log)"""
        super().__init__()
        self._transactions: List[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        """
        Add a transaction to the audit log.

        Args:
            transaction: Transaction object to store
        """
        # Store in both dict (for ID lookup) and list (for ordering)
        self.add(transaction.transaction_id, transaction)
        self._transactions.append(transaction)

    def get_transaction(self, transaction_id: str) -> Transaction:
        """
        Get a transaction by ID.

        Args:
            transaction_id: Transaction identifier

        Returns:
            Transaction object if found, None otherwise
        """
        return self.get_by_id(transaction_id)

    def get_all_transactions(self) -> List[Transaction]:
        """
        Get all transactions in order.

        Returns:
            List of all Transaction objects (in insertion order)
        """
        return self._transactions.copy()

    def find_by_vehicle(self, vehicle_reg: str) -> List[Transaction]:
        """
        Find all transactions for a specific vehicle.

        Args:
            vehicle_reg: Vehicle registration number

        Returns:
            List of Transaction objects for the vehicle
        """
        return [
            txn for txn in self._transactions
            if txn.vehicle_reg == vehicle_reg
        ]

    def find_by_toll(self, toll_id: str) -> List[Transaction]:
        """
        Find all transactions at a specific toll.

        Args:
            toll_id: Toll identifier

        Returns:
            List of Transaction objects for the toll
        """
        return [
            txn for txn in self._transactions
            if txn.toll_id == toll_id
        ]

    def find_by_booth(self, booth_id: str, toll_id: str) -> List[Transaction]:
        """
        Find all transactions at a specific booth.

        Args:
            booth_id: Booth identifier
            toll_id: Toll identifier

        Returns:
            List of Transaction objects for the booth
        """
        return [
            txn for txn in self._transactions
            if txn.booth_id == booth_id and txn.toll_id == toll_id
        ]

    def find_by_type(self, transaction_type: str) -> List[Transaction]:
        """
        Find all transactions of a specific type.

        Args:
            transaction_type: "PASSAGE" or "PURCHASE"

        Returns:
            List of Transaction objects of that type
        """
        return [
            txn for txn in self._transactions
            if txn.transaction_type == transaction_type
        ]
