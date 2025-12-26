"""
Leaderboard Controller - Handles leaderboard/statistics API endpoints.

This controller manages booth statistics and ranking operations.
"""

from typing import Dict


class LeaderboardController:
    """
    Controller for leaderboard and statistics operations.

    API Endpoints handled:
    - GET /api/leaderboard?metric=vehicles_processed  → get_leaderboard()
    """

    def __init__(self, toll_system):
        """
        Initialize with toll management system dependency.

        Args:
            toll_system: Instance of TollManagementSystem
        """
        self.system = toll_system

    def get_leaderboard(self, metric: str = "vehicles_processed") -> Dict:
        """
        Get booth leaderboard sorted by specified metric.

        This is the API endpoint handler for: GET /api/leaderboard?metric=vehicles_processed

        Flow:
        1. Validate metric parameter
        2. Call business feature (system.get_leaderboard)
        3. Format response

        Args:
            metric: Sorting metric ("vehicles_processed" or "total_charges_collected")

        Returns:
            Dict with status and leaderboard data:
            {
                "status": "success",
                "code": 200,
                "data": {
                    "metric": str,
                    "leaderboard": [...]
                },
                "message": str
            }

        Example:
            >>> controller = LeaderboardController(system)
            >>> result = controller.get_leaderboard("vehicles_processed")
            >>> print(result["data"]["leaderboard"][0]["rank"])  # 1
        """
        # ============ STEP 1: INPUT VALIDATION ============

        valid_metrics = ["vehicles_processed", "total_charges_collected"]

        if metric not in valid_metrics:
            return {
                "status": "error",
                "code": 400,
                "data": None,
                "message": f"Invalid metric. Must be one of: {', '.join(valid_metrics)}"
            }

        # ============ STEP 2: CALL BUSINESS FEATURE ============

        try:
            leaderboard = self.system.get_leaderboard(metric)

            # ============ STEP 3: FORMAT RESPONSE ============

            return {
                "status": "success",
                "code": 200,
                "data": {
                    "metric": metric,
                    "total_booths": len(leaderboard),
                    "leaderboard": leaderboard
                },
                "message": f"Retrieved leaderboard sorted by {metric}"
            }

        except ValueError as e:
            # Business validation error (though unlikely here)
            return {
                "status": "error",
                "code": 400,
                "data": None,
                "message": str(e)
            }

        except Exception as e:
            return {
                "status": "error",
                "code": 500,
                "data": None,
                "message": f"Internal error: {str(e)}"
            }
