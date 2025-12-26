"""
Pass Controller - Handles toll pass-related API endpoints.

This controller manages pass purchase and information display operations.
"""

from typing import Dict, List
from models import PassType, VehicleType


class PassController:
    """
    Controller for pass-related operations.

    API Endpoints handled:
    - POST /api/pass/purchase  → purchase_pass()
    - GET  /api/pass/options   → get_pass_options()
    """

    def __init__(self, toll_system):
        """
        Initialize with toll management system dependency.

        Args:
            toll_system: Instance of TollManagementSystem
        """
        self.system = toll_system

    def purchase_pass(
        self,
        vehicle_reg: str,
        toll_id: str,
        booth_id: str,
        pass_type: str  # String from API, will convert to enum
    ) -> Dict:
        """
        Handle pass purchase request.

        This is the API endpoint handler for: POST /api/pass/purchase

        Flow:
        1. Validate inputs
        2. Convert pass_type string to enum
        3. Call business feature (system.purchase_pass)
        4. Format response

        Args:
            vehicle_reg: Vehicle registration number
            toll_id: Toll plaza ID
            booth_id: Booth ID where purchase happens
            pass_type: Pass type as string ("single", "return", "seven_day")

        Returns:
            Dict with status and response data:
            {
                "status": "success" or "error",
                "code": HTTP status code,
                "data": {...} or None,
                "message": str
            }

        Example:
            >>> controller = PassController(system)
            >>> result = controller.purchase_pass("MH-12-AB-1234", "T1", "B1", "return")
            >>> print(result["data"]["pass_id"])  # "PASS-0001"
        """
        # ============ STEP 1: INPUT VALIDATION ============

        if not vehicle_reg or not isinstance(vehicle_reg, str):
            return {
                "status": "error",
                "code": 400,
                "data": None,
                "message": "Invalid vehicle registration number"
            }

        if not toll_id or not isinstance(toll_id, str):
            return {
                "status": "error",
                "code": 400,
                "data": None,
                "message": "Invalid toll ID"
            }

        if not booth_id or not isinstance(booth_id, str):
            return {
                "status": "error",
                "code": 400,
                "data": None,
                "message": "Invalid booth ID"
            }

        # Convert string to PassType enum
        try:
            pass_type_enum = PassType(pass_type.lower())
        except (ValueError, AttributeError):
            return {
                "status": "error",
                "code": 400,
                "data": None,
                "message": f"Invalid pass type. Must be one of: single, return, seven_day"
            }

        # ============ STEP 2: CALL BUSINESS FEATURE ============

        try:
            toll_pass = self.system.purchase_pass(
                vehicle_reg, toll_id, booth_id, pass_type_enum
            )

            # ============ STEP 3: FORMAT RESPONSE ============

            return {
                "status": "success",
                "code": 201,  # Created
                "data": {
                    "pass_id": toll_pass.pass_id,
                    "vehicle_reg": toll_pass.vehicle_reg,
                    "toll_id": toll_pass.toll_id,
                    "pass_type": toll_pass.pass_type.value,
                    "price": toll_pass.price,
                    "purchased_at": toll_pass.purchased_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "uses_remaining": toll_pass.uses_remaining,
                    "status": toll_pass.status.value
                },
                "message": f"Pass {toll_pass.pass_id} purchased successfully"
            }

        except ValueError as e:
            # Business validation failed
            return {
                "status": "error",
                "code": 400,  # Bad Request (business rule violation)
                "data": None,
                "message": str(e)
            }

        except Exception as e:
            # Unexpected error
            return {
                "status": "error",
                "code": 500,
                "data": None,
                "message": f"Internal error: {str(e)}"
            }

    def get_pass_options(self, vehicle_type: str) -> Dict:
        """
        Get available pass options for a vehicle type.

        This is the API endpoint handler for: GET /api/pass/options?vehicle_type=two_wheeler

        Flow:
        1. Validate input
        2. Convert vehicle_type string to enum
        3. Call business feature (system.display_pass_options)
        4. Format response

        Args:
            vehicle_type: Vehicle type as string ("two_wheeler", "four_wheeler")

        Returns:
            Dict with status and pass options data

        Example:
            >>> controller = PassController(system)
            >>> result = controller.get_pass_options("two_wheeler")
            >>> print(len(result["data"]["options"]))  # 3
        """
        # ============ STEP 1: INPUT VALIDATION ============

        # Convert string to VehicleType enum
        try:
            vehicle_type_enum = VehicleType(vehicle_type.lower())
        except (ValueError, AttributeError):
            return {
                "status": "error",
                "code": 400,
                "data": None,
                "message": "Invalid vehicle type. Must be: two_wheeler or four_wheeler"
            }

        # ============ STEP 2: CALL BUSINESS FEATURE ============

        try:
            options = self.system.display_pass_options(vehicle_type_enum)

            # ============ STEP 3: FORMAT RESPONSE ============

            # Convert PassType enums to strings for JSON serialization
            formatted_options = []
            for option in options:
                formatted_options.append({
                    "pass_type": option["pass_type"].value,
                    "price": option["price"],
                    "duration": option["duration"],
                    "uses": option["uses"],
                    "description": option["description"]
                })

            return {
                "status": "success",
                "code": 200,
                "data": {
                    "vehicle_type": vehicle_type,
                    "options": formatted_options
                },
                "message": f"Retrieved {len(formatted_options)} pass options"
            }

        except Exception as e:
            return {
                "status": "error",
                "code": 500,
                "data": None,
                "message": f"Internal error: {str(e)}"
            }
