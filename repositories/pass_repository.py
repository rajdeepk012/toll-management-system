"""
Pass Repository - Handles storage and retrieval of TollPass entities.
Includes custom queries for finding active passes.
"""

from typing import Optional, List
from .base_repository import BaseRepository
from models import TollPass, PassStatus


class PassRepository(BaseRepository[TollPass]):
    """Repository for managing TollPass entities"""

    def add_pass(self, toll_pass: TollPass) -> None:
        """
        Add a toll pass to storage.

        Args:
            toll_pass: TollPass object to store
        """
        self.add(toll_pass.pass_id, toll_pass)

    def get_pass(self, pass_id: str) -> Optional[TollPass]:
        """
        Get a pass by ID.

        Args:
            pass_id: Pass identifier

        Returns:
            TollPass object if found, None otherwise
        """
        return self.get_by_id(pass_id)

    def get_all_passes(self) -> List[TollPass]:
        """
        Get all passes.

        Returns:
            List of all TollPass objects
        """
        return self.get_all()

    def find_active_pass(self, vehicle_reg: str, toll_id: str) -> Optional[TollPass]:
        """
        Find active pass for a vehicle at a specific toll.
        This is a CUSTOM QUERY specific to pass business logic.

        Args:
            vehicle_reg: Vehicle registration number
            toll_id: Toll identifier

        Returns:
            Active TollPass if found, None otherwise
        """
        for toll_pass in self._storage.values():
            if (toll_pass.vehicle_reg == vehicle_reg and
                toll_pass.toll_id == toll_id and
                toll_pass.status == PassStatus.ACTIVE):
                return toll_pass
        return None

    def find_passes_by_vehicle(self, vehicle_reg: str) -> List[TollPass]:
        """
        Find all passes for a specific vehicle.

        Args:
            vehicle_reg: Vehicle registration number

        Returns:
            List of TollPass objects for the vehicle
        """
        return [
            toll_pass for toll_pass in self._storage.values()
            if toll_pass.vehicle_reg == vehicle_reg
        ]

    def find_passes_by_toll(self, toll_id: str) -> List[TollPass]:
        """
        Find all passes for a specific toll.

        Args:
            toll_id: Toll identifier

        Returns:
            List of TollPass objects for the toll
        """
        return [
            toll_pass for toll_pass in self._storage.values()
            if toll_pass.toll_id == toll_id
        ]
