"""
Base Repository - Common CRUD operations for all repositories.
Uses Generic types to work with any entity type.
"""

from typing import Dict, List, Optional, TypeVar, Generic

# Generic type variable - can be any entity type
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository with common CRUD operations.
    All specific repositories inherit from this.

    Type parameter T represents the entity type (Toll, Vehicle, etc.)
    """

    def __init__(self):
        """Initialize in-memory storage"""
        self._storage: Dict[str, T] = {}

    def add(self, key: str, entity: T) -> None:
        """
        Add an entity to storage.

        Args:
            key: Unique identifier (toll_id, vehicle_reg, pass_id, etc.)
            entity: The entity object to store
        """
        self._storage[key] = entity

    def get_by_id(self, key: str) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            key: The unique identifier

        Returns:
            The entity if found, None otherwise
        """
        return self._storage.get(key)

    def exists(self, key: str) -> bool:
        """
        Check if an entity exists.

        Args:
            key: The unique identifier

        Returns:
            True if entity exists, False otherwise
        """
        return key in self._storage

    def get_all(self) -> List[T]:
        """
        Get all entities.

        Returns:
            List of all entities in storage
        """
        return list(self._storage.values())

    def count(self) -> int:
        """
        Count total entities.

        Returns:
            Number of entities in storage
        """
        return len(self._storage)

    def remove(self, key: str) -> bool:
        """
        Remove an entity from storage.

        Args:
            key: The unique identifier

        Returns:
            True if entity was removed, False if not found
        """
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all entities from storage"""
        self._storage.clear()
