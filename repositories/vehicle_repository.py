"""
Vehicle Repository - Handles storage and retrieval of Vehicle entities.
"""

from typing import Optional, List
from .base_repository import BaseRepository
from models import Vehicle


class VehicleRepository(BaseRepository[Vehicle]):
    """Repository for managing Vehicle entities"""

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """
        Add a vehicle to storage.

        Args:
            vehicle: Vehicle object to store
        """
        self.add(vehicle.registration_number, vehicle)

    def get_vehicle(self, registration_number: str) -> Optional[Vehicle]:
        """
        Get a vehicle by registration number.

        Args:
            registration_number: Vehicle registration number

        Returns:
            Vehicle object if found, None otherwise
        """
        return self.get_by_id(registration_number)

    def get_all_vehicles(self) -> List[Vehicle]:
        """
        Get all vehicles.

        Returns:
            List of all Vehicle objects
        """
        return self.get_all()
