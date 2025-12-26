"""
Vehicle Controller - Handles vehicle-related API endpoints.

This controller manages operations related to vehicle passage through toll booths.
In a real application, this would be a FastAPI/Flask route handler.
"""

from typing import Dict


class VehicleController:
    """
    Controller for vehicle-related operations.

    This layer sits between external clients (HTTP, CLI) and the business layer.

    Responsibilities:
    - Input validation (basic checks)
    - Calling business features
    - Response formatting
    """

    def __init__(self, toll_system):
        """
        Initialize with toll management system dependency.

        Args:
            toll_system: Instance of TollManagementSystem
        """
        self.system = toll_system

    def process_vehicle_passage(
        self,
        vehicle_reg: str,
        toll_id: str,
        booth_id: str
    ) -> Dict:
        """
        Handle vehicle passage through a toll booth.

        This is the API endpoint handler for: POST /api/vehicle/process

        Flow:
        1. Validate inputs (basic checks)
        2. Call business feature (system.process_vehicle)
        3. Format response

        Args:
            vehicle_reg: Vehicle registration number
            toll_id: Toll plaza ID
            booth_id: Booth ID

        Returns:
            Dict with status code and response data:
            {
                "status": "success" or "error",
                "code": HTTP status code (200, 400, etc.),
                "data": {...} or None,
                "message": str or None
            }

        Example:
            >>> controller = VehicleController(system)
            >>> result = controller.process_vehicle_passage("MH-12-AB-1234", "T1", "B1")
            >>> print(result["status"])  # "success"
        """
        # ============ STEP 1: INPUT VALIDATION ============

        # Basic validation (type checks, empty strings, etc.)
        if not vehicle_reg or not isinstance(vehicle_reg, str):
            return {
                "status": "error",
                "code": 400,  # Bad Request
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

        # ============ STEP 2: CALL BUSINESS FEATURE ============

        try:
            # Call the business feature (system.process_vehicle)
            result = self.system.process_vehicle(vehicle_reg, toll_id, booth_id)

            # ============ STEP 3: FORMAT RESPONSE ============

            if result["allowed"]:
                # Success - vehicle was allowed to pass
                return {
                    "status": "success",
                    "code": 200,  # OK
                    "data": {
                        "allowed": True,
                        "message": result["message"],
                        "pass_info": result.get("pass_info")
                    },
                    "message": "Vehicle passage processed successfully"
                }
            else:
                # Denied - vehicle was not allowed (no pass, expired, etc.)
                return {
                    "status": "success",  # Request was successful, but passage denied
                    "code": 200,  # OK (denial is a valid business outcome)
                    "data": {
                        "allowed": False,
                        "message": result["message"],
                        "pass_info": result.get("pass_info"),
                        "pass_options": result.get("pass_options")
                    },
                    "message": "Vehicle passage denied"
                }

        except ValueError as e:
            # Business validation failed (vehicle not found, toll not found, etc.)
            return {
                "status": "error",
                "code": 404,  # Not Found
                "data": None,
                "message": str(e)
            }

        except Exception as e:
            # Unexpected error
            return {
                "status": "error",
                "code": 500,  # Internal Server Error
                "data": None,
                "message": f"Internal error: {str(e)}"
            }
