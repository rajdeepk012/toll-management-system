"""
Toll Repository - Handles storage and retrieval of Toll entities.
"""

from typing import Optional, List
from .base_repository import BaseRepository
from models import Toll


class TollRepository(BaseRepository[Toll]):
    """Repository for managing Toll entities"""

    def add_toll(self, toll: Toll) -> None:
        """
        Add a toll plaza to storage.

        Args:
            toll: Toll object to store
        """
        self.add(toll.toll_id, toll)

    def get_toll(self, toll_id: str) -> Optional[Toll]:
        """
        Get a toll by ID.

        Args:
            toll_id: Toll identifier

        Returns:
            Toll object if found, None otherwise
        """
        return self.get_by_id(toll_id)

    def get_all_tolls(self) -> List[Toll]:
        """
        Get all tolls.

        Returns:
            List of all Toll objects
        """
        return self.get_all()
